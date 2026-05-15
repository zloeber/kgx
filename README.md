# kgx

**kgx** is a small toolkit for **portable knowledge packs**: directory bundles (`manifest.json`, `entities.jsonl`, `relationships.jsonl`, `documents/`, …) you can validate, inspect, and search locally, then wire into agents via an optional **MCP** server.

For the full product intent and roadmap, see [`prompt.md`](prompt.md). The on-disk format is summarized in [`docs/pack-spec.md`](docs/pack-spec.md).

## Requirements

- **Python** 3.12 or newer  
- Optional: **[mise](https://mise.jdx.dev)** (pinned runtimes and CLI binaries) and **[Task](https://taskfile.dev)** (project tasks)

## Quick start (mise)

```bash
mise install          # python, task, ruff (see mise.toml)
mise trust            # if mise asks to trust this repo’s config
task install          # creates .venv and: pip install -e '.[dev]'
task test
```

`task` targets use **`.venv/bin/python`** so you get a consistent interpreter and pytest/ruff from the dev extra. The `ruff` entry in `mise.toml` is optional for running Ruff outside the project venv (for example `mise exec -- ruff check …`).

## Common commands

| Goal | Command |
|------|--------|
| Run tests | `task test` |
| Lint | `task lint` |
| Format | `task format` |
| Validate example pack | `task validate-fixture` |
| CLI help | `kgx --help` |
| MCP server (stdio) | `kgx-mcp` or `python -m kgx.mcp` |
| AWS docs spike (network) | `task spike` — see [`docs/runbooks/aws-ingestion-spike.md`](docs/runbooks/aws-ingestion-spike.md) |
| Confluence export → pack | `task confluence-pack EXPORT_DIR=...` — see [`docs/runbooks/confluence-export-to-pack.md`](docs/runbooks/confluence-export-to-pack.md) |

## Layout

- `src/kgx/` — library, Typer CLI, MCP server, pack loader, search, providers  
- `schemas/` — JSON Schema for manifests and JSONL rows  
- `examples/fixtures/` — minimal valid pack for tests  
- `scripts/` — standalone spikes (not part of the importable package)  
- `docs/plans/` — feature design notes  
- `docs/runbooks/` — operator steps (exports, ingestion)
