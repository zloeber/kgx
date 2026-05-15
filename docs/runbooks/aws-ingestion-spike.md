# AWS documentation ingestion spike

Manual spike proving we can pull a **small, bounded** slice of official AWS documentation HTML, normalize it into `records[]`, and emit a valid `kgx` directory pack.

## Official entrypoint

Use this single documented starting URL (Amazon S3 User Guide on AWS Documentation):

https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html

The spike script fetches this page plus up to **two** additional same-guide pages discovered from `href` links on that page, limited to `docs.aws.amazon.com` paths under `/AmazonS3/latest/userguide/`.

## Prerequisites

- Python **3.12+** (matches `kgx` `requires-python`).
- Repository dependencies installed (e.g. `pip install -e '.[dev]'` from the repo root) so `jsonschema` and other `kgx` imports resolve. The script also prepends `src/` to `sys.path` so it can run without an editable install in many cases.

## Run

From the repository root (the directory that contains `src/` and `scripts/`):

```bash
python scripts/aws_docs_spike.py
```

## Rate limiting and respect

- The script sets **`User-Agent: kgx-spike/0.1`** on every request.
- It performs **at most three** GETs total, with a short pause (~0.6s) between the second and third request.
- Follow [AWS Site Terms](https://aws.amazon.com/terms/) and site policies; this spike is for local experimentation only—not a crawler. If a request fails, the script logs a warning and continues when possible; a failed entrypoint aborts with a non-zero exit.

## Output

Generated pack directory (not committed; `build/` is gitignored):

`build/aws-core.kgpack/`

After writing the pack, the script runs `validate_pack_directory` and `load_pack_directory` and prints `OK` with an entity count, or raises with a clear error.

## Manual verification

With network access, run the command above and confirm:

1. `build/aws-core.kgpack/manifest.json` exists.
2. `build/aws-core.kgpack/documents/` contains one `.md` file per ingested page.
3. Console ends with `OK: wrote ...`.

If you are offline or AWS returns errors, expect stderr warnings or a non-zero exit on entrypoint failure.
