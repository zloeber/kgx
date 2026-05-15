from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from kgx.core.pack.loader import load_pack_directory
from kgx.core.pack.validator import validate_pack_directory
from kgx.core.search.keyword import SearchHit, keyword_search

app = typer.Typer(help="kgx — knowledge pack tooling.", no_args_is_help=True)


def _err(msg: str) -> None:
    print(msg, file=sys.stderr)


def _search_hit_json(hit: SearchHit) -> str:
    return json.dumps(
        {
            "kind": hit.kind,
            "document_path": str(hit.document_path) if hit.document_path is not None else None,
            "entity_id": hit.entity_id,
        },
        ensure_ascii=False,
    )


@app.command()
def validate(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Path to a .kgpack directory",
    ),
) -> None:
    """Validate pack layout and manifest, then load the full pack."""
    try:
        validate_pack_directory(path)
        load_pack_directory(path)
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
    typer.echo(f"OK: validated and loaded {path.resolve()}")


@app.command()
def inspect(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Path to a .kgpack directory",
    ),
) -> None:
    """Print manifest.json as pretty-printed JSON."""
    try:
        pack = load_pack_directory(path)
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
    typer.echo(pack.manifest.model_dump_json(indent=2))


@app.command()
def query(
    path: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=False,
        dir_okay=True,
        readable=True,
        help="Path to a .kgpack directory",
    ),
    q: str = typer.Argument(
        "",
        help="Search string (case-insensitive substring). "
        "If empty or whitespace-only, exits successfully with no output.",
    ),
) -> None:
    """Keyword search over document paths and entity fields; prints one JSON object per line."""
    try:
        pack = load_pack_directory(path)
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
    for hit in keyword_search(pack, q):
        typer.echo(_search_hit_json(hit))
