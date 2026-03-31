from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
RAW_SOURCES_DIR = RAW_DIR / "sources"
PROCESSED_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
TEMP_UPLOADS_DIR = PROJECT_ROOT / "temp_uploads"

DEFAULT_OUTPUT_STEM = os.getenv("OUTPUT_STEM", "multi_source_training_corpus")
TEXT_CHUNK_SIZE = int(os.getenv("TEXT_CHUNK_SIZE", "1200"))
TEXT_CHUNK_OVERLAP = int(os.getenv("TEXT_CHUNK_OVERLAP", "150"))


@dataclass(frozen=True)
class AppConfig:
    output_stem: str = DEFAULT_OUTPUT_STEM
    chunk_size: int = TEXT_CHUNK_SIZE
    chunk_overlap: int = TEXT_CHUNK_OVERLAP


def ensure_directories() -> None:
    for path in [RAW_DIR, RAW_SOURCES_DIR, PROCESSED_DIR, EXPORTS_DIR, TEMP_UPLOADS_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def processed_csv_path(stem: str = DEFAULT_OUTPUT_STEM) -> Path:
    return PROCESSED_DIR / f"{stem}.csv"


def processed_json_path(stem: str = DEFAULT_OUTPUT_STEM) -> Path:
    return PROCESSED_DIR / f"{stem}.json"


def diagnostics_csv_path(stem: str = DEFAULT_OUTPUT_STEM) -> Path:
    return EXPORTS_DIR / f"{stem}_diagnostics.csv"
