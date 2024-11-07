from __future__ import annotations

from typing import Protocol, NewType


class BaseService(Protocol):
    id: str

    @property
    def required(self) -> set[str]: ...

    async def preparing(self) -> None: ...

    async def blocking(self) -> None: ...

    async def cleanup(self) -> None: ...

    def get_service(self) -> set[BaseService]: ...


ServiceID = NewType("ServiceID", str)
