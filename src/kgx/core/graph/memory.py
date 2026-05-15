from __future__ import annotations

from collections import defaultdict, deque
from typing import Any

from kgx.core.pack.model import LoadedPack


class MemoryGraph:
    """Undirected adjacency over pack relationships for neighbor and traversal queries."""

    def __init__(self, adjacency: dict[str, list[tuple[str, str]]]) -> None:
        self._adj = adjacency

    @classmethod
    def from_pack(cls, pack: LoadedPack) -> MemoryGraph:
        adj: dict[str, list[tuple[str, str]]] = defaultdict(list)
        for rel in pack.relationships:
            adj[rel.from_id].append((rel.to_id, rel.type))
            adj[rel.to_id].append((rel.from_id, rel.type))
        return cls(dict(adj))

    def neighbors(self, entity_id: str) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for nbr, _ in self._adj.get(entity_id, []):
            if nbr not in seen:
                seen.add(nbr)
                out.append(nbr)
        out.sort()
        return out

    def traverse(
        self,
        start_id: str,
        max_depth: int,
        rel_type_filter: str | None = None,
    ) -> list[dict[str, Any]]:
        """Breadth-first traversal up to ``max_depth`` hops from ``start_id``.

        ``depth`` is hop count: the start node is 0, its neighbors are 1, etc.
        When ``rel_type_filter`` is set, only edges whose relationship type
        matches are followed.
        """
        if max_depth < 0:
            return []

        result: list[dict[str, Any]] = [{"id": start_id, "depth": 0}]
        if max_depth == 0:
            return result

        q: deque[tuple[str, int]] = deque([(start_id, 0)])
        visited: set[str] = {start_id}

        while q:
            cur, depth = q.popleft()
            if depth >= max_depth:
                continue
            next_depth = depth + 1
            for nbr, rtype in self._adj.get(cur, []):
                if rel_type_filter is not None and rtype != rel_type_filter:
                    continue
                if nbr in visited:
                    continue
                visited.add(nbr)
                result.append({"id": nbr, "depth": next_depth})
                if next_depth < max_depth:
                    q.append((nbr, next_depth))

        return result
