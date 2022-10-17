import asyncio
import inspect
import json
from typing import Any, Callable, Union
from typing import NewType


def try_parse_json(o):
    try:
        return json.loads(o)
    except:
        return o


def as_awaitable(func: Callable) -> Callable:
    """
    Makes an callable awaitable.
    :param func:
    :return:
    """
    if inspect.iscoroutinefunction(func):
        return func
    else:
        async def coro(*args, **kwargs):
            return func(*args, **kwargs)

        return coro