from __future__ import annotations

from typing import (
    Any,
    Generic,
    TypeVar,
    overload,
    Type,
    Annotated,
    Mapping,
    Callable,
    Optional,
)

from typing_extensions import Self, Literal

from .globals import INSTANCE_CONTEXT_VAR

T = TypeVar("T")


class _MISSING_TYPE:
    pass


MISSING = _MISSING_TYPE()


class InstanceOfV(Generic[T]):
    target: Type[T]

    def __init__(
        self,
        target: Type[T],
        default: T | Any = MISSING,
        check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
    ) -> None:
        self.target = target
        self._default = default
        self._check_func = check_func

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: type) -> T: ...

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self
        try:
            res = INSTANCE_CONTEXT_VAR.get().get(
                self.target, check_func=self._check_func
            )
            return res
        except (KeyError, ValueError) as e:
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

    def __init__(
        self,
        target: Type[T],
        default: T | Any = MISSING,
        check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
    ) -> None:
        self.target = target
        self._default = default
        self._check_func = check_func

    @overload
    def __get__(self, instance: None, owner: type) -> Self: ...

    @overload
    def __get__(self, instance: Any, owner: type) -> T: ...

    def __get__(self, instance: Any, owner: type):
        if instance is None:
            return self
        try:
            res = INSTANCE_CONTEXT_VAR.get().get(
                self.target, is_key=True, check_func=self._check_func
            )
            return res
        except (KeyError, ValueError) as e:
            if self._default is not MISSING:
                return self._default
            raise e

    def __set__(self, instance: Any, value: Mapping[Type[T], T]) -> None:
        if instance is None:
            raise AttributeError("Cannot set attribute on class")
        else:
            INSTANCE_CONTEXT_VAR.get().store(value)


@overload
def InstanceOf(
    target: Type[T],
    is_key: Literal[False],
    default: T | Any = MISSING,
    check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
) -> InstanceOfV[T]: ...
@overload
def InstanceOf(
    target: Type[T],
    is_key: Literal[True],
    default: T | Any = MISSING,
    check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
) -> InstanceOfK[T]: ...
@overload
def InstanceOf(
    target: Type[T],
    is_key: bool = False,
    default: T | Any = MISSING,
    check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
) -> InstanceOfV[T]: ...


def InstanceOf(
    target: Type[T],
    is_key: bool = False,
    default: T | Any = MISSING,
    check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
) -> InstanceOfV[T] | InstanceOfK[T]:
    if is_key:
        return InstanceOfK[T](target, default=default, check_func=check_func)
    return InstanceOfV[T](target, default=default, check_func=check_func)


def get_instance(
    target: Type[T] | Annotated,
    is_key: bool = False,
    check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
) -> T:
    return INSTANCE_CONTEXT_VAR.get().get(target, is_key=is_key, check_func=check_func)


def is_instance(
    target: Type[T] | Annotated,
    is_key: bool = False,
    check_func: Optional[Callable[[Type[T], Type[T], T], bool]] = None,
) -> bool:
    return INSTANCE_CONTEXT_VAR.get().has_value(
        target, is_key=is_key, check_func=check_func
    )
