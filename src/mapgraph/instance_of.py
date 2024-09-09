from __future__ import annotations

from typing import Any, Generic, TypeVar, overload, Type, Annotated, Mapping

from typing_extensions import Self, Literal

from .globals import INSTANCE_CONTEXT_VAR

T = TypeVar("T")

class _MISSING_TYPE:
    pass
MISSING = _MISSING_TYPE()

class InstanceOfV(Generic[T]):
    target: Type[T]

    def __init__(self, target: Type[T], default: T | Any = MISSING) -> None:
        self.target = target
        self._default = default

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: type) -> T: ...

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self
        try:
            res =  INSTANCE_CONTEXT_VAR.get().get_by_value(self.target)
            return res
        except ValueError as e:
            if self._default is not MISSING:
                return self._default
            raise e

    def __set__(self, instance: Any, value: T) -> None:
        if instance is None:
            raise AttributeError("Cannot set attribute on class")
        else:
            INSTANCE_CONTEXT_VAR.get().store(value)


class InstanceOfK(Generic[T]):
    target: Type[T]

    def __init__(self, target: Type[T], default: T | Any = MISSING) -> None:
        self.target = target
        self._default = default

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: type) -> T: ...

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self
        try:
            res =  INSTANCE_CONTEXT_VAR.get().get_by_key(self.target)
            return res
        except KeyError as e:
            if self._default is not MISSING:
                return self._default
            raise e


    def __set__(self, instance: Any, value: Mapping[Type[T], T]) -> None:
        if instance is None:
            raise AttributeError("Cannot set attribute on class")
        else:
            INSTANCE_CONTEXT_VAR.get().store(value)


@overload
def InstanceOf(target: Type[T], is_key: Literal[False], default: T | Any = MISSING) -> InstanceOfV[T]: ...
@overload
def InstanceOf(target: Type[T], is_key: Literal[True], default: T | Any = MISSING) -> InstanceOfK[T]: ...
@overload
def InstanceOf(target: Type[T], is_key: bool = False, default: T | Any = MISSING) -> InstanceOfV[T]: ...

def InstanceOf(
    target: Type[T], is_key: bool = False, default: T | Any = MISSING
) -> InstanceOfV[T] | InstanceOfK[T]:
    if is_key:
        return InstanceOfK[T](target, default=default)
    return InstanceOfV[T](target, default=default)


def get_instance(target: Type[T] | Annotated, is_key: bool = False) -> T:
    if is_key:
        return INSTANCE_CONTEXT_VAR.get().get_by_key(target)
    return INSTANCE_CONTEXT_VAR.get().get_by_value(target)


def is_instance(target: Type[T] | Annotated, is_key: bool = False) -> bool:
    if is_key:
        return INSTANCE_CONTEXT_VAR.get().has_key_of_type(target)
    return INSTANCE_CONTEXT_VAR.get().has_value_of_type(target)
