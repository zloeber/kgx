from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from kgx.cli.main import app
from kgx.core.pack.editor import PackEditor

runner = CliRunner()
FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_pack_init_and_entity_add(tmp_path: Path) -> None:
    out = tmp_path / "new.kgpack"
    result = runner.invoke(
        app,
        [
            "pack",
            "init",
            str(out),
            "--name",
            "cli-pack",
            "--pack-id",
            "https://example.invalid/packs/cli",
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    result = runner.invoke(
        app,
        [
            "pack",
            "entity",
            "add",
            str(out),
            "--id",
            "x1",
            "--type",
            "note",
            "--label",
            "Note",
            "--body",
            "# Hi",
        ],
    )
    assert result.exit_code == 0, result.stdout + result.stderr
    editor = PackEditor.open(out)
    assert editor.get_entity("x1") is not None
    assert editor.read_entity_document("x1") == "# Hi"


def test_pack_list_fixture() -> None:
    result = runner.invoke(app, ["pack", "list", str(FIXTURE)])
    assert result.exit_code == 0
    assert "entity\t" in result.stdout
