from __future__ import annotations

from pathlib import Path


def resolve_pack_directory(pack_path: str, *, cwd: Path | None = None) -> Path:
    """Resolve *pack_path* to an existing directory.

    Relative paths are resolved against *cwd* (default: process ``cwd``).
    ``~`` is expanded. Raises ``ValueError`` if the path is not a readable directory.
    """
    base = cwd if cwd is not None else Path.cwd()
    raw = Path(pack_path.strip()).expanduser()
    resolved = (raw if raw.is_absolute() else (base / raw)).resolve(strict=False)
    if not resolved.is_dir():
        msg = f"Pack path is not a directory or does not exist: {resolved}"
        raise ValueError(msg)
    return resolved
