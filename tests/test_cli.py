from pathlib import Path

from typer.testing import CliRunner

from kgx.cli.main import app

runner = CliRunner()

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_validate_help():
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0


def test_validate_minimal_fixture():
    result = runner.invoke(app, ["validate", str(FIXTURE)])
    assert result.exit_code == 0
    assert "OK:" in result.stdout


def test_query_empty_exits_zero_no_lines():
    result = runner.invoke(app, ["query", str(FIXTURE), ""])
    assert result.exit_code == 0
    assert result.stdout.strip() == ""
