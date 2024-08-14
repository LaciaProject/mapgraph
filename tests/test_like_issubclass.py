import pytest

from typing import List, Dict, Type, Union, TypeVar, Protocol, Generic, Iterable, Optional

from mapgraph.typevar import check_typevar_model as like_issubclass


# 定义 Protocol 和 TypedDict 以便测试
class MyProtocol(Protocol):
    def method(self) -> str: ...


class ImplMyProtocol:
    def method(self) -> str:
        return "hello"


# 新增泛型类
T = TypeVar("T")
V = TypeVar("V")
K = TypeVar("K")


class MyGenericClass(Generic[T]):
    def __init__(self, value: T):
        self.value = value


class MyProtocolGeneric(Protocol[T, V]):
    a: Iterable[dict[T, V]]

    def output(self, value: T) -> T: ...


class ImplMyProtocolClass:
    a: list[dict[str, int]]

    def output(self, value: str) -> str:
        return value


class ImplMyGeneric(Generic[T, K]):
    a: list[dict[T, K]]

    def output(self, value: T) -> T:
        return value

class ImplMyGeneric2(ImplMyGeneric[int, str]):
    ...

def test_like_issubclass():
    # 常见类型测试
    assert like_issubclass(int, int)
    assert like_issubclass(str, str)
    assert not like_issubclass(int, str)
    assert not like_issubclass(str, int)

    # 泛型测试
    assert like_issubclass(List[int], List)
    assert like_issubclass(Dict[str, int], Dict)
    assert not like_issubclass(Dict[str, int], List)

    # 嵌套类型测试
    assert like_issubclass(List[Dict[str, List[int]]], List)
    assert not like_issubclass(List[Dict[str, List[int]]], Dict)

    # Union类型测试
    assert like_issubclass(Union[Union[int, str], float], Union[int, str, float])
    assert like_issubclass(Union[int, str, int], Union[str, int])
    assert like_issubclass(Union[int, str], Union[str, int])
    assert not like_issubclass(Union[int, str], Union[str, float])
    assert not like_issubclass(Union[int, str], List[int | str])

    # Optional类型测试
    assert like_issubclass(Optional[int], None | int)
    assert like_issubclass(Optional[int], Optional[int | str])
    assert not like_issubclass(Optional[int], Optional[str])
    assert not like_issubclass(Optional[int], str | None)
    
    # Type类型测试
    assert like_issubclass(Type[int], Type)
    assert not like_issubclass(Type[int], int)

    # 泛型类测试
    assert like_issubclass(MyGenericClass[int], MyGenericClass)
    assert not like_issubclass(MyGenericClass[int], MyGenericClass[str])

    # Protocol测试
    assert like_issubclass(ImplMyProtocol, MyProtocol)

    class AnotherImplMyProtocol:
        def method(self) -> str:
            return "another hello"

    assert like_issubclass(AnotherImplMyProtocol, MyProtocol)

    class NotImplMyProtocol:
        def another_method(self) -> str:
            return "not implementing"

    assert not like_issubclass(NotImplMyProtocol, MyProtocol)

    # 泛型 Protocol 测试
    assert like_issubclass(ImplMyProtocolClass, MyProtocolGeneric[str, int])
    assert not like_issubclass(ImplMyProtocolClass, MyProtocolGeneric[int, str])

    assert like_issubclass(ImplMyGeneric[int, str], MyProtocolGeneric[int, str])
    assert not like_issubclass(ImplMyGeneric[str, int], MyProtocolGeneric[int, str])

    assert like_issubclass(ImplMyGeneric2, MyProtocolGeneric[int, str])
    assert not like_issubclass(ImplMyGeneric2, MyProtocolGeneric[str, int])


if __name__ == "__main__":
    pytest.main()
