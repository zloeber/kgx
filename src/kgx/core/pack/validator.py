from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

import jsonschema


def _find_repo_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "schemas" / "kgpack-manifest.schema.json"
        if candidate.is_file():
            return parent
    msg = "Could not locate schemas/ directory containing kgpack-manifest.schema.json"
    raise FileNotFoundError(msg)


@lru_cache(maxsize=1)
def _manifest_schema() -> dict:
    path = _find_repo_root() / "schemas" / "kgpack-manifest.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _entity_schema() -> dict:
    path = _find_repo_root() / "schemas" / "kgpack-entity.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _relationship_schema() -> dict:
    path = _find_repo_root() / "schemas" / "kgpack-relationship.schema.json"
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _manifest_validator() -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(_manifest_schema())


@lru_cache(maxsize=1)
def _entity_validator() -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(_entity_schema())


@lru_cache(maxsize=1)
def _relationship_validator() -> jsonschema.Draft202012Validator:
    return jsonschema.Draft202012Validator(_relationship_schema())


def validate_pack_directory(path: Path) -> None:
    """Validate ``manifest.json`` against ``kgpack-manifest.schema.json``."""
    root = Path(path)
    if not root.is_dir():
        raise NotADirectoryError(f"not a directory: {root}")
    manifest_path = root / "manifest.json"
    if not manifest_path.is_file():
        raise FileNotFoundError(f"missing manifest.json under {root}")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    _manifest_validator().validate(data)


def validate_entity_json(data: object) -> None:
    _entity_validator().validate(data)


def validate_relationship_json(data: object) -> None:
    _relationship_validator().validate(data)
