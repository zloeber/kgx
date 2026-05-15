from __future__ import annotations

from pathlib import Path
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class KnowledgeProvider(Protocol):
    """Contract for building KG packs from external knowledge sources.

    A *provider* is responsible for discovering raw material, shaping it into
    records compatible with the KG pack model, and writing an on-disk pack tree
    that ``kgx`` can load and validate.

    MVP implementations may leave method bodies as ``...`` or raise
    ``NotImplementedError`` until wired to real upstreams; the protocol documents
    the intended lifecycle: fetch → normalize → emit.
    """

    def fetch_sources(self) -> list[dict[str, Any]]:
        """Pull or synthesize raw source payloads (API responses, crawl pages, etc.)."""
        ...

    def normalize(self, raw: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Transform ``fetch_sources`` output into normalized entity-shaped dicts."""
        ...

    def emit_pack(self, out_dir: Path, records: list[dict[str, Any]]) -> None:
        """Write ``manifest.json``, JSONL, documents, and sidecar JSON under ``out_dir``."""
        ...
