from __future__ import annotations

import asyncio
import signal
from typing import Iterable, List, Set

import networkx as nx

from .base import BaseService, ServiceID
from ..context import InstanceContext


async def any_completed(*waits):
    return await asyncio.wait(
        [i if isinstance(i, asyncio.Task) else asyncio.create_task(i) for i in waits],
        return_when=asyncio.FIRST_COMPLETED,
    )


def build_dependency_graph(services: Iterable[BaseService]) -> nx.DiGraph:
    graph = nx.DiGraph()
    for service in services:
        graph.add_node(service.id)
        for dependency in service.required:
            if isinstance(dependency, str):
                graph.add_edge(dependency, service.id)
            else:
                graph.add_edge(dependency.id, service.id)
    return graph


def to_mermaid(graph: nx.DiGraph) -> str:
    lines = ["graph TD"]
    for source, target in graph.edges():
        lines.append(f"    {source} --> {target}")
    return "\n".join(lines)


def resolve_requirements(
    components: Iterable[BaseService], reverse: bool = False
) -> List[Set[BaseService]]:
    resolved_id: Set[str] = set()
    unresolved: Set[BaseService] = set(components)
    result: List[Set[BaseService]] = []
    while unresolved:
        layer = {
            component for component in unresolved if resolved_id >= component.required
        }

        if layer:
            unresolved -= layer
            resolved_id.update(component.id for component in layer)
            result.append(layer)
        else:
            unresolved_ids = {component.id for component in unresolved}
            raise ValueError(f"Unresolved dependencies: {unresolved_ids}")
    if reverse:
        result.reverse()
    return result


async def launch_services(components: Iterable[BaseService]):
    context = InstanceContext()
    context.store({ServiceID(component.id): component for component in components})

    resolve_requirements(components)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        stop_event.set()

    loop.add_signal_handler(signal.SIGINT, signal_handler)
    loop.add_signal_handler(signal.SIGTERM, signal_handler)

    tasks = []

    try:
        with context.scope():
            for layer in resolve_requirements(components):
                asyncio.gather(*(component.preparing() for component in layer))
            tasks.extend(
                [asyncio.create_task(component.blocking()) for component in components]
            )

        await stop_event.wait()

    except asyncio.CancelledError:
        pass

    finally:
        for task in tasks:
            task.cancel()
        with context.scope():
            for layer in resolve_requirements(components, reverse=True):
                await asyncio.gather(*(component.cleanup() for component in layer))
