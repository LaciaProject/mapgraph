from __future__ import annotations

from collections import ChainMap
from contextlib import contextmanager
from typing import Any, cast, TypeVar, Type, MutableMapping, Mapping, Optional, Callable

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

    def get(
        self,
        target_type: Type[T],
        is_key: bool = False,
        check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
    ) -> T:
        if check_func is not None:
            for key, value in self.iter_items():
                try:
                    y = check_func(target_type, key, value)
                except Exception:
                    y = False
                if y:
                    return cast(T, value)
            raise ValueError(target_type)
        if is_key:
            return self.get_by_key(target_type)
        return self.get_by_value(target_type)

    def get_all(
        self,
        target_type: Type[T],
        is_key: bool = False,
        check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
    ):
        """遍历出所有符合要求的值"""

        if check_func is not None:
            for key, value in self.iter_items(all_maps=True):
                try:
                    y = check_func(target_type, key, value)
                except Exception:
                    y = False
                if y:
                    yield cast(T, value)
        elif is_key:
            for key, value in self.iter_items(all_maps=True):
                if like_issubclass(key, target_type):
                    yield cast(T, value)
        else:
            for key, value in self.iter_items(all_maps=True):
                if like_isinstance(value, target_type):
                    yield cast(T, value)

    def iter_items(self, all_maps: bool = False):
        if all_maps:
            if isinstance(self.instances, ChainMap):
                for i in self.instances.maps:
                    for key, value in i.items():
                        yield key, value
            else:
                for key, value in self.instances.items():
                    yield key, value
        else:
            for key, value in self.instances.items():
                yield key, value

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

    def has_value(
        self,
        target_type: Type[T],
        is_key: bool = False,
        check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
    ) -> bool:
        if check_func is not None:
            for key, value in self.instances.items():
                try:
                    y = check_func(target_type, key, value)
                except Exception:
                    y = False
                if y:
                    return True
            return False
        if is_key:
            return self.has_key_of_type(target_type)
        return self.has_value_of_type(target_type)

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
