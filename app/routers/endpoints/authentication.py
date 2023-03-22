import logging
import base64
from typing import Final, Annotated, Optional, Dict, Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, status
from fastapi.requests import Request
from fastapi.responses import Response, RedirectResponse

from app import deps
from app.settings import CONFIG

logger = logging.getLogger(__name__)

router = APIRouter()

STATE_KEY: Final[str] = "spotify_auth_state"

RandomString = Annotated[str, Depends(deps.RandomStringGenerator(16))]

@router.get("/login")
def login(state: RandomString) -> RedirectResponse:
    scope = "user-read-private user-read-email"
    query_params = {
        "response_type": "code",
        "client_id": CONFIG.SPOTIFY_CLIENT_ID,
        "scope": scope,
        "redirect_uri": CONFIG.SPOTIFY_REDIRECT_URI,
        "state": state
    }
    response = RedirectResponse(
        "https://accounts.spotify.com/authorize?" + urlencode(query_params),
        status_code=status.HTTP_307_TEMPORARY_REDIRECT
    )
    response.set_cookie(STATE_KEY, state)
    return response

@router.get("/callback")
async def login_callback(
    request: Request,
    response: Response,
    code: Optional[str] = None,
    state: Optional[str] = None,
) -> RedirectResponse:
    stored_state = request.cookies.get(STATE_KEY)

    if state is None or state != stored_state:
        return RedirectResponse(
            url="/error?" + urlencode({"error": "state_mismatch"})
        )

    response.delete_cookie(STATE_KEY)

    data = {
        "code": code,
        "redirect_uri": CONFIG.SPOTIFY_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    auth_token = base64.b64encode((CONFIG.SPOTIFY_CLIENT_ID + ':' + CONFIG.SPOTIFY_CLIENT_SECRET).encode())
    headers = {
        "Authorization": f"Basic {auth_token.decode('utf-8')}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post("https://accounts.spotify.com/api/token", data=data, headers=headers)

        if resp.status_code != status.HTTP_200_OK:
            # Reject request, reason: invalid_token
            logger.warning(resp.json())
            return RedirectResponse(
                url="/error?" + urlencode({"error": "invalid_token"})
            )

        body: Dict[str, Any] = resp.json()

        logger.info(f"API Token body: {body}")

        access_token, refresh_token = body.get("access_token"), body.get("refresh_token")

        # Use tokens to access spotify web api
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        resp = await client.get("https://api.spotify.com/v1/me", headers=headers)

        logger.info(f"Request returned: {resp.json()}")

# TODO: Implement refresh token flow https://developer.spotify.com/documentation/general/guides/authorization/code-flow/
# Store the spotify refresh token inside the database: doesn't matter which token, always store the latest
# refresh tokens will work until user specifically removes your application from the authorized list
