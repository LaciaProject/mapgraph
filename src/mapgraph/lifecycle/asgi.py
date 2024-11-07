from typing import Any, Callable

try:
    from uvicorn import Config, Server
    from uvicorn._types import ASGIApplication

except ImportError:
    raise ImportError(
        "dependency 'uvicorn' is required for asgi service\nplease install it or install 'mapgraph[uvicorn]'"
    )


class UvicornService:
    id = "asgi.service/uvicorn"

    def __init__(
        self,
        app: ASGIApplication | Callable[..., Any] | str,
        host: str,
        port: int,
        **kwargs,
    ):
        self.config = Config(app, host=host, port=port, **kwargs)

    @property
    def required(self):
        return set()

    async def preparing(self) -> None:
        self.server = Server(config=self.config)

    async def blocking(self) -> None:
        await self.server.serve()

    async def cleanup(self) -> None:
        await self.server.shutdown()

    def get_service(self):
        return set()
