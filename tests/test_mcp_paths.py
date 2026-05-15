from __future__ import annotations

from pathlib import Path

import pytest

from kgx.mcp.paths import resolve_pack_directory


def test_resolve_pack_directory_absolute(tmp_path: Path) -> None:
    pack = tmp_path / "my.kgpack"
    pack.mkdir()
    got = resolve_pack_directory(str(pack))
    assert got == pack.resolve()


def test_resolve_pack_directory_relative(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    pack = tmp_path / "p"
    pack.mkdir()
    got = resolve_pack_directory("p")
    assert got == pack.resolve()


def test_resolve_pack_directory_missing(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not a directory"):
        resolve_pack_directory(str(tmp_path / "nope"))
