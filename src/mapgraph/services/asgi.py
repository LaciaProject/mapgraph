from __future__ import annotations

import asyncio
import logging
import typing
from typing import Any

from launart import Launart, Service
from launart.utilles import any_completed
from loguru import logger

try:
    from uvicorn import Config, Server
except ImportError:
    raise ImportError(
        "dependency 'uvicorn' is required for asgi service\nplease install it or install 'mapgraph[uvicorn]'"
    )


class DispatcherMiddleware:
    def __init__(self, mounts: typing.Dict[str, Any]) -> None:
        self.mounts = mounts

    async def __call__(
        self, scope, receive: typing.Callable, send: typing.Callable
    ) -> None:
        if scope["type"] == "lifespan":
            await self._handle_lifespan(scope, receive, send) # type: ignore
        else:
            for path, app in self.mounts.items():
                if scope["path"].startswith(path):
                    scope["path"] = scope["path"][len(path) :] or "/"
                    return await app(scope, receive, send)

            if scope["type"] == "http":
                await send(
                    {
                        "type": "http.response.start",
                        "status": 404,
                        "headers": [(b"content-length", b"0")],
                    }
                )
                await send({"type": "http.response.body"})
            elif scope["type"] == "websocket":
                await send({"type": "websocket.close"})


async def _empty_asgi_handler(scope, receive, send):
    if scope["type"] == "lifespan":
        while True:
            message = await receive()
            if message["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
                return
            elif message["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    await send(
        {
            "type": "http.response.start",
            "status": 404,
            "headers": [(b"content-length", b"0")],
        }
    )
    await send({"type": "http.response.body"})


class LoguruHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = str(record.levelno)

        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


class WithoutSigHandlerServer(Server):
    def install_signal_handlers(self) -> None:
        pass


class UvicornASGIService(Service):
    id = "asgi.service/uvicorn"

    host: str
    port: int

    def __init__(
        self,
        host: str,
        port: int,
        mounts: dict[str, Any] | None = None,
    ):
        self.host = host
        self.port = port
        self.middleware = DispatcherMiddleware(
            mounts or {"\0\0\0": _empty_asgi_handler}
        )
        super().__init__()

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart) -> None:
        async with self.stage("preparing"):
            self.server = WithoutSigHandlerServer(
                Config(self.middleware, host=self.host, port=self.port, factory=False)
            )

            level = logging.getLevelName(20)  # default level for uvicorn
            logging.basicConfig(handlers=[LoguruHandler()], level=level)
            PATCHES = ["uvicorn.error", "uvicorn.asgi", "uvicorn.access", ""]
            for name in PATCHES:
                target = logging.getLogger(name)
                target.handlers = [LoguruHandler(level=level)]
                target.propagate = False

            serve_task = asyncio.create_task(self.server.serve())

        async with self.stage("blocking"):
            await any_completed(serve_task, manager.status.wait_for_sigexit())

        async with self.stage("cleanup"):
            logger.warning("try to shutdown uvicorn server...")
            self.server.should_exit = True
            await any_completed(serve_task, asyncio.sleep(5))
            if not serve_task.done():
                logger.warning("timeout, force exit uvicorn server...")
