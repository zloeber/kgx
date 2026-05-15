from pathlib import Path

from kgx.core.pack.loader import load_pack_directory
from kgx.core.search.keyword import keyword_search

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_keyword_search_finds_document():
    pack = load_pack_directory(FIXTURE)
    hits = keyword_search(pack, "README")
    assert any(h.kind == "document" for h in hits)
