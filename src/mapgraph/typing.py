from __future__ import annotations

from typing import Callable, TypeVar
from contextlib import contextmanager
from contextvars import ContextVar
from typing_extensions import ParamSpec

T = TypeVar("T")
R = TypeVar("R", covariant=True)
P = ParamSpec("P")
CR = TypeVar("CR", covariant=True, bound=Callable)

@contextmanager
def cvar(var: ContextVar[T], val: T):
    token = var.set(val)
    try:
        yield val
    finally:
        var.reset(token)