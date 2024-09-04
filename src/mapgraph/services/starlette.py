from __future__ import annotations

from contextlib import suppress

from launart import Launart, Service
from launart.utilles import any_completed

from .asgi import UvicornASGIService

try:
    from starlette.applications import Starlette
except ImportError:
    raise ImportError(
        "dependency 'aiohttp' is required for aiohttp client service\nplease install it or install 'mapgraph[starlette]'"
    )


class StarletteASGIService(Service):
    id = "asgi.service/starlette"

    def __init__(
        self,
        app: Starlette,
    ):
        self.app = app
        super().__init__()

    @property
    def required(self):
        return set({UvicornASGIService.id})

    @property
    def stages(self):
        return {"preparing", "blocking", "cleanup"}

    async def launch(self, manager: Launart) -> None:
        async with self.stage("preparing"):
            asgi_service = manager.get_component(UvicornASGIService)
            asgi_service.middleware.mounts[""] = self.app

        async with self.stage("blocking"):
            await any_completed(manager.status.wait_for_sigexit())

        async with self.stage("cleanup"):
            with suppress(KeyError):
                del asgi_service.middleware.mounts[""]
