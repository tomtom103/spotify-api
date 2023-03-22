from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "fastapi-spotify"
    VERSION: str = "0.1.0"
    PROXY_ROOT_PATH: str = ""

    OPEN_API_URL: str = "/api/v1/openapi.json"
    CORS_ORIGIN_REGEX: str = r".*"  # TODO

    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8080

    DEBUG: bool = True

    ENV_STATE: str = "dev"
    LOGGER_FILE: str = "fastapi-spotify.log"
    JSON_LOGS_ENABLED: bool = False
    RICH_LOGS_ENABLED: bool = True

    # Spotify
    SPOTIFY_CLIENT_ID: str
    SPOTIFY_CLIENT_SECRET: str
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8080/api/authentication/callback"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()


CONFIG = get_settings()
