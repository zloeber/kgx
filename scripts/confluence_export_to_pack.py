#!/usr/bin/env python3
"""Turn a Confluence Markdown export directory into a kgpack (no Confluence API here)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
_SRC = _REPO_ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from kgx.core.pack.loader import load_pack_directory  # noqa: E402
from kgx.core.pack.validator import validate_pack_directory  # noqa: E402
from kgx.providers.confluence.export_dir import emit_confluence_pack_from_export_dir  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(
        description=(
            "Build a kgpack directory from Markdown files under EXPORT_DIR "
            "(e.g. output of confluence-markdown-exporter)."
        )
    )
    p.add_argument(
        "export_dir",
        type=Path,
        help="Root directory containing exported .md files",
    )
    p.add_argument(
        "-o",
        "--out",
        type=Path,
        default=_REPO_ROOT / "build" / "confluence-export.kgpack",
        help="Output pack directory (default: build/confluence-export.kgpack)",
    )
    p.add_argument("--pack-name", default="confluence-export")
    p.add_argument("--pack-version", default="0.1.0")
    p.add_argument(
        "--pack-id",
        default="https://kgx.dev/packs/confluence-export",
        help="Stable URI for manifest pack_id",
    )
    args = p.parse_args()

    emit_confluence_pack_from_export_dir(
        args.out,
        args.export_dir,
        pack_name=args.pack_name,
        pack_version=args.pack_version,
        pack_id=args.pack_id,
    )
    validate_pack_directory(args.out)
    pack = load_pack_directory(args.out)
    print(
        f"OK: wrote {args.out.resolve()} ({len(pack.entities)} entities)",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
