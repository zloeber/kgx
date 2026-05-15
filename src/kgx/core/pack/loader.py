from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from kgx.core.pack.model import (
    CapabilitiesFile,
    EntityRecord,
    LoadedPack,
    Manifest,
    ProvenanceFile,
    RelationshipRecord,
)
from kgx.core.pack.validator import (
    validate_entity_json,
    validate_pack_directory,
    validate_relationship_json,
)


def _jsonl_records(
    path: Path,
    *,
    rel_name: str,
    schema_validate: Any,
    model_validate: Any,
) -> list[Any]:
    text = path.read_text(encoding="utf-8")
    out: list[Any] = []
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            raw = json.loads(stripped)
        except json.JSONDecodeError as exc:
            msg = f"{rel_name} line {line_no}: invalid JSON ({exc})"
            raise ValueError(msg) from exc
        try:
            schema_validate(raw)
        except Exception as exc:
            msg = f"{rel_name} line {line_no}: schema validation failed ({exc})"
            raise ValueError(msg) from exc
        out.append(model_validate(raw))
    return out


def _documents_relative_paths(pack_root: Path, manifest: Manifest) -> list[Path]:
    root_name = manifest.documents_root or "documents/"
    doc_dir = (pack_root / root_name).resolve()
    if not doc_dir.is_dir():
        return []
    return sorted(
        p.relative_to(pack_root.resolve())
        for p in doc_dir.rglob("*")
        if p.is_file()
    )


def load_pack_directory(path: Path) -> LoadedPack:
    """Load a pack directory into structured in-memory models."""
    pack_root = Path(path).resolve()
    if not pack_root.is_dir():
        raise NotADirectoryError(f"not a directory: {pack_root}")

    validate_pack_directory(pack_root)

    manifest_data = json.loads((pack_root / "manifest.json").read_text(encoding="utf-8"))
    manifest = Manifest.model_validate(manifest_data)

    entities_path = pack_root / "entities.jsonl"
    relationships_path = pack_root / "relationships.jsonl"
    if not entities_path.is_file():
        raise FileNotFoundError(f"missing entities.jsonl under {pack_root}")
    if not relationships_path.is_file():
        raise FileNotFoundError(f"missing relationships.jsonl under {pack_root}")

    entities = _jsonl_records(
        entities_path,
        rel_name="entities.jsonl",
        schema_validate=validate_entity_json,
        model_validate=EntityRecord.model_validate,
    )
    relationships = _jsonl_records(
        relationships_path,
        rel_name="relationships.jsonl",
        schema_validate=validate_relationship_json,
        model_validate=RelationshipRecord.model_validate,
    )

    prov_path = pack_root / "provenance.json"
    if prov_path.is_file():
        provenance = ProvenanceFile.model_validate(
            json.loads(prov_path.read_text(encoding="utf-8"))
        )
    else:
        provenance = ProvenanceFile()

    cap_path = pack_root / "capabilities.json"
    if cap_path.is_file():
        capabilities = CapabilitiesFile.model_validate(
            json.loads(cap_path.read_text(encoding="utf-8"))
        )
    else:
        capabilities = CapabilitiesFile()

    document_paths = _documents_relative_paths(pack_root, manifest)

    return LoadedPack(
        root=pack_root,
        manifest=manifest,
        entities=entities,
        relationships=relationships,
        provenance=provenance,
        capabilities=capabilities,
        document_paths=document_paths,
    )
