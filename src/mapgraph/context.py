from __future__ import annotations

import itertools
from contextlib import contextmanager
from typing import Any, cast, TypeVar, Type, Iterable, Iterator

from .type_utils import like_isinstance

T = TypeVar("T")


class ChainList(Iterable[Any]):
    def __init__(self, *iterables: Iterable[Any]):
        self.iterables = list(iterables)

    def extend(self, *other: Iterable[Any]):
        self.iterables.extend(other)

    def __iter__(self) -> Iterator[Any]:
        return itertools.chain(*self.iterables)

    def __contains__(self, item: Any) -> bool:
        return any(item in it for it in self.iterables)


class InstanceContext:
    instances: ChainList

    def __init__(self):
        self.instances = ChainList()

    def store(self, *targets: Any):
        self.instances.extend(targets)

    def get(self, target: Type[T]) -> T:
        for instance in self.instances:
            if like_isinstance(instance, target):
                return cast(T, instance)
        raise KeyError(target)

    def is_target(self, target: Type[T]) -> bool:
        for instance in self.instances:
            if like_isinstance(instance, target):
                return True
        return False

    @contextmanager
    def scope(self, *, inherit: bool = True):
        from .globals import INSTANCE_CONTEXT_VAR

        if inherit:
            res = InstanceContext()
            res.instances.extend(self.instances, INSTANCE_CONTEXT_VAR.get().instances)
            with res.scope(inherit=False):
                yield self
        else:
            token = INSTANCE_CONTEXT_VAR.set(self)
            try:
                yield self
            finally:
                INSTANCE_CONTEXT_VAR.reset(token)
