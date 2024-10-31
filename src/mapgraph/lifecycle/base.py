from __future__ import annotations

from typing import Protocol, NewType, TypedDict, Literal


class BaseService(Protocol):
    id: str
    required: set[str]

    async def preparing(self) -> None: ...

    async def blocking(self) -> None: ...

    async def cleanup(self) -> None: ...


ServiceID = NewType("ServiceID", str)
