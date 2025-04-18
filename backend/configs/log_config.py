import sys
from pathlib import Path
from typing import Any, Dict

from pydantic import Field
from pydantic_settings import BaseSettings

# Create log directory
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Common constants
DETAILED_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "process=<cyan>{process.name}({process.id})</cyan> | "
    "thread=<cyan>{thread.name}({thread.id})</cyan> | "
    "<blue>{name}</blue>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "file=<blue>{file.path}</blue> | "
    "<level>{message}</level>"
    "{exception}\n"
)
# Console 
CONSOLE_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<blue>{name}</blue>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


class LogConfig(BaseSettings):
    """
    Logging-related configuration
    """
    # Basic logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")
    LOG_FORMAT: str = Field(default=DETAILED_LOG_FORMAT, description="Log format string")
    
    # File logging settings
    LOG_FILENAME: str = Field(
        default="funiq_logging.log",
        description="Fixed log filename"
    )
    LOG_ROTATION: str = Field(default="500 MB", description="Log rotation size")
    LOG_RETENTION: str = Field(default="7 days", description="Log retention period")
    LOG_COMPRESSION: str = Field(default="zip", description="Log compression format")

    # Third-party logging settings
    UVICORN_ACCESS_LOG_LEVEL: str = Field(default="INFO", description="Uvicorn access log level")

    @property
    def LOGGING_CONFIG(self) -> Dict[str, Any]:
        """
        Dynamic logging configuration
        """
        return {
            "handlers": [
                # Console handler
                {
                    "sink": sys.stdout,
                    "format": CONSOLE_LOG_FORMAT,
                    "level": self.LOG_LEVEL,
                    "colorize": True,
                    "backtrace": True,
                    "diagnose": True,
                    "enqueue": True,
                },
                # File handler
                {
                    "sink": str(LOG_DIR / self.LOG_FILENAME),
                    "format": self.LOG_FORMAT,
                    "level": self.LOG_LEVEL,
                    "rotation": self.LOG_ROTATION,
                    "retention": self.LOG_RETENTION,
                    "compression": self.LOG_COMPRESSION,
                    "encoding": "utf-8",
                    "enqueue": True,
                    "backtrace": True,
                    "diagnose": True,
                },
            ],
        }
