import pytest

from typing import List, Dict, Type, Union, TypeVar, Protocol, Generic
from typing_extensions import Annotated, TypedDict

from pydantic import Field

# from mapgraph.type_utils import like_issubclass

from mapgraph.typevar import check_typevar_model as like_issubclass


# 定义 Protocol 和 TypedDict 以便测试
class MyProtocol(Protocol):
    def method(self) -> str: ...


class ImplMyProtocol:
    def method(self) -> str:
        return "hello"


# 新增泛型类
T = TypeVar("T")


class MyGenericClass(Generic[T]):
    def __init__(self, value: T):
        self.value = value


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

    # Type类型测试
    assert like_issubclass(Type[int], Type)
    assert not like_issubclass(Type[int], int)

    # 泛型类测试
    assert like_issubclass(MyGenericClass[int], MyGenericClass)
    assert not like_issubclass(MyGenericClass[int], MyGenericClass[str])

    # # Annotated测试
    # AnnotatedStrField = Annotated[str, Field(description="A simple string")]
    # AnnotatedStrIntField = Annotated[Union[str, int], Field(description="A string or integer")]
    # AnnotatedIntField = Annotated[int, Field(description="A simple string", gt=1, lt=10)]

    # assert like_issubclass(AnnotatedStrField, str)
    # assert like_issubclass(AnnotatedStrIntField, Union)
    # assert like_issubclass(AnnotatedIntField, int)

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


if __name__ == "__main__":
    pytest.main()
