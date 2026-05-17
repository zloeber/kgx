from __future__ import annotations

import json
from pathlib import Path

from kgx.mcp.server import kgx_inspect_manifest, kgx_query_pack, kgx_validate_pack

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_mcp_validate_fixture() -> None:
    out = kgx_validate_pack(str(FIXTURE))
    assert json.loads(out)["ok"] is True


def test_mcp_inspect_fixture() -> None:
    out = kgx_inspect_manifest(str(FIXTURE))
    assert "fixture-minimal" in out


def test_mcp_query_fixture() -> None:
    out = kgx_query_pack(str(FIXTURE), "README")
    assert "document" in out


def test_mcp_entity_upsert_roundtrip(tmp_path) -> None:
    from kgx.mcp.server import kgx_pack_entity_upsert

    out = tmp_path / "mcp-edit.kgpack"
    from kgx.core.pack.editor import PackEditor

    PackEditor.create_empty(
        out,
        name="mcp",
        pack_id="https://example.invalid/packs/mcp",
    )
    result = kgx_pack_entity_upsert(
        str(out),
        entity_id="mcp.test",
        type="test",
        label="MCP",
        body_md="# MCP\n",
    )
    assert json.loads(result)["ok"] is True
    editor = PackEditor.open(out)
    assert editor.read_entity_document("mcp.test") == "# MCP\n"
