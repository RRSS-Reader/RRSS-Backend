from asyncio import iscoroutinefunction
from typing import Callable, Awaitable, Any, overload
from asyncer import asyncify


# overload when func returns awaitable
@overload
def ensure_asyncify[
    **T_Params, T_Ret
](func: Callable[T_Params, Awaitable[T_Ret]]) -> Callable[
    T_Params, Awaitable[T_Ret]
]: ...


# overload when function is sync function
@overload
def ensure_asyncify[**T_Params, T_Ret](func: Callable[T_Params, T_Ret]) -> Callable[
    T_Params,
    Awaitable[T_Ret],
]: ...


def ensure_asyncify[
    **T_Params, T_Ret
](func: Callable[T_Params, T_Ret]) -> (
    Callable[T_Params, T_Ret] | Callable[T_Params, Awaitable[T_Ret]]
):
    """
    Return the received function object,
    asyncify the function if it's not a coroutine function (using `asyncer` package)

    Check out [Asyncer Docs](https://asyncer.tiangolo.com/tutorial/install/) for more info.
    """
    if not iscoroutinefunction(func):
        return asyncify(func)
    return func
