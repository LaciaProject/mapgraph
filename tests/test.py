# example.py

from typing import TypeVar, Generic
from typing_extensions import Annotated

from mapgraph.instance_of import InstanceOf, get_instance, is_instance
from mapgraph.context import InstanceContext
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT

from pydantic import Field

T = TypeVar("T")


class Obj(Generic[T]):
    a: T

    def __init__(self, a: T):
        self.a = a


context = InstanceContext()
local_context = InstanceContext()

GLOBAL_INSTANCE_CONTEXT.store("GLOBAL", 10, {"a": 10}, Obj[int](10))
local_context.store(1, {1: "a"}, Obj[str]("1"))
context.store("context")


class Test:
    a = InstanceOf(str)
    b = InstanceOf(int)


test = Test()

assert test.a == "GLOBAL"
assert test.b == 10

assert get_instance(Obj[int]).a == 10
assert is_instance(Obj[str]) is False

with local_context.scope():
    assert test.a == "GLOBAL"
    assert test.b == 1
    with context.scope():
        print(get_instance(Annotated[int, Field(gt=1)]))
        print(get_instance(dict))
        print(get_instance(dict[str, int]))
        print(get_instance(Obj).a)
        print(get_instance(Obj[int]).a)
        print(is_instance(dict[str, int]), get_instance(dict[str, int]))
