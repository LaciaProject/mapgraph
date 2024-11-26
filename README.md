<div align="center">

# Mapgraph

_`mapgraph` 提供了强大的对象控制工具, 覆盖了配置管理、状态管理、上下文管理和生命周期管理。_

> 一阴一阳之谓道

 [![CodeFactor](https://www.codefactor.io/repository/github/LaciaProject/mapgraph/badge)](https://www.codefactor.io/repository/github/LaciaProject/mapgraph)
 [![GitHub](https://img.shields.io/github/license/LaciaProject/mapgraph)](https://github.com/LaciaProject/mapgraph/blob/master/LICENSE)
 [![CodeQL](https://github.com/LaciaProject/mapgraph/workflows/CodeQL/badge.svg)](https://github.com/LaciaProject/mapgraph/blob/master/.github/workflows/codeql.yml)

</div>

## 功能

* 配置管理
  * 基于类型声明的配置
  * 支持实时变更
* 上下文管理
  * 基于描述器的依赖注入
  * 优雅的上下文切换
* 生命周期管理
  * 服务编排
* 状态管理

## 安装

```sh
pip install mapgraph
```

Or

```sh
pdm add mapgraph
```

## 入门指南

### 上下文管理

```python
from mapgraph.context import InstanceContext
```

`InstanceContext` 实例上下文, 顾名思义是管理 `对象` 的抽象, 它通过两个维度对 `对象` 进行管理, 即 `名义类型` 与 `值`。

* `名义类型` 可以理解为 `变量名` 或者是 `变量类型`, 总之它在当前实例上下文是唯一的 `KEY`
* `值` 很好理解，即是某个被管理的 `对象`

```python
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT
```

`GLOBAL_INSTANCE_CONTEXT` 全局实例上下文, 即最顶层的命名空间, 本质也是一个 `InstanceContext`。

#### 基本使用

```python
from typing import NewType

from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT
from mapgraph.instance_of import get_instance

MYINT = NewType("MYINT", int)

GLOBAL_INSTANCE_CONTEXT.store(123, "test")
# GLOBAL_INSTANCE_CONTEXT.store({int: 123, str: "test"}) 
GLOBAL_INSTANCE_CONTEXT.store({list[int]: [1,2,3]})
GLOBAL_INSTANCE_CONTEXT.store({MYINT: -123})

print(get_instance(int)) # 123
print(get_instance(MYINT)) # 123
print(get_instance(MYINT, is_key=True)) # -123
print(get_instance(str)) # test
print(get_instance(list[int])) # [1,2,3]
```

* `get_instance` 可以通过类型获取 `InstanceContext` 中的值, 当 `is_key=True` 为 `名义类型` 匹配, 反之为 `值` 匹配
* `.store` 拥有可变位置参数 `collection_or_targets` 类型为 `Mapping[type, Any] | Any`
* `.store(123, "test")` 等价于 `.store({int: 123, str: "test"})`

> 因为运行时类型检查器拥有的局限性，所以分别引入了 `名义类型` 与 `值`，它们相互补充

#### 多级实例上下文

```python
from mapgraph.context import InstanceContext
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT
from mapgraph.instance_of import get_instance

loacl_context = InstanceContext()

GLOBAL_INSTANCE_CONTEXT.store(123, {list[int]: [1,2,3]})
loacl_context.store("test", -123)

print(get_instance(int)) # 123
# print(get_instance(str)) # ValueError: <class 'str'>

with loacl_context.scope():
    print(get_instance(str)) # test
    print(get_instance(int)) # -123
    print(get_instance(list[int])) # [1,2,3]

with loacl_context.scope(inherit=False):
    print(get_instance(str)) # test
    print(get_instance(int)) # -123
    print(get_instance(list[int])) # ValueError: <class 'list[int]'>
```

> `.scope` 拥有关键字参数 `inherit`, 表示是否继承上一级 `InstanceContext`

#### 描述器支持

```python
from typing import NewType

from httpx import AsyncClient
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT
from mapgraph.instance_of import get_instance, InstanceOf, InstanceOfK, InstanceOfV

OPENAI_API_KEY = NewType("OPENAI_API_KEY", str)

class Test:
    client: InstanceOfV[AsyncClient] = InstanceOf(AsyncClient)
    openai_api_key: InstanceOfK[OPENAI_API_KEY] = InstanceOf(OPENAI_API_KEY, is_key=True)

GLOBAL_INSTANCE_CONTEXT.store({OPENAI_API_KEY: "test"}, AsyncClient())

test = Test()

print(test.client) # <httpx.AsyncClient object at 0x7f7f7f7f7f7f>
print(test.openai_api_key) # test
```

`InstanceOf` 是一个函数会返两种描述器 `InstanceOfV[T]` 与 `InstanceOfK[T]`, 很好理解 前者被声明为通过 `值` 匹配, 后者被声明通过 `名义类型` 匹配。

#### 描述器读取

```python
from typing import NewType

from httpx import AsyncClient
from mapgraph.context import InstanceContext
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT
from mapgraph.instance_of import get_instance, InstanceOf, InstanceOfK, InstanceOfV

OPENAI_API_KEY = NewType("OPENAI_API_KEY", str)
BASE_URL = NewType("BASE_URL", str)

loacl_context = InstanceContext()

class Test:
    client: InstanceOfV[AsyncClient] = InstanceOf(AsyncClient)
    openai_api_key: InstanceOfK[OPENAI_API_KEY] = InstanceOf(OPENAI_API_KEY, is_key=True)
    base_url: InstanceOfK[BASE_URL] = InstanceOf(BASE_URL, is_key=True)

GLOBAL_INSTANCE_CONTEXT.store({OPENAI_API_KEY: "sk-proj-xxx", BASE_URL: "https://api.openai.com"}, AsyncClient())
loacl_context.store({BASE_URL: "https://api.xxxmy.com"})

test = Test()

print(test.client) # <httpx.AsyncClient object at 0x7f7f7f7f7f7f>
print(test.openai_api_key) # sk-proj-xxx
print(test.base_url) # https://api.openai.com

with loacl_context.scope():
    print(test.base_url) # https://api.xxxmy.com
```

#### 描述器写入

```python
from typing import NewType

from httpx import AsyncClient
from mapgraph.context import InstanceContext
from mapgraph.globals import GLOBAL_INSTANCE_CONTEXT
from mapgraph.instance_of import get_instance, InstanceOf, InstanceOfK, InstanceOfV

OPENAI_API_KEY = NewType("OPENAI_API_KEY", str)
BASE_URL = NewType("BASE_URL", str)

loacl_context = InstanceContext()

class Test:
    client: InstanceOfV[AsyncClient] = InstanceOf(AsyncClient)
    base_url: InstanceOfK[BASE_URL] = InstanceOf(BASE_URL, is_key=True)


GLOBAL_INSTANCE_CONTEXT.store(
    {BASE_URL: "https://api.openai.com"}, AsyncClient()
)
loacl_context.store({BASE_URL: "https://api.xxxmy.com"})

test = Test()

print(id(test.client))  # 139921911645712
print(test.base_url)  # https://api.openai.com

with loacl_context.scope():
    print(test.base_url)  # https://api.xxxmy.com
    print(id(test.client))  # 139921911645712
    test.base_url = {BASE_URL: BASE_URL("https://api.yyymy.com")}
    test.client = AsyncClient()
    print(test.base_url)  # https://api.yyymy.com
    print(id(test.client))  # 140043844997072

print(test.base_url)  # https://api.openai.com
print(id(test.client))  # 139921911645712
```

* 当描述器为 `InstanceOfK[T]` 时, 设置值需要一个 `Mapping[Type[T], T]`
* 当描述器为 `InstanceOfV[T]` 时, 设置值需要为 `T`

### 配置管理

**.env**

```.env
OPENAI_API_KEY = "sk-proj-xxx"
BASE_URL = "https://api.openai.com"
MYINT = 123
MYDICT = {"a": 1}
MYLIST = [1, 2, 3]
```

```python
from typing import NewType

from mapgraph.config import load_env
from mapgraph.instance_of import InstanceOf

OPENAI_API_KEY = NewType("OPENAI_API_KEY", str)
BASE_URL = NewType("BASE_URL", str)
MYINT = NewType("MYINT", int)
MYLIST = NewType("MYLIST", list[int])
MYDICT = NewType("MYDICT", dict[str, int])
MYBOOL = NewType("MYBOOL", bool)

class ConfigData:
    a = InstanceOf(MYINT, is_key=True)
    b = InstanceOf(MYLIST, is_key=True)
    c = InstanceOf(MYDICT, is_key=True)
    d = InstanceOf(MYBOOL, is_key=True)

class Config:
    api_key = InstanceOf(OPENAI_API_KEY, is_key=True)
    base_url = InstanceOf(BASE_URL, is_key=True)
    data = ConfigData()


load_env(
    envs=(OPENAI_API_KEY, BASE_URL, MYINT, MYLIST, MYDICT), 
    envs_kv={MYBOOL: False}, # 设置默认值
    dotenv_path=".env"
)

config = Config()

print(config.api_key) # sk-proj-xxx
print(config.base_url) # https://api.openai.com
print(config.data.a) # 123
print(config.data.b) # [1, 2, 3]
print(config.data.c) # {'a': 1}
print(config.data.d) # False
```

> 最佳实践是控制所需的最细的粒度, 当配置较为复杂可以进行嵌套

### 状态管理

依赖于 [statv](https://github.com/GraiaProject/statv) [文档](https://graia.cn/other/statv/)

### 生命周期管理

* `mapgraph.lifecycle` 提供了 `launch_services` 服务自动编排

```python
class BaseService(Protocol):
    id: str

    @property
    def required(self) -> set[str]: ...

    async def preparing(self) -> None: ...

    async def blocking(self) -> None: ...

    async def cleanup(self) -> None: ...

    def get_service(self) -> set[BaseService]: ...
```

* id: 服务的唯一标识符
* required: 服务的依赖
* preparing: 服务的准备阶段
* blocking: 服务的阻塞阶段
* cleanup: 服务的清理阶段
* get_service: 获取服务的依赖
