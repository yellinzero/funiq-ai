import orjson


def json_dumps(*args, **kwargs) -> str:
    # Special handling for bytes
    if len(args) > 0 and isinstance(args[0], bytes):
        args = (args[0].decode(),) + args[1:]
    return orjson.dumps(*args, **kwargs).decode()


def json_loads(*args, **kwargs):
    return orjson.loads(*args, **kwargs)