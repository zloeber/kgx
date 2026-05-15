# KG Pack format specification

Normative machine definitions for the portable KG Pack bundle live under `schemas/` in this repository. This document summarizes the on-disk layout, `manifest.json` fields, JSONL record shape, and normative constraints for tooling and authors.

## Required top-level layout

A valid pack **directory** (a `.kgpack` bundle is this directory, possibly archived) MUST contain at least the following paths relative to the pack root:

| Path | Description |
|------|-------------|
| `manifest.json` | Pack metadata; MUST conform to `schemas/kgpack-manifest.schema.json`. |
| `entities.jsonl` | One entity record per line; each line MUST conform to `schemas/kgpack-entity.schema.json`. |
| `relationships.jsonl` | One relationship record per line; each line MUST conform to `schemas/kgpack-relationship.schema.json`. |
| `documents/` | Document payload root. MAY be empty; filenames and subdirectory layout are product-specific. |

MVP bundles in this repository MAY also include `capabilities.json`, `provenance.json`, and other auxiliary files as described in the implementation plan; validators that only understand the core graph MAY ignore unknown files unless explicitly scoped to validate them.

## `manifest.json`

The manifest is a single JSON object. Required and optional fields:

| Field | Required | Type / values | Description |
|-------|----------|----------------|-------------|
| `name` | yes | string | Human-readable pack name. |
| `version` | yes | string | Semver `MAJOR.MINOR.PATCH` for the pack contents. |
| `kind` | yes | string | One of `vendor_core`, `overlay`, `workload`. |
| `pack_id` | yes | string (URI) | Stable, globally meaningful identifier for this pack (URI). |
| `created_at` | yes | string (ISO 8601) | Creation timestamp; RFC 3339 / ISO 8601 date-time recommended. |
| `dependencies` | no | array of strings | Upstream packs this pack depends on; see **Dependency strings** below. |
| `documents_root` | no | string | Directory path relative to pack root for document files. If omitted, tooling MUST treat the default as `documents/`. |

### Dependency strings

When `dependencies` is present, each entry MUST be a single string matching:

`^[^:]+:.+@[0-9]+\.[0-9]+\.[0-9]+$`

That is: a non-empty `pack_id` prefix containing at least one colon (typical URI scheme plus authority or path), a non-empty remainder, an `@` separator, and a **strict** three-part numeric semver `MAJOR.MINOR.PATCH` (digits only in each part).

Examples (illustrative):

- `urn:kgx:vendor:aws-s3-iam@1.0.0`
- `https://example.com/packs/foo@2.3.4`

## JSONL conventions

Files `entities.jsonl` and `relationships.jsonl`:

- Encoding: **UTF-8**.
- Each line: exactly one JSON value (object), with no leading or trailing data on that line.
- Blank lines SHOULD NOT appear in interchange; if present, consumers SHOULD reject or strip them consistently (product decision).

Line order is **not** semantically meaningful for graph truth: the same multiset of lines denotes the same entity or relationship set. Deterministic export tooling MAY sort lines (for example by `id`) to produce stable diffs; that ordering MUST NOT be interpreted as priority or causality unless a separate field explicitly encodes such semantics.

## Immutability and `vendor_core`

Packs with `kind: "vendor_core"` are **immutable vendor cores**. Such packs:

- MUST NOT embed secrets (API keys, tokens, passwords, private keys, or other credentials).
- MUST express external integration only as **references** (for example MCP server names, tool identifiers, skill paths, URIs) in auxiliary metadata or companion files such as `capabilities.json`, never as executable definitions or credential material inside the pack bytes.

Overlays (`overlay`) and workload-specific packs (`workload`) MAY attach additional context subject to separate policy; they still SHOULD avoid shipping secrets and SHOULD prefer references for capabilities.
