import logging
from pathlib import Path
from typing import Any, Dict

from loguru import logger

from configs import funiq_ai_config

# Create logs directory if not exists
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


class InterceptHandler(logging.Handler):
    """
    Custom logging handler to redirect standard library logging to loguru
    """

    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def serialize_record(record: Dict[str, Any]) -> str:
    """
    Serialize log record to JSON format

    Args:
        record: Log record to serialize

    Returns:
        Serialized log record as dictionary
    """
    subset = {
        "timestamp": record["time"].strftime("%Y-%m-%d %H:%M:%S.%f"),
        "level": record["level"].name,
        "process_id": record["process"].id,
        "thread_id": record["thread"].id,
        "logger": record["name"],
        "module": record["file"].name,
        "function": record["function"],
        "line": record["line"],
        "message": record["message"],
    }

    # Add optional fields if present
    if "extra" in record:
        subset["extra"] = record["extra"]
    if "exception" in record:
        subset["exception"] = record["exception"]

    return subset


def setup_loguru() -> None:
    """
    Configure loguru logger with console and file handlers
    """
    # Get config from settings
    config = funiq_ai_config.LOGGING_CONFIG
    # Set log level based on DEBUG flag
    level = "DEBUG" if funiq_ai_config.DEBUG else "INFO"
    for handler in config["handlers"]:
        handler["level"] = level
    # Configure loguru
    logger.configure(**config)

    # Replace standard library handlers with loguru
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Configure third-party loggers
    for _log in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        _logger = logging.getLogger(_log)
        _logger.handlers = [InterceptHandler()]
        _logger.propagate = False
    
    # Set specific levels for some loggers
    logging.getLogger("uvicorn.access").setLevel(getattr(logging, funiq_ai_config.UVICORN_ACCESS_LOG_LEVEL))

    logger.info("Loguru logging system initialized")
