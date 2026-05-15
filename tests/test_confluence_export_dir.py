from __future__ import annotations

from pathlib import Path

from kgx.core.pack.loader import load_pack_directory
from kgx.providers.confluence.export_dir import (
    emit_confluence_pack_from_export_dir,
    scan_confluence_markdown_export,
)

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "confluence-export-sample"


def test_scan_finds_pages() -> None:
    records = scan_confluence_markdown_export(FIXTURE)
    ids = {r["id"] for r in records}
    assert "confluence.export:README" in ids
    assert "confluence.export:ENG.Runbook" in ids
    assert all(r["type"] == "confluence.page" for r in records)
    runbook = next(r for r in records if r["id"] == "confluence.export:ENG.Runbook")
    assert runbook["metadata"]["export_relative_path"] == "ENG/Runbook.md"
    assert "On-call runbook" in runbook["body_md"]


def test_skips_hidden_path_segments(tmp_path: Path) -> None:
    (tmp_path / "public.md").write_text("# Public", encoding="utf-8")
    hidden = tmp_path / ".obsidian"
    hidden.mkdir()
    (hidden / "note.md").write_text("# Secret", encoding="utf-8")
    records = scan_confluence_markdown_export(tmp_path)
    assert len(records) == 1
    assert records[0]["id"] == "confluence.export:public"


def test_emit_and_load_pack(tmp_path: Path) -> None:
    out = tmp_path / "pack"
    emit_confluence_pack_from_export_dir(out, FIXTURE, pack_name="test-conf", pack_id="https://example.invalid/pack/t")
    pack = load_pack_directory(out)
    assert pack.manifest.kind == "overlay"
    assert pack.manifest.name == "test-conf"
    assert len(pack.entities) >= 2
