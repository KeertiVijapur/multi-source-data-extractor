from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


TITLE_CANDIDATES = ("title", "name", "subject", "headline", "topic")


def compact_whitespace(value: Any) -> str:
    if value is None:
        return ""
    return " ".join(str(value).replace("\x00", " ").split())


def slugify(value: str) -> str:
    text = compact_whitespace(value).lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "source"


def serialize_metadata(metadata: dict[str, Any]) -> str:
    return json.dumps(metadata, ensure_ascii=True, sort_keys=True)


def split_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    clean_text = compact_whitespace(text)
    if not clean_text:
        return []
    if len(clean_text) <= chunk_size:
        return [clean_text]

    chunks: list[str] = []
    start = 0
    while start < len(clean_text):
        end = min(len(clean_text), start + chunk_size)
        chunk = clean_text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(clean_text):
            break
        start = max(end - overlap, start + 1)
    return chunks


def choose_title(metadata: dict[str, Any], fallback: str) -> str:
    for key in TITLE_CANDIDATES:
        value = compact_whitespace(metadata.get(key))
        if value:
            return value
    return compact_whitespace(fallback)


def is_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"}


def infer_source_type(location: str) -> str:
    if is_url(location):
        return "website"

    suffix = Path(location).suffix.lower()
    if suffix == ".pdf":
        return "pdf"
    if suffix == ".csv":
        return "csv"
    if suffix in {".xlsx", ".xls"}:
        return "spreadsheet"
    if suffix in {".db", ".sqlite", ".sqlite3"}:
        return "database"
    if suffix in {".html", ".htm"}:
        return "website"
    raise ValueError(f"Unsupported source type for: {location}")


def normalize_record_id(source_name: str, source_type: str, record_index: int) -> str:
    return f"{slugify(source_name)}__{source_type}__{record_index:04d}"
