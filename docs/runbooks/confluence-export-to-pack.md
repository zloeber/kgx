# Confluence export → kgpack

`kgx` does **not** call the Confluence API. Use an exporter such as **[confluence-markdown-exporter](https://github.com/Spenhouet/confluence-markdown-exporter)** (`cme`) to produce a directory of Markdown files, then turn that tree into a pack.

## 1. Export from Confluence

Install and authenticate per upstream docs (see [README](https://github.com/Spenhouet/confluence-markdown-exporter) and [documentation site](https://spenhouet.github.io/confluence-markdown-exporter/)).

Example (after `cme config edit auth.confluence`):

```bash
cme pages https://your-site.atlassian.net/wiki/spaces/ENG/pages/123456789/Some-Page
# or a space / org export — see upstream usage
```

Note the **output directory** you configured (`export.output_path` in `cme` config).

## 2. Build the pack

From the **kgx** repository root (directory containing `src/` and `scripts/`):

```bash
python scripts/confluence_export_to_pack.py /path/to/cme/output -o build/confluence-export.kgpack
```

Or with Task:

```bash
task confluence-pack EXPORT_DIR=/path/to/cme/output
```

## 3. Validate and query

```bash
kgx validate build/confluence-export.kgpack
kgx query build/confluence-export.kgpack runbook
```

## Semantics

- Pack **`kind`** is **`overlay`** (organization / internal content).
- **Provenance** uses **`internal_overlay`** with a generic Confluence product URI.
- Each **entity** has `type` **`confluence.page`** and **`metadata.export_relative_path`** for traceability to the export tree.
- **Stable ids** derive from the path relative to the export root (see `scan_confluence_markdown_export`).

## Hygiene

- Do not commit **credentials**; `cme` keeps auth in its own config.
- Treat the export directory as **sensitive** if it contains internal docs; the generated pack inherits that sensitivity.
