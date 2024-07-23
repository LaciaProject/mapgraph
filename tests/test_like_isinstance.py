from typing import List, Dict, Type, Union, TypeVar, Protocol, Generic
from typing_extensions import Annotated, TypedDict
from dataclasses import dataclass

import pytest
from pydantic import Field

from mapgraph.type_utils import like_isinstance


# 定义 Protocol 和 TypedDict 以便测试
class MyProtocol(Protocol):
    def method(self) -> str: ...


class ImplMyProtocol:
    def method(self) -> str:
        return "hello"


class MyTypedDict(TypedDict):
    key: str
    value: int


# 新增泛型类
T = TypeVar("T")


class MyGenericClass(Generic[T]):
    def __init__(self, value: T):
        self.value = value


def test_like_isinstance():
    # 常见类型测试
    assert like_isinstance(10, int)
    assert like_isinstance("hello", str)
    assert not like_isinstance(10, str)
    assert not like_isinstance("hello", int)

    # 泛型测试
    assert like_isinstance([1, 2, 3], List[int])
    assert not like_isinstance([1, 2, "3"], List[int])
    assert like_isinstance({"key": "value"}, Dict[str, str])
    assert not like_isinstance({"key": 123}, Dict[str, str])

    # 嵌套类型测试
    assert like_isinstance([{"key": [1, 2, 3]}], List[Dict[str, List[int]]])
    assert not like_isinstance([{"key": ["1", "2", 3]}], List[Dict[str, List[int]]])

    # Union类型测试
    assert like_isinstance("hello", Union[int, str])
    assert like_isinstance(10, Union[int, str])
    assert not like_isinstance(10.5, Union[int, str])

    # Type类型测试
    assert like_isinstance(int, Type[int])
    assert not like_isinstance(str, Type[int])

    # 泛型类实例测试
    inst_str = MyGenericClass[str]("test")
    inst_int = MyGenericClass[int](123)
    inst_list = MyGenericClass[list[int]]([1, 2, 3])

    assert like_isinstance(inst_str, MyGenericClass[str])
    assert not like_isinstance(inst_str, MyGenericClass[int])

    assert like_isinstance(inst_int, MyGenericClass[int])
    assert not like_isinstance(inst_int, MyGenericClass[str])

    assert like_isinstance(inst_list, MyGenericClass[list[int]])
    assert not like_isinstance(inst_list, MyGenericClass[list[str]])

    # Annotated和Field测试
    AnnotatedStrField = Annotated[str, Field(description="A simple string")]
    AnnotatedStrIntField = Annotated[
        Union[str, int], Field(description="A string or integer")
    ]
    AnnotatedIntField = Annotated[
        int, Field(description="A simple string", gt=1, lt=10)
    ]

    assert like_isinstance("a string", AnnotatedStrField)
    assert not like_isinstance(100, AnnotatedStrField)
    assert like_isinstance(100, AnnotatedStrIntField)
    assert like_isinstance("another string", AnnotatedStrIntField)
    assert not like_isinstance(10.5, AnnotatedStrIntField)
    assert like_isinstance(5, AnnotatedIntField)
    assert not like_isinstance(0, AnnotatedIntField)

    # Protocol测试
    assert like_isinstance(ImplMyProtocol(), MyProtocol)

    class AnotherImplMyProtocol:
        def method(self) -> str:
            return "another hello"

    assert like_isinstance(AnotherImplMyProtocol(), MyProtocol)

    class NotImplMyProtocol:
        def another_method(self) -> str:
            return "not implementing"

    assert not like_isinstance(NotImplMyProtocol(), MyProtocol)

    # TypedDict测试
    valid_typed_dict_instance = {"key": "test", "value": 123}
    invalid_typed_dict_instance = {"key": "test", "value": "123"}
    assert like_isinstance(valid_typed_dict_instance, MyTypedDict)
    assert not like_isinstance(invalid_typed_dict_instance, MyTypedDict)


if __name__ == "__main__":
    pytest.main()
