from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Annotated

import typer

from kgx.core.pack.editor import PackEditor
from kgx.core.pack.model import EntityRecord, PackKind, RelationshipRecord

pack_app = typer.Typer(
    help="Create and edit kgpack directories (manifest, entities, relationships, documents).",
    no_args_is_help=True,
)


def _err(msg: str) -> None:
    print(msg, file=sys.stderr)


def _read_body(body: str | None, body_file: Path | None) -> str | None:
    if body_file is not None:
        return body_file.read_text(encoding="utf-8")
    if body is not None:
        if body == "-":
            return sys.stdin.read()
        return body
    return None


@pack_app.command("init")
def pack_init(
    out: Annotated[
        Path,
        typer.Argument(help="New pack directory to create"),
    ],
    name: Annotated[str, typer.Option("--name", help="manifest.name")],
    pack_id: Annotated[str, typer.Option("--pack-id", help="manifest.pack_id (URI)")],
    kind: Annotated[PackKind, typer.Option("--kind")] = "overlay",
    version: Annotated[str, typer.Option("--version")] = "0.1.0",
) -> None:
    """Create an empty valid pack directory."""
    if out.exists() and any(out.iterdir()):
        _err(f"refusing to init non-empty directory: {out}")
        raise typer.Exit(code=1)
    editor = PackEditor.create_empty(
        out,
        name=name,
        pack_id=pack_id,
        kind=kind,
        version=version,
    )
    editor.save()
    typer.echo(f"OK: created pack at {editor.root}")


@pack_app.command("list")
def pack_list(
    path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)],
) -> None:
    """List entity and relationship ids in a pack."""
    try:
        editor = PackEditor.open(path)
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
    for entity in sorted(editor.pack.entities, key=lambda e: e.id):
        typer.echo(f"entity\t{entity.id}\t{entity.type}\t{entity.label}")
    for rel in sorted(editor.pack.relationships, key=lambda r: r.id):
        typer.echo(f"relationship\t{rel.id}\t{rel.type}\t{rel.from_id}\t{rel.to_id}")


entity_app = typer.Typer(help="Add, update, or remove entities.")
pack_app.add_typer(entity_app, name="entity")


@entity_app.command("add")
def entity_add(
    path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)],
    entity_id: Annotated[str, typer.Option("--id", help="Stable entity id")],
    type_: Annotated[str, typer.Option("--type", help="Entity type string")],
    label: Annotated[str, typer.Option("--label")],
    body: Annotated[
        str | None,
        typer.Option("--body", help="Markdown body, or '-' for stdin"),
    ] = None,
    body_file: Annotated[
        Path | None,
        typer.Option("--body-file", exists=True, dir_okay=False, readable=True),
    ] = None,
) -> None:
    """Add or replace an entity (and optional document body)."""
    try:
        editor = PackEditor.open(path)
        body_md = _read_body(body, body_file)
        editor.upsert_entity(
            EntityRecord(id=entity_id, type=type_, label=label),
            body_md=body_md,
        )
        editor.save()
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
    typer.echo(f"OK: upserted entity {entity_id}")


@entity_app.command("rm")
def entity_rm(
    path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)],
    entity_id: Annotated[str, typer.Argument(help="Entity id to remove")],
) -> None:
    """Remove an entity and relationships that reference it."""
    try:
        editor = PackEditor.open(path)
        if not editor.remove_entity(entity_id):
            _err(f"entity not found: {entity_id}")
            raise typer.Exit(code=1)
        editor.save()
    except typer.Exit:
        raise
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
    typer.echo(f"OK: removed entity {entity_id}")


@entity_app.command("show")
def entity_show(
    path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)],
    entity_id: Annotated[str, typer.Argument()],
) -> None:
    """Print entity JSON and document body if present."""
    try:
        editor = PackEditor.open(path)
        entity = editor.get_entity(entity_id)
        if entity is None:
            _err(f"entity not found: {entity_id}")
            raise typer.Exit(code=1)
        typer.echo(entity.model_dump_json(indent=2))
        doc = editor.read_entity_document(entity_id)
        if doc:
            typer.echo("--- document ---")
            typer.echo(doc)
    except typer.Exit:
        raise
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc


rel_app = typer.Typer(help="Add or remove relationships.")
pack_app.add_typer(rel_app, name="relationship")


@rel_app.command("add")
def relationship_add(
    path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)],
    rel_id: Annotated[str, typer.Option("--id", help="Relationship id")],
    from_id: Annotated[str, typer.Option("--from")],
    to_id: Annotated[str, typer.Option("--to")],
    type_: Annotated[str, typer.Option("--type", help="Relationship type")],
) -> None:
    """Add or replace a relationship."""
    try:
        editor = PackEditor.open(path)
        editor.upsert_relationship(
            RelationshipRecord(id=rel_id, from_id=from_id, to_id=to_id, type=type_)
        )
        editor.save()
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
    typer.echo(f"OK: upserted relationship {rel_id}")


@rel_app.command("rm")
def relationship_rm(
    path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)],
    rel_id: Annotated[str, typer.Argument(help="Relationship id to remove")],
) -> None:
    """Remove a relationship by id."""
    try:
        editor = PackEditor.open(path)
        if not editor.remove_relationship(rel_id):
            _err(f"relationship not found: {rel_id}")
            raise typer.Exit(code=1)
        editor.save()
    except typer.Exit:
        raise
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
    typer.echo(f"OK: removed relationship {rel_id}")


manifest_app = typer.Typer(help="Update manifest fields.")
pack_app.add_typer(manifest_app, name="manifest")


@manifest_app.command("set")
def manifest_set(
    path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)],
    name: Annotated[str | None, typer.Option("--name")] = None,
    version: Annotated[str | None, typer.Option("--version")] = None,
    kind: Annotated[PackKind | None, typer.Option("--kind")] = None,
    pack_id: Annotated[str | None, typer.Option("--pack-id")] = None,
) -> None:
    """Update one or more manifest fields, then save."""
    fields = {
        k: v
        for k, v in {
            "name": name,
            "version": version,
            "kind": kind,
            "pack_id": pack_id,
        }.items()
        if v is not None
    }
    if not fields:
        _err("provide at least one of --name, --version, --kind, --pack-id")
        raise typer.Exit(code=1)
    try:
        editor = PackEditor.open(path)
        editor.update_manifest(**fields)
        editor.save()
        typer.echo(json.dumps(editor.pack.manifest.model_dump(mode="json"), indent=2))
    except Exception as exc:
        _err(str(exc))
        raise typer.Exit(code=1) from exc
