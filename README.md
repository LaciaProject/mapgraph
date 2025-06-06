<div align="center">

# 🗺️ Mapgraph

**下一代 Python 对象控制框架**

*优雅的依赖注入 • 智能配置管理 • 生命周期编排*

---

[![CodeFactor](https://www.codefactor.io/repository/github/LaciaProject/mapgraph/badge)](https://www.codefactor.io/repository/github/LaciaProject/mapgraph)
[![GitHub](https://img.shields.io/github/license/LaciaProject/mapgraph)](https://github.com/LaciaProject/mapgraph/blob/master/LICENSE)
[![CodeQL](https://github.com/LaciaProject/mapgraph/workflows/CodeQL/badge.svg)](https://github.com/LaciaProject/mapgraph/blob/master/.github/workflows/codeql.yml)
[![Python Version](https://img.shields.io/badge/python-3.10+-blue.svg)](https://python.org)
[![PyPI Version](https://img.shields.io/pypi/v/mapgraph.svg)](https://pypi.org/project/mapgraph/)

</div>

## ✨ 为什么选择 Mapgraph？

在复杂的 Python 应用中，对象管理往往变得混乱不堪。Mapgraph 通过**类型安全的依赖注入**和**智能上下文管理**，让您的代码变得优雅而强大。

```python
# 🚀 一行代码，优雅注入
class APIService:
    client: AsyncClient = InstanceOf(AsyncClient)
    api_key: str = InstanceOf(API_KEY, is_key=True)
    
    async def fetch_data(self):
        return await self.client.get("/api/data")
```

## 🎯 核心特性

<table>
<tr>
<td width="50%">

### 🧠 智能依赖注入
- **类型安全**：基于 Python 类型系统
- **零配置**：自动解析依赖关系
- **多层级**：支持复杂的上下文嵌套

</td>
<td width="50%">

### ⚙️ 强大配置管理
- **类型声明**：配置即代码
- **实时更新**：动态配置变更
- **环境隔离**：多环境无缝切换

</td>
</tr>
<tr>
<td width="50%">

### 🔄 生命周期编排
- **自动编排**：智能服务依赖解析
- **优雅启停**：完整的生命周期管理
- **异步优先**：原生支持异步操作

</td>
<td width="50%">

### 🎛️ 状态管理
- **响应式**：状态变化自动通知
- **类型安全**：编译时类型检查
- **高性能**：最小化状态更新开销

</td>
</tr>
</table>

## 🚀 快速开始

### 安装

```bash
# 使用 pip
pip install mapgraph

# 使用 pdm
pdm add mapgraph

# 带可选依赖
pip install mapgraph[httpx,aiohttp]
```

### 30秒上手

```python
from typing import NewType
from mapgraph import InstanceOf, GLOBAL_INSTANCE_CONTEXT

# 1️⃣ 定义类型
DatabaseURL = NewType("DatabaseURL", str)

# 2️⃣ 创建服务类
class DatabaseService:
    url: str = InstanceOf(DatabaseURL, is_key=True)
    
    def connect(self):
        print(f"连接到数据库: {self.url}")

# 3️⃣ 注册依赖
GLOBAL_INSTANCE_CONTEXT.store({DatabaseURL: "postgresql://localhost:5432/mydb"})

# 4️⃣ 使用服务
service = DatabaseService()
service.connect()  # 输出: 连接到数据库: postgresql://localhost:5432/mydb
```

## 📚 深入指南

### 🏗️ 依赖注入系统

Mapgraph 的依赖注入基于**名义类型**和**值类型**两个维度，提供了灵活而强大的对象管理能力。

#### 基础概念

```python
from typing import NewType
from mapgraph import InstanceOf, GLOBAL_INSTANCE_CONTEXT

# 名义类型 - 用于精确匹配
API_KEY = NewType("API_KEY", str)
DATABASE_URL = NewType("DATABASE_URL", str)

# 值类型 - 用于类型匹配
from httpx import AsyncClient

class APIService:
    # 通过名义类型注入 (精确匹配)
    api_key: str = InstanceOf(API_KEY, is_key=True)
    
    # 通过值类型注入 (类型匹配)
    client: AsyncClient = InstanceOf(AsyncClient)
```

#### 多层级上下文

```python
from mapgraph import InstanceContext

# 创建本地上下文
local_context = InstanceContext()

# 全局配置
GLOBAL_INSTANCE_CONTEXT.store({
    API_KEY: "global-key",
    DATABASE_URL: "postgresql://prod:5432/db"
})

# 本地配置
local_context.store({
    API_KEY: "local-key",  # 覆盖全局配置
})

class Service:
    api_key: str = InstanceOf(API_KEY, is_key=True)
    db_url: str = InstanceOf(DATABASE_URL, is_key=True)

service = Service()
print(service.api_key)  # "global-key"

# 切换到本地上下文
with local_context.scope():
    print(service.api_key)  # "local-key"
    print(service.db_url)   # "postgresql://prod:5432/db" (继承自全局)
```

### ⚙️ 配置管理

#### 环境变量配置

创建 `.env` 文件：

```env
# .env
API_KEY=sk-proj-your-secret-key
DATABASE_URL=postgresql://localhost:5432/myapp
DEBUG=true
MAX_CONNECTIONS=10
ALLOWED_HOSTS=["localhost", "127.0.0.1"]
```

Python 代码：

```python
from typing import NewType
from mapgraph import InstanceOf, load_env

# 定义配置类型
API_KEY = NewType("API_KEY", str)
DATABASE_URL = NewType("DATABASE_URL", str)
DEBUG = NewType("DEBUG", bool)
MAX_CONNECTIONS = NewType("MAX_CONNECTIONS", int)
ALLOWED_HOSTS = NewType("ALLOWED_HOSTS", list[str])

# 加载环境变量
load_env(
    envs=(API_KEY, DATABASE_URL, DEBUG, MAX_CONNECTIONS, ALLOWED_HOSTS),
    envs_kv={DEBUG: False},  # 默认值
    dotenv_path=".env"
)

# 配置类
class AppConfig:
    api_key: str = InstanceOf(API_KEY, is_key=True)
    database_url: str = InstanceOf(DATABASE_URL, is_key=True)
    debug: bool = InstanceOf(DEBUG, is_key=True)
    max_connections: int = InstanceOf(MAX_CONNECTIONS, is_key=True)
    allowed_hosts: list[str] = InstanceOf(ALLOWED_HOSTS, is_key=True)

# 使用配置
config = AppConfig()
print(f"API Key: {config.api_key}")
print(f"Debug Mode: {config.debug}")
```

#### 嵌套配置结构

```python
class DatabaseConfig:
    url: str = InstanceOf(DATABASE_URL, is_key=True)
    max_connections: int = InstanceOf(MAX_CONNECTIONS, is_key=True)

class APIConfig:
    key: str = InstanceOf(API_KEY, is_key=True)
    base_url: str = InstanceOf(BASE_URL, is_key=True)

class AppConfig:
    database = DatabaseConfig()
    api = APIConfig()
    debug: bool = InstanceOf(DEBUG, is_key=True)

config = AppConfig()
print(f"数据库连接: {config.database.url}")
print(f"API密钥: {config.api.key}")
```

### 🔄 生命周期管理

Mapgraph 提供了强大的服务编排能力，自动解析服务依赖并按正确顺序启动。

```python
from mapgraph.lifecycle import launch_services
from typing import Protocol

class BaseService(Protocol):
    id: str
    
    @property
    def required(self) -> set[str]: ...
    
    async def preparing(self) -> None: ...
    async def blocking(self) -> None: ...
    async def cleanup(self) -> None: ...

class DatabaseService:
    id = "database"
    required = set()
    
    async def preparing(self):
        print("🔌 连接数据库...")
    
    async def blocking(self):
        print("📊 数据库服务运行中...")
        # 保持服务运行
    
    async def cleanup(self):
        print("🔌 断开数据库连接")

class APIService:
    id = "api"
    required = {"database"}  # 依赖数据库服务
    
    async def preparing(self):
        print("🚀 启动API服务...")
    
    async def blocking(self):
        print("🌐 API服务运行中...")
    
    async def cleanup(self):
        print("🛑 关闭API服务")

# 自动编排启动
services = [DatabaseService(), APIService()]
await launch_services(services)
```

### 🎛️ 状态管理

Mapgraph 集成了强大的 [statv](https://github.com/GraiaProject/statv) 响应式状态管理库，提供类型安全的状态管理和事件驱动的编程模式。

#### 基础概念

```python
from mapgraph.statv import Statv, Stats, stats

# 创建状态定义
user_count_stat = stats("user_count", default=0)
is_connected_stat = stats("is_connected", default=False)

# 定义状态容器类
class AppState(Statv):
    user_count: Stats[int] = user_count_stat
    is_connected: Stats[bool] = is_connected_stat

# 创建状态实例
app_state = AppState()
print(app_state.user_count)  # 0
print(app_state.is_connected)  # False
```

#### 状态定义方式

```python
# 1. 使用默认值
user_count = stats("user_count", default=100)

# 2. 使用工厂函数
session_data = stats("session", default_factory=lambda: {})

# 3. 无默认值（需要在初始化时提供）
api_key = stats("api_key")

class MyState(Statv):
    user_count: Stats[int] = user_count
    session_data: Stats[dict] = session_data
    api_key: Stats[str] = api_key

# 使用无默认值的状态需要初始化参数
state = MyState(init_stats={"api_key": "sk-xxx"})
```

#### 状态更新与监听

```python
class ServerState(Statv):
    user_count: Stats[int] = stats("user_count", default=0)
    is_online: Stats[bool] = stats("is_online", default=False)

server_state = ServerState()

# 单个状态更新
server_state.user_count = 50
server_state.is_online = True

# 批量状态更新（原子操作）
server_state.update_multi({
    ServerState.user_count: 100,
    ServerState.is_online: True
})

# 监听状态变化
@server_state.on_update(ServerState.user_count)
def on_user_count_change(statv_instance, stats_field, old_value, new_value):
    print(f"用户数量从 {old_value} 变为 {new_value}")

# 触发监听器
server_state.user_count = 150  # 输出: 用户数量从 100 变为 150
```

#### 状态验证器

```python
class GameState(Statv):
    player_health: Stats[int] = stats("health", default=100)
    player_level: Stats[int] = stats("level", default=1)

# 添加验证器 - 限制生命值范围
@GameState.player_health.validator
def validate_health(stats_field, old_value, new_value):
    # 确保生命值在 0-100 之间
    return max(0, min(new_value, 100))

game_state = GameState()

# 验证器会自动应用
game_state.player_health = 150  # 实际设置为 100
game_state.player_health = -10  # 实际设置为 0

print(game_state.player_health)  # 0
```

#### 异步状态等待

```python
import asyncio

class ConnectionState(Statv):
    is_connected: Stats[bool] = stats("connected", default=False)
    
    @property
    def available(self) -> bool:
        """定义可用性条件"""
        return self.is_connected

async def wait_for_connection():
    conn_state = ConnectionState()
    
    # 在后台等待连接
    wait_task = asyncio.create_task(conn_state.wait_for_available())
    
    # 模拟连接过程
    await asyncio.sleep(1)
    conn_state.is_connected = True
    
    # 等待完成
    await wait_task
    print("连接已建立！")

# 运行异步示例
asyncio.run(wait_for_connection())
```

#### 复杂状态管理示例

```python
class ApplicationState(Statv):
    # 用户相关状态
    user_count: Stats[int] = stats("user_count", default=0)
    active_users: Stats[list] = stats("active_users", default_factory=list)
    
    # 系统状态
    is_healthy: Stats[bool] = stats("is_healthy", default=True)
    cpu_usage: Stats[float] = stats("cpu_usage", default=0.0)
    memory_usage: Stats[float] = stats("memory_usage", default=0.0)
    
    # 配置状态
    max_connections: Stats[int] = stats("max_connections", default=1000)

# 添加复合验证器
@ApplicationState.cpu_usage.validator
def validate_cpu_usage(stats_field, old_value, new_value):
    return max(0.0, min(new_value, 100.0))

@ApplicationState.memory_usage.validator  
def validate_memory_usage(stats_field, old_value, new_value):
    return max(0.0, min(new_value, 100.0))

app_state = ApplicationState()

# 监听系统健康状态
@app_state.on_update(ApplicationState.cpu_usage)
@app_state.on_update(ApplicationState.memory_usage)
def check_system_health(statv_instance, stats_field, old_value, new_value):
    # 当CPU或内存使用率过高时标记为不健康
    if statv_instance.cpu_usage > 80 or statv_instance.memory_usage > 90:
        statv_instance.is_healthy = False
    else:
        statv_instance.is_healthy = True

# 批量更新系统指标
app_state.update_multi({
    ApplicationState.cpu_usage: 85.5,
    ApplicationState.memory_usage: 92.3,
    ApplicationState.user_count: 500
})

print(f"系统健康状态: {app_state.is_healthy}")  # False
```

#### 与依赖注入集成

```python
from typing import NewType
from mapgraph import InstanceOf, GLOBAL_INSTANCE_CONTEXT

# 定义状态类型
AppStateType = NewType("AppStateType", ApplicationState)

class MonitoringService:
    """监控服务，依赖注入状态管理"""
    app_state: ApplicationState = InstanceOf(AppStateType, is_key=True)
    
    def start_monitoring(self):
        # 监听关键指标
        @self.app_state.on_update(ApplicationState.is_healthy)
        def on_health_change(statv, stats, old, new):
            if not new:
                self.send_alert("系统健康状态异常！")
    
    def send_alert(self, message: str):
        print(f"🚨 警报: {message}")

# 注册状态实例
app_state = ApplicationState()
GLOBAL_INSTANCE_CONTEXT.store({AppStateType: app_state})

# 使用监控服务
monitor = MonitoringService()
monitor.start_monitoring()

# 触发警报
app_state.cpu_usage = 95  # 🚨 警报: 系统健康状态异常！
```

#### 状态持久化

```python
import json
from pathlib import Path

class PersistentState(Statv):
    user_preferences: Stats[dict] = stats("preferences", default_factory=dict)
    session_data: Stats[dict] = stats("session", default_factory=dict)
    
    def save_to_file(self, filepath: str):
        """保存状态到文件"""
        state_data = {
            "preferences": self.user_preferences,
            "session": self.session_data
        }
        Path(filepath).write_text(json.dumps(state_data, indent=2))
    
    def load_from_file(self, filepath: str):
        """从文件加载状态"""
        if Path(filepath).exists():
            data = json.loads(Path(filepath).read_text())
            self.update_multi({
                PersistentState.user_preferences: data.get("preferences", {}),
                PersistentState.session_data: data.get("session", {})
            })

# 使用持久化状态
persistent_state = PersistentState()
persistent_state.user_preferences = {"theme": "dark", "language": "zh-CN"}
persistent_state.save_to_file("app_state.json")

# 重新加载
new_state = PersistentState()
new_state.load_from_file("app_state.json")
print(new_state.user_preferences)  # {"theme": "dark", "language": "zh-CN"}
```

#### 最佳实践

```python
# ✅ 推荐：使用描述性的状态名称
user_login_status = stats("user_login_status", default=False)
api_request_count = stats("api_request_count", default=0)

# ✅ 推荐：合理组织状态结构
class UserState(Statv):
    is_logged_in: Stats[bool] = stats("logged_in", default=False)
    username: Stats[str] = stats("username", default="")
    permissions: Stats[list] = stats("permissions", default_factory=list)

class SystemState(Statv):
    uptime: Stats[float] = stats("uptime", default=0.0)
    request_count: Stats[int] = stats("requests", default=0)

# ✅ 推荐：使用验证器确保数据完整性
@UserState.permissions.validator
def validate_permissions(stats, old, new):
    # 确保权限列表只包含有效权限
    valid_permissions = {"read", "write", "admin"}
    return [p for p in new if p in valid_permissions]

# ✅ 推荐：合理使用批量更新
def login_user(user_state: UserState, username: str, permissions: list):
    user_state.update_multi({
        UserState.is_logged_in: True,
        UserState.username: username,
        UserState.permissions: permissions
    })
```

## 🛠️ 实战示例

### Web API 服务

```python
from typing import NewType
from httpx import AsyncClient
from mapgraph import InstanceOf, GLOBAL_INSTANCE_CONTEXT, load_env

# 配置类型
API_KEY = NewType("API_KEY", str)
BASE_URL = NewType("BASE_URL", str)
TIMEOUT = NewType("TIMEOUT", int)

# 加载配置
load_env(
    envs=(API_KEY, BASE_URL),
    envs_kv={TIMEOUT: 30},
    dotenv_path=".env"
)

class HTTPService:
    """HTTP 客户端服务"""
    client: AsyncClient = InstanceOf(AsyncClient)
    timeout: int = InstanceOf(TIMEOUT, is_key=True)
    
    async def get(self, url: str):
        return await self.client.get(url, timeout=self.timeout)

class OpenAIService:
    """OpenAI API 服务"""
    api_key: str = InstanceOf(API_KEY, is_key=True)
    base_url: str = InstanceOf(BASE_URL, is_key=True)
    http: HTTPService = HTTPService()
    
    async def chat_completion(self, messages: list):
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = await self.http.client.post(
            f"{self.base_url}/chat/completions",
            json={"model": "gpt-3.5-turbo", "messages": messages},
            headers=headers
        )
        return response.json()

# 注册依赖
GLOBAL_INSTANCE_CONTEXT.store(AsyncClient())

# 使用服务
openai_service = OpenAIService()
result = await openai_service.chat_completion([
    {"role": "user", "content": "Hello!"}
])
```

### 微服务架构

```python
class ConfigService:
    id = "config"
    required = set()
    
    def __init__(self):
        self.config = {}
    
    async def preparing(self):
        # 加载配置
        self.config = load_config()

class DatabaseService:
    id = "database"
    required = {"config"}
    
    config: ConfigService = InstanceOf(ConfigService)
    
    async def preparing(self):
        db_url = self.config.config["database_url"]
        # 连接数据库

class CacheService:
    id = "cache"
    required = {"config"}
    
    async def preparing(self):
        # 连接Redis

class APIService:
    id = "api"
    required = {"database", "cache"}
    
    database: DatabaseService = InstanceOf(DatabaseService)
    cache: CacheService = InstanceOf(CacheService)
    
    async def blocking(self):
        # 启动Web服务器
        pass

# 服务将按依赖顺序启动: config -> database,cache -> api
services = [APIService(), DatabaseService(), CacheService(), ConfigService()]
await launch_services(services)
```

## 🎨 最佳实践

### 1. 类型定义规范

```python
# ✅ 推荐：使用描述性的类型名称
DATABASE_URL = NewType("DATABASE_URL", str)
API_TIMEOUT = NewType("API_TIMEOUT", int)
REDIS_CONFIG = NewType("REDIS_CONFIG", dict)

# ❌ 避免：通用类型名称
URL = NewType("URL", str)  # 太通用
TIMEOUT = NewType("TIMEOUT", int)  # 不够具体
```

### 2. 配置组织

```python
# ✅ 推荐：按功能模块组织配置
class DatabaseConfig:
    url: str = InstanceOf(DATABASE_URL, is_key=True)
    pool_size: int = InstanceOf(DATABASE_POOL_SIZE, is_key=True)

class RedisConfig:
    url: str = InstanceOf(REDIS_URL, is_key=True)
    max_connections: int = InstanceOf(REDIS_MAX_CONNECTIONS, is_key=True)

class AppConfig:
    database = DatabaseConfig()
    redis = RedisConfig()
```

### 3. 服务设计

```python
# ✅ 推荐：单一职责原则
class UserService:
    """用户相关业务逻辑"""
    database: DatabaseService = InstanceOf(DatabaseService)
    
    async def get_user(self, user_id: int):
        return await self.database.fetch_user(user_id)

class AuthService:
    """认证相关业务逻辑"""
    user_service: UserService = InstanceOf(UserService)
    
    async def authenticate(self, token: str):
        # 认证逻辑
        pass
```

## 🤝 贡献指南

我们欢迎所有形式的贡献！

1. **Fork** 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启 **Pull Request**

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- 感谢 [statv](https://github.com/GraiaProject/statv) 提供状态管理支持
- 感谢所有贡献者的辛勤工作

---

<div align="center">

**如果这个项目对您有帮助，请给我们一个 ⭐️**

[报告问题](https://github.com/LaciaProject/mapgraph/issues) • [功能请求](https://github.com/LaciaProject/mapgraph/issues) • [讨论](https://github.com/LaciaProject/mapgraph/discussions)

</div>
