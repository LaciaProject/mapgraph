from __future__ import annotations

from contextlib import asynccontextmanager
from typing import (
    Protocol,
    NewType,
    TypeVar,
)


T = TypeVar("T")


class BaseService(Protocol):
    id: str

    @property
    def required(self) -> set[str]: ...

    async def preparing(self) -> None: ...

    @asynccontextmanager
    async def blocking(self):
        yield

    async def cleanup(self) -> None: ...

    def get_service(self) -> set[BaseService]: ...


ServiceID = NewType("ServiceID", str)
