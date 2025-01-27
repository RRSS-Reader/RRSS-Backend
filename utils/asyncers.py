from asyncio import iscoroutinefunction
from typing import Callable, Awaitable
from asyncer import asyncify


def ensure_asyncify[
    **T_Params, T_Ret
](func: Callable[T_Params, T_Ret]) -> Callable[T_Params, Awaitable[T_Ret]]:
    """
    Return the received function object,
    asyncify the function if it's not a coroutine function
    """
    if not iscoroutinefunction(func):
        return asyncify(func)
    return func
