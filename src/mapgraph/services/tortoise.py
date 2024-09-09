from __future__ import annotations

from launart import Launart, Service
from launart.utilles import any_completed

try:
    from tortoise import Tortoise
except ImportError:
    raise ImportError(
        "dependency 'aiohttp' is required for aiohttp client service\nplease install it or install 'mapgraph[tortoise]'"
    )


class StarletteASGIService(Service):
    id = "database/tortoise"

    def __init__(
        self,
        config: dict,
    ):
        self.config = config
        super().__init__()

    @property
    def required(self):
        return set()

    @property
    def stages(self):
        return {"preparing", "cleanup"}

    async def launch(self, manager: Launart) -> None:
        async with self.stage("preparing"):
            await Tortoise.init(self.config)

        async with self.stage("cleanup"):
            await Tortoise.close_connections()
