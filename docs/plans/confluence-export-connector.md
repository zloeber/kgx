# Plan: Confluence export → kgpack connector

## Goal

Let operators use [confluence-markdown-exporter](https://github.com/Spenhouet/confluence-markdown-exporter) (`cme`) to export Confluence to Markdown on disk, then turn that tree into a valid **`kgx` directory pack** without embedding Confluence credentials in `kgx`.

## Principles

- **Separation of concerns:** Auth and Atlassian API access stay outside `kgx` (e.g. `cme` CLI or Docker).
- **Pack contract:** Output matches existing layout (`manifest.json`, JSONL, `documents/`) and validates with `kgx validate`.
- **Provenance:** Enterprise Confluence content is modeled as **`internal_overlay`** (not `vendor_official`).
- **Stable IDs:** Entity ids derive from paths **relative to the export root** so re-exports produce the same ids when layout is unchanged.

## Phases

| Phase | Scope | Status |
|-------|--------|--------|
| **A** | `emit_pack_from_records` optional manifest + provenance overrides; `scan` + `emit` from a markdown tree; tests + runbook + script | **This PR** |
| **B** | Optional YAML frontmatter (title, Confluence URL) if present in `cme` output | Later |
| **C** | Thin wrapper CLI around `cme export` → `kgx` emit (single command, still two processes) | Later |
| **D** | SharePoint / other connectors using the same “staging dir → records → emit” pattern | Later |

## Files (phase A)

- `src/kgx/providers/aws/prototype.py` — extend `emit_pack_from_records(..., **overrides)`
- `src/kgx/providers/confluence/export_dir.py` — scan + `emit_confluence_pack_from_export_dir`
- `scripts/confluence_export_to_pack.py` — argparse entrypoint
- `docs/runbooks/confluence-export-to-pack.md` — prerequisites + `cme` pointers + `kgx` steps
- `examples/fixtures/confluence-export-sample/` — minimal fake export tree for tests
- `tests/test_confluence_export_dir.py`
- `Taskfile.yml` — `confluence-pack` task (optional)

## Acceptance

- `task test` passes; new tests build a pack from the fixture and pass `load_pack_directory`.
- Runbook documents installing/running `cme` and points to upstream docs: [confluence-markdown-exporter](https://github.com/Spenhouet/confluence-markdown-exporter).
