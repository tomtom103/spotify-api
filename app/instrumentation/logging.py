import logging
import logging.config
from typing import Any, Dict

from pythonjsonlogger.jsonlogger import JsonFormatter

from app.settings import CONFIG

LOGGER_FORMAT = "%(asctime)s %(name)s - %(levelname)s:%(message)s"
JSON_LOGGER_FORMAT = "%(asctime)s %(name)s %(levelname)s %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


class APIJsonFormatter(JsonFormatter):
    def process_log_record(self, log_record: Dict[str, Any]) -> Any:
        # Any custom logic to modify JSON logs can go here.
        return super().process_log_record(log_record)


LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple_formatter": {
            "datefmt": LOG_DATE_FORMAT,
            "format": "%(message)s",
        }
    },
    "handlers": {
        "default_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple_formatter",
        }
    },
    "loggers": {
        # Root logger
        "": {
            "level": "DEBUG",
            "handlers": ["default_handler"],
        },
        "uvicorn.access": {
            "level": "WARNING",
            "handlers": ["default_handler"],
        },
    },
}

JSON_LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "class": "app.instrumentation.logging.APIJsonFormatter",
            "datefmt": LOG_DATE_FORMAT,
            "format": JSON_LOGGER_FORMAT,
        },
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "json",
            "stream": "ext://sys.stdout",
        },
        "file_handler": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "simple_formatter",
            "filename": CONFIG.LOGGER_FILE,
        },
    },
    "loggers": {
        # Root logger
        "": {
            "level": "DEBUG",
            "handlers": ["console_handler", "file_handler"],
        },
        "uvicorn.access": {
            "level": "WARNING",
            "handlers": ["console_handler", "file_handler"],
        },
    },
}


def init_logging() -> None:
    if CONFIG.JSON_LOGS_ENABLED:
        logging.config.dictConfig(JSON_LOGGING_CONFIG)
    elif CONFIG.RICH_LOGS_ENABLED:
        try:
            from rich.logging import RichHandler  # noqa

            LOGGING_CONFIG["handlers"]["default_handler"][
                "class"
            ] = "rich.logging.RichHandler"
            LOGGING_CONFIG["handlers"]["default_handler"]["rich_tracebacks"] = True
            logging.config.dictConfig(LOGGING_CONFIG)
        except ModuleNotFoundError:
            logging.config.dictConfig(LOGGING_CONFIG)
    else:
        logging.config.dictConfig(LOGGING_CONFIG)
