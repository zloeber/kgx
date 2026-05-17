from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from kgx.core.pack.editor import PackEditor
from kgx.core.pack.loader import load_pack_directory
from kgx.core.pack.model import EntityRecord, RelationshipRecord

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_roundtrip_save_reload(tmp_path: Path) -> None:
    out = tmp_path / "copy.kgpack"
    shutil.copytree(FIXTURE, out)
    editor = PackEditor.open(out)
    editor.save()
    reloaded = load_pack_directory(out)
    assert reloaded.manifest.name == editor.pack.manifest.name
    assert len(reloaded.entities) == len(editor.pack.entities)


def test_upsert_entity_and_relationship(tmp_path: Path) -> None:
    editor = PackEditor.create_empty(
        tmp_path / "edit",
        name="edit-test",
        pack_id="https://example.invalid/packs/edit-test",
    )
    editor.upsert_entity(
        EntityRecord(id="e1", type="test.node", label="One"),
        body_md="# One\n",
    )
    editor.upsert_relationship(
        RelationshipRecord(id="r1", from_id="e1", to_id="e1", type="self")
    )
    editor.save()
    again = PackEditor.open(tmp_path / "edit")
    assert again.get_entity("e1") is not None
    assert again.read_entity_document("e1") == "# One\n"
    assert len(again.pack.relationships) == 1


def test_remove_entity_cascades_relationships(tmp_path: Path) -> None:
    editor = PackEditor.create_empty(
        tmp_path / "cascade",
        name="cascade",
        pack_id="https://example.invalid/packs/cascade",
    )
    editor.upsert_entity(EntityRecord(id="a", type="t", label="A"))
    editor.upsert_entity(EntityRecord(id="b", type="t", label="B"))
    editor.upsert_relationship(
        RelationshipRecord(id="ab", from_id="a", to_id="b", type="links")
    )
    editor.save()
    editor.remove_entity("a")
    editor.save()
    assert editor.get_entity("a") is None
    assert editor.pack.relationships == []


def test_update_manifest_version(tmp_path: Path) -> None:
    editor = PackEditor.create_empty(
        tmp_path / "ver",
        name="ver",
        pack_id="https://example.invalid/packs/ver",
        version="0.1.0",
    )
    editor.update_manifest(version="0.2.0")
    editor.save()
    assert PackEditor.open(tmp_path / "ver").pack.manifest.version == "0.2.0"


def test_unknown_manifest_field_raises(tmp_path: Path) -> None:
    editor = PackEditor.create_empty(
        tmp_path / "bad",
        name="bad",
        pack_id="https://example.invalid/packs/bad",
    )
    with pytest.raises(ValueError, match="unsupported manifest fields"):
        editor.update_manifest(foo="bar")
