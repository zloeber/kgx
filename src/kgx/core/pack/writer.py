from __future__ import annotations

from kgx.core.pack.model import LoadedPack
from kgx.core.pack.serialize import compact_json, entity_jsonl_line, relationship_jsonl_line
from kgx.core.pack.validator import validate_pack_directory


def _documents_root_name(pack: LoadedPack) -> str:
    root = pack.manifest.documents_root or "documents/"
    return root if root.endswith("/") else f"{root}/"


def save_pack_directory(pack: LoadedPack, *, validate: bool = True) -> None:
    """Write a loaded pack back to ``pack.root`` (deterministic JSONL ordering)."""
    root = pack.root.resolve()
    root.mkdir(parents=True, exist_ok=True)

    manifest_data = pack.manifest.model_dump(mode="json", exclude_none=True)
    (root / "manifest.json").write_text(
        compact_json(manifest_data) + "\n",
        encoding="utf-8",
    )

    entities_sorted = sorted(pack.entities, key=lambda e: e.id)
    rels_sorted = sorted(pack.relationships, key=lambda r: r.id)

    entity_lines = [entity_jsonl_line(e) for e in entities_sorted]
    rel_lines = [relationship_jsonl_line(r) for r in rels_sorted]

    (root / "entities.jsonl").write_text(
        ("\n".join(entity_lines) + "\n") if entity_lines else "",
        encoding="utf-8",
    )
    (root / "relationships.jsonl").write_text(
        ("\n".join(rel_lines) + "\n") if rel_lines else "",
        encoding="utf-8",
    )

    (root / "provenance.json").write_text(
        compact_json(pack.provenance.model_dump(mode="json", exclude_none=True)) + "\n",
        encoding="utf-8",
    )
    (root / "capabilities.json").write_text(
        compact_json(pack.capabilities.model_dump(mode="json", exclude_none=True)) + "\n",
        encoding="utf-8",
    )

    doc_root = root / _documents_root_name(pack).rstrip("/")
    doc_root.mkdir(parents=True, exist_ok=True)

    if validate:
        validate_pack_directory(root)


def default_document_rel_path(entity_id: str, documents_root: str = "documents/") -> str:
    """Relative path for an entity's markdown document inside the pack."""
    prefix = documents_root if documents_root.endswith("/") else f"{documents_root}/"
    safe = entity_id.replace("/", "_").replace(":", "_")
    return f"{prefix}{safe}.md"
