from __future__ import annotations

from collections import ChainMap
from contextlib import contextmanager
from typing import Any, cast, TypeVar, Type, MutableMapping, Mapping

from typing_tool import like_issubclass, like_isinstance
from typing_tool.type_utils import deep_type

from .typing import cvar

T = TypeVar("T")


class InstanceContext:
    instances: MutableMapping[type, Any]

    def __init__(self):
        self.instances = {}

    def store(self, *collection_or_targets: Mapping[type, Any] | Any):
        for item in collection_or_targets:
            if isinstance(item, Mapping):
                self.instances.update(item)
            else:
                self.instances[deep_type(item)] = item

    def get_by_key(self, target_type: Type[T]) -> T:
        for key, value in self.instances.items():
            if like_issubclass(key, target_type):
                return cast(T, value)
        raise KeyError(target_type)

    def get_by_value(self, target_type: Type[T]) -> T:
        for key, value in self.instances.items():
            if like_isinstance(value, target_type):
                return cast(T, value)
        raise ValueError(target_type)

    def has_value_of_type(self, target_type: Type[T]) -> bool:
        for key, value in self.instances.items():
            if like_isinstance(value, target_type):
                return True
        return False

    def has_key_of_type(self, target_type: Type[T]) -> bool:
        for key in self.instances.keys():
            if like_issubclass(key, target_type):
                return True
        return False

    @contextmanager
    def scope(self, *, inherit: bool = True):
        from .globals import INSTANCE_CONTEXT_VAR

        if inherit:
            res = InstanceContext()
            res.instances = ChainMap(
                {}, self.instances, INSTANCE_CONTEXT_VAR.get().instances
            )

            with res.scope(inherit=False):
                yield self
        else:
            with cvar(INSTANCE_CONTEXT_VAR, self):
                yield self


# class ChainList(Iterable):
#     def __init__(self, *iterables: Iterable):
#         self.iterables = list(iterables)

#     def extend(self, *other: Iterable):
#         for iterable in other:
#             self.iterables.insert(0, iterable)

#     def __iter__(self) -> Iterator:
#         return itertools.chain(*self.iterables)

#     def __contains__(self, item) -> bool:
#         return any(item in it for it in self.iterables)

# class InstanceContext:
#     instances: ChainList

#     def __init__(self):
#         self.instances = ChainList()

#     def store(self, *targets: Any):
#         for target in targets:
#             self.instances.extend((target,))

#     def get(self, target: Type[T]) -> T:
#         for instance in self.instances:
#             if like_isinstance(instance, target):
#                 return cast(T, instance)
#         raise KeyError(target)

#     def is_target(self, target: Type[T]) -> bool:
#         for instance in self.instances:
#             if like_isinstance(instance, target):
#                 return True
#         return False

#     @contextmanager
#     def scope(self, *, inherit: bool = True):
#         from .globals import INSTANCE_CONTEXT_VAR

#         if inherit:
#             res = InstanceContext()
#             res.instances.extend(INSTANCE_CONTEXT_VAR.get().instances, self.instances)
#             with res.scope(inherit=False):
#                 yield self
#         else:
#             token = INSTANCE_CONTEXT_VAR.set(self)
#             try:
#                 yield self
#             finally:
#                 INSTANCE_CONTEXT_VAR.reset(token)
