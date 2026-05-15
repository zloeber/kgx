from pathlib import Path

from kgx.core.graph.memory import MemoryGraph
from kgx.core.pack.loader import load_pack_directory

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_neighbors_round_trip():
    pack = load_pack_directory(FIXTURE)
    g = MemoryGraph.from_pack(pack)
    some_id = next(iter(pack.entities)).id
    nbrs = g.neighbors(some_id)
    assert isinstance(nbrs, list)
