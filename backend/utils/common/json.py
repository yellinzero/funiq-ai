from decimal import Decimal
from typing import Any

import orjson


def default(obj: Any) -> Any:
    """Default JSON serializer"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def json_dumps(*args, **kwargs) -> str:
    # Special handling for bytes
    if len(args) > 0 and isinstance(args[0], bytes):
        args = (args[0].decode(),) + args[1:]
    
    # Add default handler for Decimal
    kwargs["default"] = default
    
    return orjson.dumps(*args, **kwargs).decode()


def json_loads(*args, **kwargs):
    return orjson.loads(*args, **kwargs)