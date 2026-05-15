#!/usr/bin/env python3
"""Bounded fetch of AWS S3 User Guide pages → kgpack via emit_pack_from_records."""

from __future__ import annotations

import html as html_module
import re
import sys
import time
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

# Allow `python scripts/aws_docs_spike.py` without an editable install.
_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
_SRC = _REPO_ROOT / "src"
if _SRC.is_dir() and str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from kgx.core.pack.loader import load_pack_directory  # noqa: E402
from kgx.core.pack.validator import validate_pack_directory  # noqa: E402
from kgx.providers.aws.prototype import emit_pack_from_records  # noqa: E402

USER_AGENT = "kgx-spike/0.1"
# Single official entrypoint (S3 User Guide); same-host discovery stays under this prefix.
ENTRYPOINT = "https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html"
S3_USERGUIDE_PREFIX = "/AmazonS3/latest/userguide/"
MAX_PAGES = 3
BODY_TEXT_CAP = 2000
REQUEST_PAUSE_SEC = 0.6


def _slug_id_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "aws.doc.root"
    slug = path.lower().replace("/", ".")
    slug = re.sub(r"[^a-z0-9._-]+", "_", slug)
    return f"aws.doc.{slug}"


def _label_from_url(url: str, title: str | None) -> str:
    if title and title.strip():
        return html_module.unescape(title.strip())
    seg = urlparse(url).path.rstrip("/").split("/")[-1]
    return seg.replace(".html", "").replace("_", " ") or url


class _HrefCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        for k, v in attrs:
            if k.lower() == "href" and v:
                self.hrefs.append(v)
                return


class _TitleAndTextParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: str | None = None
        self._in_title = False
        self._title_buf: list[str] = []
        self._skip_depth = 0
        self._text_buf: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t == "title":
            self._in_title = True
            self._title_buf = []
            return
        if t in ("script", "style", "noscript"):
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t == "title" and self._in_title:
            self._in_title = False
            self.title = "".join(self._title_buf).strip() or None
            return
        if t in ("script", "style", "noscript") and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_buf.append(data)
        elif self._skip_depth == 0:
            self._text_buf.append(data)


def _fetch(url: str) -> tuple[int, bytes]:
    req = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(req, timeout=45) as resp:  # noqa: S310 — spike script, bounded URLs
        code = getattr(resp, "status", 200)
        return int(code), resp.read()


def _normalize_same_guide_link(base_url: str, href: str) -> str | None:
    joined = urljoin(base_url, href)
    p = urlparse(joined)
    if p.scheme not in ("http", "https"):
        return None
    if p.netloc.lower() != "docs.aws.amazon.com":
        return None
    path = p.path or ""
    if not path.startswith(S3_USERGUIDE_PREFIX):
        return None
    # Drop fragments for dedupe / stable fetch target
    return p._replace(fragment="").geturl()


def _discover_extra_urls(landing_url: str, html_bytes: bytes, max_extra: int) -> list[str]:
    text = html_bytes.decode("utf-8", errors="replace")
    collector = _HrefCollector()
    collector.feed(text)
    collector.close()
    seen: set[str] = {landing_url}
    out: list[str] = []
    for href in collector.hrefs:
        norm = _normalize_same_guide_link(landing_url, href)
        if not norm or norm in seen:
            continue
        seen.add(norm)
        out.append(norm)
        if len(out) >= max_extra:
            break
    return out


def _strip_text(parser: _TitleAndTextParser) -> str:
    raw = "".join(parser._text_buf)
    raw = html_module.unescape(raw)
    raw = re.sub(r"\s+", " ", raw).strip()
    return raw


def _body_md(title: str, plain: str) -> str:
    excerpt = plain[:BODY_TEXT_CAP]
    if len(plain) > BODY_TEXT_CAP:
        excerpt += "…"
    lines = [f"# {title}", ""]
    if excerpt:
        lines.append(excerpt)
    return "\n".join(lines) + "\n"


def _page_record(url: str, html_bytes: bytes) -> dict[str, Any]:
    text = html_bytes.decode("utf-8", errors="replace")
    parser = _TitleAndTextParser()
    parser.feed(text)
    parser.close()
    label = _label_from_url(url, parser.title)
    title = label
    plain = _strip_text(parser)
    return {
        "id": _slug_id_from_url(url),
        "type": "aws.doc.page",
        "label": label,
        "body_md": _body_md(title, plain),
        "metadata": {"source_uri": url},
    }


def main() -> int:
    out_dir = _REPO_ROOT / "build" / "aws-core.kgpack"
    urls: list[str] = [ENTRYPOINT]
    try:
        _, first_html = _fetch(ENTRYPOINT)
    except (HTTPError, URLError, TimeoutError, OSError) as e:
        print(f"ERROR: failed to fetch entrypoint {ENTRYPOINT}: {e}", file=sys.stderr)
        return 1

    extra = _discover_extra_urls(ENTRYPOINT, first_html, max_extra=MAX_PAGES - 1)
    urls.extend(extra)

    records: list[dict[str, Any]] = []
    # Landing page (already fetched)
    records.append(_page_record(ENTRYPOINT, first_html))

    for u in extra:
        time.sleep(REQUEST_PAUSE_SEC)
        try:
            _, data = _fetch(u)
        except (HTTPError, URLError, TimeoutError, OSError) as e:
            print(f"WARN: skip {u}: {e}", file=sys.stderr)
            continue
        records.append(_page_record(u, data))

    if not records:
        print("ERROR: no pages ingested", file=sys.stderr)
        return 1

    emit_pack_from_records(out_dir, records)
    validate_pack_directory(out_dir)
    pack = load_pack_directory(out_dir)
    print(f"OK: wrote {out_dir} ({len(pack.entities)} entities)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
