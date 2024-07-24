<div align="center">

# Mapgraph

_**Mapgraph** 是一个便捷实用的上下文管理工具_

> 一阴一阳之谓道

 [![CodeFactor](https://www.codefactor.io/repository/github/LaciaProject/mapgraph/badge)](https://www.codefactor.io/repository/github/LaciaProject/mapgraph)
 [![GitHub](https://img.shields.io/github/license/LaciaProject/mapgraph)](https://github.com/LaciaProject/mapgraph/blob/master/LICENSE)
 [![CodeQL](https://github.com/LaciaProject/mapgraph/workflows/CodeQL/badge.svg)](https://github.com/LaciaProject/mapgraph/blob/master/.github/workflows/codeql.yml)

</div>

## 功能

* 上下文管理/切换
* 描述器支持
* 一流的类型支持

## 安装

```sh
pip install mapgraph
```

Or

```sh
pdm add mapgraph
```

## 入门指南

### 全局上下文对象

```python
from mapgraph.instance_of import get_instance
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT

GLOBAL_INSTANCE_CONTEXT.store(666)

assert get_instance(int) == 666
```

### 描述器支持

```python
from mapgraph.instance_of import InstanceOf, get_instance
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT

GLOBAL_INSTANCE_CONTEXT.store(666)

class Test:
    a = InstanceOf(int)

assert Test().a == 666
```

### 实例上下文

```python
from mapgraph.instance_of import InstanceOf, get_instance
from mapgraph.context import InstanceContext
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT

context = InstanceContext()

GLOBAL_INSTANCE_CONTEXT.store(666)

context.store(6, "6")

assert get_instance(int) == 666

with context.scope():
    assert get_instance(int) == 6
    assert get_instance(str) == "6"
```

### 泛型支持

```python
from typing import TypeVar, Generic
from typing_extensions import Annotated

from mapgraph.instance_of import get_instance
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


assert get_instance(Obj[int]).a == 10

with local_context.scope():
    assert get_instance(Obj[str]).a == "1"
    with context.scope():
        assert get_instance(int) == 1
        assert get_instance(Annotated[int, Field(gt=1)]) == 10
        assert get_instance(dict) == {1: "a"}
        assert get_instance(dict[str, int]) == {"a": 10}
```

## 支持类型

### like_isinstance

* 基础类型 str/int/...
* 容器泛型 list[T]/dict[K, V]/...
* Union 类型类型
* Type 
* TypeVar 类型变量
* 泛型类 Generic[T]
* Annotated/Field 注解类型
* Protocol 协议类型
* Protocol[T] 泛型协议类型
* TypedDict 字典类型

### like_issubclass

* 基础类型 str/int
* 容器泛型 list[T]/dict[K, V]
* Union 类型类型
* Type 
* TypeVar 类型变量
* 泛型类 Generic[T]
* Protocol 协议类型
* Protocol[T] 泛型协议类型
