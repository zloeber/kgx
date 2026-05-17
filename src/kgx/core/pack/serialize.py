from __future__ import annotations

import json
from typing import Any

from kgx.core.pack.model import EntityRecord, RelationshipRecord


def compact_json(obj: dict[str, Any]) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def entity_to_dict(entity: EntityRecord) -> dict[str, Any]:
    data = entity.model_dump(mode="json", exclude_none=True)
    return data


def relationship_to_dict(rel: RelationshipRecord) -> dict[str, Any]:
    return rel.model_dump(mode="json", exclude_none=True)


def entity_jsonl_line(entity: EntityRecord) -> str:
    return compact_json(entity_to_dict(entity))


def relationship_jsonl_line(rel: RelationshipRecord) -> str:
    return compact_json(relationship_to_dict(rel))
