import logging
import logging.config
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FILE = "logs/app.log"


def setup_logging():
    os.makedirs("logs", exist_ok=True)

    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-7s | %(name)s | req=%(request_id)s user=%(user_id)s | %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            }
        },
        "filters": {"context": {"()": "app.core.log_context.ContextFilter"}},
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "filters": ["context"],
            },
            "file": {
                "class": "logging.handlers.TimedRotatingFileHandler",
                "filename": LOG_FILE,
                "when": "midnight",
                "backupCount": 14,
                "encoding": "utf-8",
                "formatter": "default",
                "filters": ["context"],
            },
        },
        "root": {
            "level": LOG_LEVEL,
            "handlers": ["console", "file"],
        },
        "loggers": {
            "uvicorn": {"level": LOG_LEVEL},
            "uvicorn.error": {"level": LOG_LEVEL},
            "uvicorn.access": {"level": "WARNING"},
        },
    }

    logging.config.dictConfig(logging_config)
