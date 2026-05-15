import json
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_schema_is_valid_json_schema():
    schema_path = ROOT / "schemas" / "kgpack-manifest.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)


def test_entity_schema_is_valid_json_schema():
    schema_path = ROOT / "schemas" / "kgpack-entity.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)


def test_relationship_schema_is_valid_json_schema():
    schema_path = ROOT / "schemas" / "kgpack-relationship.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
