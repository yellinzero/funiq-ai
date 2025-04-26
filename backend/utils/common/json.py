from decimal import Decimal
from typing import Any

import orjson
from babel.support import LazyProxy

from utils.common.i18n import translate_text


def default(obj: Any) -> Any:
    """Default JSON serializer"""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, LazyProxy):
        return translate_text(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


def json_dumps(*args, **kwargs) -> str:
    # Special handling for bytes
    if len(args) > 0 and isinstance(args[0], bytes):
        args = (args[0].decode(),) + args[1:]
    
    # Add default handler for Decimal and LazyProxy
    kwargs["default"] = default
    
    return orjson.dumps(*args, **kwargs).decode()


def json_loads(*args, **kwargs):
    return orjson.loads(*args, **kwargs)