from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from kgx.core.pack.loader import load_pack_directory
from kgx.core.pack.validator import validate_pack_directory
from kgx.core.search.keyword import SearchHit, keyword_search
from kgx.mcp.paths import resolve_pack_directory

mcp = FastMCP(
    "kgx",
    instructions=(
        "kgx knowledge-pack tools. Each tool takes a pack_path pointing at a directory "
        "bundle (manifest.json, entities.jsonl, …). Prefer absolute paths."
    ),
)


def _hit_dict(hit: SearchHit) -> dict:
    return {
        "kind": hit.kind,
        "document_path": str(hit.document_path) if hit.document_path is not None else None,
        "entity_id": hit.entity_id,
    }


@mcp.tool(name="kgx_validate_pack")
def kgx_validate_pack(pack_path: str) -> str:
    """Validate manifest.json against the kgpack schema, then load entities and relationships."""
    path = resolve_pack_directory(pack_path)
    validate_pack_directory(path)
    load_pack_directory(path)
    return json.dumps({"ok": True, "resolved_path": str(path)}, ensure_ascii=False)


@mcp.tool(name="kgx_inspect_manifest")
def kgx_inspect_manifest(pack_path: str) -> str:
    """Return the pack manifest as formatted JSON."""
    path = resolve_pack_directory(pack_path)
    pack = load_pack_directory(path)
    return pack.manifest.model_dump_json(indent=2)


@mcp.tool(name="kgx_query_pack")
def kgx_query_pack(pack_path: str, query: str) -> str:
    """Keyword search over document paths and entity id/type/label; returns JSON array of hits."""
    path = resolve_pack_directory(pack_path)
    pack = load_pack_directory(path)
    hits = [_hit_dict(h) for h in keyword_search(pack, query)]
    return json.dumps(hits, ensure_ascii=False, indent=2)


def main() -> None:
    """Console entrypoint for ``kgx-mcp`` (stdio transport)."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
