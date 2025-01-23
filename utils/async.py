from asyncio import iscoroutinefunction
from asyncer import asyncify


def ensure_asyncify(func):
    """
    Return the received function object, asyncify the function if
    it's not a coroutine function
    """
    if not iscoroutinefunction(func):
        return asyncify(func)
    return func
