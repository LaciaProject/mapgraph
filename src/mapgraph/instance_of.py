from __future__ import annotations

from typing import Any, Generic, TypeVar, overload, Type, Annotated, Mapping

from typing_extensions import Self, Literal

from .globals import INSTANCE_CONTEXT_VAR

T = TypeVar("T")


class InstanceOfV(Generic[T]):
    target: Type[T]

    def __init__(self, target: Type[T]) -> None:
        self.target = target

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: type) -> T: ...

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self
        return INSTANCE_CONTEXT_VAR.get().get_by_value(self.target)

    def __set__(self, instance: Any, value: T) -> None:
        if instance is None:
            raise AttributeError("Cannot set attribute on class")
        else:
            INSTANCE_CONTEXT_VAR.get().store(value)


class InstanceOfK(Generic[T]):
    target: Type[T]

    def __init__(self, target: Type[T]) -> None:
        self.target = target

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: type) -> T: ...

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self
        return INSTANCE_CONTEXT_VAR.get().get_by_key(self.target)

    def __set__(self, instance: Any, value: Mapping[Type[T], T]) -> None:
        if instance is None:
            raise AttributeError("Cannot set attribute on class")
        else:
            INSTANCE_CONTEXT_VAR.get().store(value)


@overload
def InstanceOf(target: Type[T], is_key: Literal[False]) -> InstanceOfV[T]: ...
@overload
def InstanceOf(target: Type[T], is_key: Literal[True]) -> InstanceOfK[T]: ...
@overload
def InstanceOf(target: Type[T], is_key: bool = False) -> InstanceOfV[T]: ...

def InstanceOf(
    target: Type[T], is_key: bool = False
) -> InstanceOfV[T] | InstanceOfK[T]:
    if is_key:
        return InstanceOfK[T](target)
    return InstanceOfV[T](target)


def get_instance(target: Type[T] | Annotated, is_key: bool = False) -> T:
    if is_key:
        return INSTANCE_CONTEXT_VAR.get().get_by_key(target)
    return INSTANCE_CONTEXT_VAR.get().get_by_value(target)


def is_instance(target: Type[T] | Annotated, is_key: bool = False) -> bool:
    if is_key:
        return INSTANCE_CONTEXT_VAR.get().has_key_of_type(target)
    return INSTANCE_CONTEXT_VAR.get().has_value_of_type(target)
