from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _compact_json(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def _document_rel_path(entity_id: str) -> str:
    safe = entity_id.replace("/", "_").replace(":", "_")
    return f"documents/{safe}.md"


def emit_pack_from_records(out_dir: Path, records: list[dict[str, Any]]) -> None:
    """Write a KG pack directory consumable by ``load_pack_directory``.

    Each record should include ``id``, ``type``, and ``label``. Optional ``body_md``
    is written under ``documents/`` and referenced from ``metadata.document``.
    """
    root = Path(out_dir)
    root.mkdir(parents=True, exist_ok=True)
    docs = root / "documents"
    docs.mkdir(parents=True, exist_ok=True)

    sorted_records = sorted(records, key=lambda r: str(r["id"]))

    entity_lines: list[str] = []
    for rec in sorted_records:
        eid = str(rec["id"])
        body_md = rec.get("body_md")
        metadata = dict(rec.get("metadata") or {})
        if isinstance(body_md, str) and body_md.strip():
            rel = _document_rel_path(eid)
            (root / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / rel).write_text(body_md, encoding="utf-8")
            metadata["document"] = rel

        entity: dict[str, Any] = {
            "id": eid,
            "type": str(rec["type"]),
            "label": str(rec["label"]),
        }
        aliases = rec.get("aliases")
        if aliases is not None:
            entity["aliases"] = aliases
        if metadata:
            entity["metadata"] = metadata
        entity_lines.append(_compact_json(entity))

    created = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = {
        "created_at": created,
        "documents_root": "documents/",
        "kind": "vendor_core",
        "name": "aws-core-prototype",
        "pack_id": "https://kgx.dev/packs/aws-core-prototype",
        "version": "0.1.0",
    }
    (root / "manifest.json").write_text(_compact_json(manifest) + "\n", encoding="utf-8")

    (root / "entities.jsonl").write_text("\n".join(entity_lines) + "\n", encoding="utf-8")
    (root / "relationships.jsonl").write_text("", encoding="utf-8")

    provenance = {
        "sources": [
            {
                "source_tier": "vendor_official",
                "uri": "https://docs.aws.amazon.com/",
            }
        ]
    }
    (root / "provenance.json").write_text(_compact_json(provenance) + "\n", encoding="utf-8")

    capabilities = {"mcp_servers": [], "skill_paths": [], "tool_ids": []}
    (root / "capabilities.json").write_text(_compact_json(capabilities) + "\n", encoding="utf-8")
