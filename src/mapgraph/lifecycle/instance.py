from __future__ import annotations

import asyncio
import signal
from typing import Iterable, Optional

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


def show_to_mermaid(components: Iterable[BaseService]):
    components = get_all_services(components)
    graph = build_dependency_graph(components)
    return to_mermaid(graph)


def resolve_requirements(
    components: Iterable[BaseService], reverse: bool = False
) -> list[set[BaseService]]:
    resolved_id: set[str] = set()
    unresolved: set[BaseService] = set(components)
    result: list[set[BaseService]] = []
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


def get_all_services(components: Iterable[BaseService]) -> set[BaseService]:
    services: set[BaseService] = set()
    stack = list(components)

    while stack:
        component = stack.pop()
        if component not in services:
            services.add(component)
            if hasattr(component, "get_service"):
                stack.extend(component.get_service())

    return services


async def worker(context, components, stop_event):
    tasks = []

    try:
        with context.scope():
            for layer in resolve_requirements(components):
                await asyncio.gather(*(component.preparing() for component in layer))
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


async def launch_services(
    components: Iterable[BaseService],
    signals: Iterable[signal.Signals] = (signal.SIGINT, signal.SIGTERM),
):
    components = get_all_services(components)

    context = InstanceContext()
    context.store({ServiceID(component.id): component for component in components})

    resolve_requirements(components)

    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    def signal_handler():
        stop_event.set()

    for sig in signals:
        loop.add_signal_handler(sig, signal_handler)

    await worker(context, components, stop_event)


def launch_services_sync(components: Iterable[BaseService]):
    components = get_all_services(components)

    context = InstanceContext()
    context.store({ServiceID(component.id): component for component in components})

    resolve_requirements(components)

    stop_event = asyncio.Event()

    asyncio.create_task(worker(context, components, stop_event))

    return stop_event
