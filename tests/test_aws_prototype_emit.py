from pathlib import Path

from kgx.core.pack.loader import load_pack_directory
from kgx.core.pack.validator import validate_pack_directory
from kgx.providers.aws.prototype import emit_pack_from_records


def test_emit_creates_manifest(tmp_path: Path):
    records = [
        {
            "id": "aws.s3.bucket",
            "type": "aws.service",
            "label": "Amazon S3",
            "body_md": "# Amazon S3\nObject storage.",
        }
    ]
    out = tmp_path / "aws-core"
    emit_pack_from_records(out, records)
    assert (out / "manifest.json").exists()
    assert (out / "entities.jsonl").read_text().strip()


def test_emit_load_validate(tmp_path: Path):
    records = [
        {
            "id": "aws.s3.bucket",
            "type": "aws.service",
            "label": "Amazon S3",
            "body_md": "# Amazon S3\nObject storage.",
        }
    ]
    out = tmp_path / "aws-core"
    emit_pack_from_records(out, records)
    validate_pack_directory(out)
    pack = load_pack_directory(out)
    assert len(pack.entities) >= 1
