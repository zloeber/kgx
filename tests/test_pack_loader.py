from pathlib import Path

from kgx.core.pack.loader import load_pack_directory

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_load_minimal_pack_counts_entities():
    pack = load_pack_directory(FIXTURE)
    assert len(pack.entities) >= 1
    assert pack.manifest.name == "fixture-minimal"
