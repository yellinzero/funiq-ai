from enum import Enum


class StreamEvent(str, Enum):
    """Stream event types."""
    MESSAGE = "message"
    FINISH = "finish"
    ERROR = "error"
    CLOSE = "close"
    