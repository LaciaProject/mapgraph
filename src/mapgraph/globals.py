from __future__ import annotations

import functools
from contextvars import ContextVar, copy_context
from typing import (
    Callable,
    Tuple,
    Iterable,
    Iterator,
    Sequence,
    Mapping,
    MappingView,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Set,
    List,
    Dict,
    ItemsView,
    KeysView,
    ValuesView,
    DefaultDict,
    OrderedDict,
    Deque,
    ChainMap,
)

from .context import InstanceContext
from .typing import P, R

GLOBAL_INSTANCE_CONTEXT = InstanceContext()

INSTANCE_CONTEXT_VAR = ContextVar("InstanceContext", default=GLOBAL_INSTANCE_CONTEXT)

CHECK_TYPE_SCOPE = (
    Tuple,
    Iterable,
    Iterator,
    Sequence,
    Mapping,
    MappingView,
    MutableMapping,
    MutableSequence,
    MutableSet,
    Set,
    List,
    Dict,
    ItemsView,
    KeysView,
    ValuesView,
    DefaultDict,
    Deque,
    OrderedDict,
    ChainMap,
)


def _standalone_context(func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return copy_context().run(func, *args, **kwargs)

    return wrapper
