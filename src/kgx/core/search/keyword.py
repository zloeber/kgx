from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from kgx.core.pack.model import LoadedPack


def _document_paths_for_search(pack: LoadedPack) -> list[Path]:
    if pack.document_paths:
        return pack.document_paths
    root_name = pack.manifest.documents_root or "documents/"
    doc_dir = (pack.root / root_name).resolve()
    if not doc_dir.is_dir():
        return []
    pack_root = pack.root.resolve()
    return sorted(
        p.relative_to(pack_root)
        for p in doc_dir.rglob("*")
        if p.is_file()
    )


@dataclass(frozen=True)
class SearchHit:
    """A single keyword match against pack documents or entities."""

    kind: str
    document_path: Path | None = None
    entity_id: str | None = None


def keyword_search(pack: LoadedPack, query: str) -> list[SearchHit]:
    """Case-insensitive substring search over document paths and entity fields."""
    needle = query.strip().lower()
    if not needle:
        return []

    hits: list[SearchHit] = []

    for rel in _document_paths_for_search(pack):
        if needle in str(rel).lower():
            hits.append(SearchHit(kind="document", document_path=rel))

    for ent in pack.entities:
        if (
            needle in ent.id.lower()
            or needle in ent.type.lower()
            or needle in ent.label.lower()
        ):
            hits.append(SearchHit(kind="entity", entity_id=ent.id))

    return hits
