# kgx Knowledge Pack Manager — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a portable, Git-friendly `.kgpack` bundle format, a validating loader, a `kgx` CLI, and a first automated vendor-pack generation path that proves official-docs → pack → local query, without collapsing the product into generic RAG or a monolithic graph platform.

**Architecture:** Packs are immutable vendor cores plus optional overlay manifests; runtime composes resolved views. MVP stores structured entities and edges as JSONL on disk inside the bundle, with a small in-process graph index (no required Neo4j). Embeddings and heavy indexes are generated locally from pack content and never required inside immutable vendor packs. Capabilities are reference-only in manifests for MVP.

**Tech Stack:** Python 3.12+, Typer, Pydantic v2, jsonschema (CLI validation), pytest; optional later: Firecrawl, MCP Python SDK, OCI tooling.

---

## Deprecation note for humans

The Cursor `/write-plan` command is deprecated; prefer invoking the **superpowers writing-plans** skill when you want future plans in this format.

---

## Plan scope and split guidance

This file is the **MVP + architecture foundation** plan (Phases 1–3 from `prompt.md`, through first vendor pack and local query). **Separate follow-on plans** are recommended before implementation work begins on: MCP adapter surface, repo analyzer, OCI registry, and production signing — each is an independent subsystem with its own test matrix and release cadence.

---

## MVP decisions (resolve open questions from spec)

These are locked for MVP to avoid blocking; revisit in a later RFC if product needs change.

| Open question (from spec) | MVP decision |
|----------------------------|--------------|
| Pack serialization | Directory bundle: `manifest.json` + `entities.jsonl` + `relationships.jsonl` + `documents/` + `capabilities.json` + `provenance.json` (Git-friendly, DB-agnostic artifact). |
| Embeddings in pack | **No.** Vendor packs ship without embeddings; local tooling may build a sidecar cache directory ignored from Git. |
| Graph storage | In-process adjacency built from JSONL at load time; optional SQLite index in a **local workspace** only, not part of immutable vendor pack bytes. |
| Vendor doc depth | Selective service-scoped AWS slice (one vertical, e.g. S3 + IAM glossary) for the first real ingestion spike. |
| Pack updates | Semver in `manifest.json`; content-addressed optional `build_id` field. |
| Capabilities | **References only** (MCP server name, tool IDs, skill paths); no executable definitions in pack. |
| Trust ranking | `provenance.json` uses enumerated `source_tier`: `vendor_official`, `vendor_generated`, `community`, `internal_overlay`. |
| Repo analyzer | **Phase 2 plan** — not in this MVP execution sequence. |

---

## File structure (create vs modify)

Greenfield repo: all paths below are **create** unless noted.

| Path | Responsibility |
|------|----------------|
| `pyproject.toml` | Package metadata, ruff/pytest, entrypoint `kgx = kgx.cli.main:app` |
| `src/kgx/__init__.py` | Version export |
| `src/kgx/cli/main.py` | Typer app: `validate`, `inspect`, `pack build` (stub), `query` (stub) |
| `src/kgx/core/pack/model.py` | Pydantic models mirroring `manifest.json` and bundle layout |
| `src/kgx/core/pack/loader.py` | Load bundle from path, parse JSONL streams, basic integrity checks |
| `src/kgx/core/pack/validator.py` | Validate directory against `schemas/kgpack-manifest.schema.json` |
| `src/kgx/core/graph/memory.py` | Build in-memory adjacency + simple BFS/depth-limited traversal API |
| `src/kgx/core/search/keyword.py` | Minimal keyword search over document filenames + entity `label` fields |
| `src/kgx/providers/base.py` | `Protocol` for providers (`fetch_sources`, `normalize`, `emit_pack`) |
| `src/kgx/providers/aws/__init__.py` | AWS provider package |
| `src/kgx/providers/aws/prototype.py` | MVP: map normalized records → pack JSONL (starts with fixture-driven data) |
| `schemas/kgpack-manifest.schema.json` | JSON Schema for `manifest.json` |
| `schemas/kgpack-entity.schema.json` | JSON Schema for each JSONL line in `entities.jsonl` |
| `schemas/kgpack-relationship.schema.json` | JSON Schema for each JSONL line in `relationships.jsonl` |
| `docs/pack-spec.md` | Human-readable spec; normative machine definitions live in `schemas/` |
| `examples/fixtures/minimal.kgpack/` | Tiny valid pack directory for tests |
| `tests/test_pack_loader.py` | Loader + model tests |
| `tests/test_validator.py` | jsonschema validation tests |
| `tests/test_graph_memory.py` | Traversal invariants |
| `tests/test_cli.py` | Typer CLI smoke tests using Click/Typer runner |

---

### Task 1: Repository and Python packaging bootstrap

**Files:**

- Create: `pyproject.toml`
- Create: `src/kgx/__init__.py`
- Create: `tests/conftest.py` (empty or shared fixtures later)

- [ ] **Step 1: Write failing import test**

Create `tests/test_bootstrap.py`:

```python
def test_package_version_defined():
    import kgx

    assert hasattr(kgx, "__version__")
    assert isinstance(kgx.__version__, str)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/zacharyloeber/Zach-Projects/Personal/active/kgx && python -m pytest tests/test_bootstrap.py -v`

Expected: `ModuleNotFoundError: No module named 'kgx'` or failure on missing `__version__`.

- [ ] **Step 3: Add minimal package metadata and version**

Create `pyproject.toml` with `[project]`, `requires-python >=3.12`, dependencies `typer`, `pydantic`, `jsonschema`, dev `pytest`, `ruff`, and `[tool.setuptools.packages.find] where = ["src"]`.

Create `src/kgx/__init__.py`:

```python
__version__ = "0.1.0"
```

- [ ] **Step 4: Install editable and run tests**

Run:

```bash
cd /Users/zacharyloeber/Zach-Projects/Personal/active/kgx
python -m pip install -e ".[dev]"
python -m pytest tests/test_bootstrap.py -v
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml src/kgx/__init__.py tests/test_bootstrap.py
git commit -m "chore: bootstrap kgx Python package with version"
```

---

### Task 2: Normative pack specification (`docs/pack-spec.md` + JSON Schemas)

**Files:**

- Create: `docs/pack-spec.md`
- Create: `schemas/kgpack-manifest.schema.json`
- Create: `schemas/kgpack-entity.schema.json`
- Create: `schemas/kgpack-relationship.schema.json`

- [ ] **Step 1: Write failing schema validation test**

Create `tests/test_validator.py`:

```python
import json
from pathlib import Path

import jsonschema
import pytest

ROOT = Path(__file__).resolve().parents[1]


def test_manifest_schema_is_valid_json_schema():
    schema_path = ROOT / "schemas" / "kgpack-manifest.schema.json"
    assert schema_path.exists()
    schema = json.loads(schema_path.read_text())
    jsonschema.Draft202012Validator.check_schema(schema)
```

- [ ] **Step 2: Run test — expect fail**

Run: `python -m pytest tests/test_validator.py::test_manifest_schema_is_valid_json_schema -v`

Expected: assertion failure (file missing).

- [ ] **Step 3: Author schemas and human spec**

`docs/pack-spec.md` must document at minimum:

- Required top-level files in a pack directory.
- `manifest.json` fields: `name`, `version`, `kind` (`vendor_core` \| `overlay` \| `workload`), `pack_id` (stable URI), `dependencies` (list of `pack_id@version` strings), `documents_root` defaulting to `documents/`.
- JSONL conventions: one JSON object per line UTF-8; line order not semantically meaningful except for deterministic export tooling.
- Immutability rule: `vendor_core` packs MUST NOT embed secrets; capabilities are references only.

Author `schemas/kgpack-manifest.schema.json` (Draft 2020-12) with required: `name`, `version`, `kind`, `pack_id`, `created_at` (ISO-8601 string). Optional: `dependencies` array of strings matching `^[^:]+:.+@[0-9]+\.[0-9]+\.[0-9]+$` (adjust regex to your chosen ID format; document the format in `pack-spec.md`).

Author `kgpack-entity.schema.json` with required: `id`, `type`, `label`, optional `aliases`, `metadata` object.

Author `kgpack-relationship.schema.json` with required: `id`, `from_id`, `to_id`, `type`, optional `metadata`.

- [ ] **Step 4: Run schema self-check test**

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add docs/pack-spec.md schemas/*.json tests/test_validator.py
git commit -m "docs: add kgpack manifest and JSONL schemas"
```

---

### Task 3: Pydantic models and pack loader

**Files:**

- Create: `src/kgx/core/pack/model.py`
- Create: `src/kgx/core/pack/loader.py`
- Create: `src/kgx/core/pack/validator.py`
- Create: `examples/fixtures/minimal.kgpack/manifest.json`
- Create: `examples/fixtures/minimal.kgpack/entities.jsonl`
- Create: `examples/fixtures/minimal.kgpack/relationships.jsonl`
- Create: `examples/fixtures/minimal.kgpack/documents/README.md`
- Create: `examples/fixtures/minimal.kgpack/capabilities.json`
- Create: `examples/fixtures/minimal.kgpack/provenance.json`
- Test: `tests/test_pack_loader.py`

- [ ] **Step 1: Write failing loader test**

```python
from pathlib import Path

import pytest

from kgx.core.pack.loader import load_pack_directory

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_load_minimal_pack_counts_entities():
    pack = load_pack_directory(FIXTURE)
    assert len(pack.entities) >= 1
    assert pack.manifest.name == "fixture-minimal"
```

Run: `python -m pytest tests/test_pack_loader.py::test_load_minimal_pack_counts_entities -v`

Expected: import or runtime failure until implemented.

- [ ] **Step 2: Implement models and loader**

`model.py`: Pydantic models `Manifest`, `EntityRecord`, `RelationshipRecord`, `ProvenanceFile`, `CapabilitiesFile`, and aggregate `LoadedPack`.

`loader.py`: `load_pack_directory(path: Path) -> LoadedPack` — read manifest, stream-parse JSONL with line-level JSON errors wrapped as `ValueError` including line number, load optional JSON files with defaults.

`validator.py`: function `validate_pack_directory(path: Path) -> None` raising `jsonschema.ValidationError` on invalid manifest.

Fixture `minimal.kgpack` must pass both Pydantic parse and jsonschema manifest validation.

- [ ] **Step 3: Run loader tests**

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add src/kgx/core/pack examples/fixtures/minimal.kgpack tests/test_pack_loader.py
git commit -m "feat: load kgpack directories with manifest and JSONL"
```

---

### Task 4: In-memory graph traversal API

**Files:**

- Create: `src/kgx/core/graph/memory.py`
- Test: `tests/test_graph_memory.py`

- [ ] **Step 1: Write failing graph test**

```python
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
```

- [ ] **Step 2: Implement `MemoryGraph`**

Build adjacency dict from `relationships`; expose `neighbors(entity_id)`, `traverse(start_id, max_depth, rel_type_filter=None)` returning visited nodes with depth metadata.

- [ ] **Step 3: Run tests**

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add src/kgx/core/graph/memory.py tests/test_graph_memory.py
git commit -m "feat: add in-memory graph traversal over loaded packs"
```

---

### Task 5: Keyword search MVP

**Files:**

- Create: `src/kgx/core/search/keyword.py`
- Test: `tests/test_keyword_search.py`

- [ ] **Step 1: Write failing search test**

```python
from pathlib import Path

from kgx.core.pack.loader import load_pack_directory
from kgx.core.search.keyword import keyword_search

FIXTURE = Path(__file__).resolve().parents[1] / "examples" / "fixtures" / "minimal.kgpack"


def test_keyword_search_finds_document():
    pack = load_pack_directory(FIXTURE)
    hits = keyword_search(pack, "README")
    assert any(h.kind == "document" for h in hits)
```

- [ ] **Step 2: Implement `keyword_search`**

Return simple dataclass hits over entity labels/types and document filenames/slugs; case-insensitive substring match is sufficient for MVP.

- [ ] **Step 3: Run tests**

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add src/kgx/core/search/keyword.py tests/test_keyword_search.py
git commit -m "feat: add keyword search over pack documents and entities"
```

---

### Task 6: Typer CLI (`validate`, `inspect`, `query`)

**Files:**

- Create: `src/kgx/cli/main.py`
- Test: `tests/test_cli.py`

- [ ] **Step 1: Write failing CLI test**

```python
from typer.testing import CliRunner

from kgx.cli.main import app

runner = CliRunner()


def test_validate_help():
    result = runner.invoke(app, ["validate", "--help"])
    assert result.exit_code == 0
```

Wire `pyproject.toml` script entrypoint to `kgx.cli.main:app` (Typer callable).

- [ ] **Step 2: Implement commands**

- `kgx validate PATH` — calls `validate_pack_directory` then attempts `load_pack_directory`; prints concise OK or raises non-zero exit with error message.
- `kgx inspect PATH` — prints manifest summary JSON to stdout (pydantic `model_dump_json`).
- `kgx query PATH Q` — runs `keyword_search` and prints TSV or JSON lines.

- [ ] **Step 3: Run tests and manual smoke**

```bash
python -m pytest tests/test_cli.py -v
python -m kgx.cli.main validate examples/fixtures/minimal.kgpack
```

(Adjust invocation to installed console script `kgx` once entrypoint works.)

Expected: tests PASS; validate returns 0 on fixture.

- [ ] **Step 4: Commit**

```bash
git add src/kgx/cli/main.py pyproject.toml tests/test_cli.py
git commit -m "feat: add kgx CLI for validate, inspect, and query"
```

---

### Task 7: Provider protocol + AWS prototype (fixture-driven first)

**Files:**

- Create: `src/kgx/providers/base.py`
- Create: `src/kgx/providers/aws/prototype.py`
- Test: `tests/test_aws_prototype_emit.py`

- [ ] **Step 1: Write failing emit test**

```python
from pathlib import Path

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
```

- [ ] **Step 2: Implement `emit_pack_from_records`**

Write deterministic JSONL ordering (sort by `id`), write `documents/` markdown files derived from `body_md`, populate `provenance.json` with `vendor_official` tier for fixture path (real crawler will supply real URLs per record).

- [ ] **Step 3: Run tests**

Expected: PASS.

- [ ] **Step 4: Commit**

```bash
git add src/kgx/providers tests/test_aws_prototype_emit.py
git commit -m "feat: add provider protocol and AWS pack emitter prototype"
```

---

### Task 8: Ingestion feasibility spike (AWS documentation)

**Files:**

- Create: `scripts/aws_docs_spike.py` (or `src/kgx/providers/aws/ingest_spike.py`)
- Create: `docs/runbooks/aws-ingestion-spike.md` (operational notes for humans; keep short)

This task validates the architectural proof point from `prompt.md`: **automatic generation from official documentation**.

- [ ] **Step 1: Choose one official entrypoint**

Example: AWS documentation sitemap or product landing for S3 (document the exact base URL in `docs/runbooks/aws-ingestion-spike.md`).

- [ ] **Step 2: Implement a read-only spike script**

Script should: fetch a bounded list of pages (respect robots/terms), normalize to `records[]` shape consumed by `emit_pack_from_records`, emit pack to `build/aws-core.kgpack/` (gitignored), run `kgx validate` on output.

Do not commit large generated corpora; commit only the script and runbook.

- [ ] **Step 3: Manual verification**

Run script locally; confirm `kgx validate` passes and `kgx query` returns sensible hits for known terms.

- [ ] **Step 4: Commit**

```bash
git add scripts/aws_docs_spike.py docs/runbooks/aws-ingestion-spike.md .gitignore
git commit -m "chore: add AWS documentation ingestion spike"
```

---

## Deferred subsystems (separate plans)

Implement only after MVP proof passes; each needs its own plan file to satisfy the writing-plans granularity rules without bloating this document.

1. **MCP adapter** — expose `validate`, `inspect`, `query`, and later `resolve` over MCP; security review for path arguments.
2. **Pack resolver / composition** — semver constraints, overlay merge rules, conflict diagnostics.
3. **Repo analyzer** — AST and manifest scanners producing recommended `dependencies` list.
4. **Registry / OCI** — push/pull, signing, provenance envelopes.

---

## Self-review checklist (completed by plan author)

**Spec coverage (from `prompt.md`):**

| Requirement area | Covered by |
|------------------|------------|
| Pack format + portability | Tasks 2–3 |
| Composition/versioning (design) | MVP decisions + deferred resolver plan |
| Semantic search | Task 5 (keyword MVP); embeddings deferred per decision table |
| Graph traversal | Task 4 |
| Capability registration | Schema + `capabilities.json` in fixture; execution deferred |
| CLI | Task 6 |
| MCP / API mode | Deferred plan |
| Repo analysis | Deferred plan |
| Vendor ingestion | Tasks 7–8 |

**Placeholder scan:** No `TBD` steps; open questions resolved in decision table or explicitly deferred with named follow-on plans.

**Type consistency:** Loader returns `LoadedPack`; graph and search consume that type; provider emit writes on-disk layout validated by same loader path.

---

## Execution handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-14-kgx-knowledge-packs-mvp.md`.

**1. Subagent-driven (recommended)** — Fresh subagent per task, review between tasks, fast iteration. **Required sub-skill:** superpowers:subagent-driven-development.

**2. Inline execution** — Execute tasks in this session using executing-plans with batch checkpoints. **Required sub-skill:** superpowers:executing-plans.

**Which approach do you want?**
