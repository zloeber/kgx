from __future__ import annotations

from pathlib import Path
from typing import Any

from kgx.providers.aws.prototype import emit_pack_from_records


def _infer_label(markdown: str, fallback: str) -> str:
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            return stripped.lstrip("#").strip() or fallback
    return fallback


def _entity_id_for_relative_path(rel_posix: str) -> str:
    """Stable id from export-relative path (POSIX, forward slashes)."""
    stem = rel_posix
    if stem.lower().endswith(".md"):
        stem = stem[:-3]
    # Avoid empty ids
    safe = stem.replace("/", ".").replace("\\", ".").strip(".")
    if not safe:
        safe = "untitled"
    return f"confluence.export:{safe}"


def scan_confluence_markdown_export(export_root: Path) -> list[dict[str, Any]]:
    """Turn a directory tree of Markdown files into provider records.

    Intended for output laid down by external tools such as
    `confluence-markdown-exporter` (``cme``). Hidden path segments (e.g.
    ``.obsidian``) are skipped.
    """
    root = export_root.resolve()
    if not root.is_dir():
        msg = f"Export root is not a directory: {root}"
        raise ValueError(msg)

    records: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*.md")):
        try:
            rel = path.relative_to(root).as_posix()
        except ValueError:
            continue
        if any(part.startswith(".") for part in path.relative_to(root).parts):
            continue
        text = path.read_text(encoding="utf-8")
        label = _infer_label(text, path.stem)
        eid = _entity_id_for_relative_path(rel)
        records.append(
            {
                "id": eid,
                "type": "confluence.page",
                "label": label,
                "body_md": text,
                "metadata": {
                    "source_system": "confluence",
                    "export_relative_path": rel,
                },
            }
        )
    return records


def emit_confluence_pack_from_export_dir(
    out_dir: Path,
    export_root: Path,
    *,
    pack_name: str = "confluence-export",
    pack_version: str = "0.1.0",
    pack_id: str = "https://kgx.dev/packs/confluence-export",
) -> None:
    """Build a pack from an on-disk Markdown export (overlay, internal provenance)."""
    records = scan_confluence_markdown_export(export_root)
    emit_pack_from_records(
        out_dir,
        records,
        pack_name=pack_name,
        pack_version=pack_version,
        pack_kind="overlay",
        pack_id=pack_id,
        provenance_sources=[
            {
                "source_tier": "internal_overlay",
                "uri": "https://www.atlassian.com/software/confluence",
            }
        ],
    )
