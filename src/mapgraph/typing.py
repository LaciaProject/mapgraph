from __future__ import annotations

from typing import Callable, TypeVar

from typing_extensions import ParamSpec


R = TypeVar("R", covariant=True)
P = ParamSpec("P")
CR = TypeVar("CR", covariant=True, bound=Callable)

