from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import pandas as pd

from app.config import AppConfig, diagnostics_csv_path, ensure_directories, processed_csv_path, processed_json_path
from app.extractors import EXTRACTORS
from app.models import ExtractionResult, SourceDescriptor
from app.utils import compact_whitespace, infer_source_type, normalize_record_id, serialize_metadata


def discover_sources(paths: Iterable[str]) -> list[SourceDescriptor]:
    sources: list[SourceDescriptor] = []
    for value in paths:
        location = str(value)
        path_obj = Path(location)
        source_type = infer_source_type(location)
        source_name = path_obj.stem if path_obj.suffix else location.rstrip("/").split("/")[-1]
        sources.append(SourceDescriptor(location=location, source_type=source_type, source_name=source_name))
    return sources


def extract_from_sources(sources: Iterable[SourceDescriptor], config: AppConfig | None = None) -> ExtractionResult:
    run_config = config or AppConfig()
    merged = ExtractionResult()

    for source in sources:
        extractor = EXTRACTORS[source.source_type]
        result = extractor.extract(source, run_config)
        merged.records.extend(result.records)
        merged.issues.extend(result.issues)

    return merged


def normalize_records(result: ExtractionResult) -> tuple[pd.DataFrame, pd.DataFrame]:
    normalized_rows = []
    diagnostics_rows = []

    for record in result.records:
        normalized_rows.append(
            {
                "record_id": normalize_record_id(record.source_name, record.source_type, record.record_index),
                "source_name": record.source_name,
                "source_type": record.source_type,
                "source_location": record.source_location,
                "title": compact_whitespace(record.title),
                "content": compact_whitespace(record.content),
                "normalized_text": compact_whitespace(f"{record.title}. {record.content}"),
                "metadata_json": serialize_metadata(record.metadata),
            }
        )

    for issue in result.issues:
        diagnostics_rows.append(asdict(issue))

    records_df = pd.DataFrame(normalized_rows)
    diagnostics_df = pd.DataFrame(diagnostics_rows)

    if not records_df.empty:
        records_df = records_df.drop_duplicates(subset=["normalized_text", "source_location"]).reset_index(drop=True)

    return records_df, diagnostics_df


def export_results(records_df: pd.DataFrame, diagnostics_df: pd.DataFrame, stem: str) -> dict[str, Path]:
    ensure_directories()
    csv_path = processed_csv_path(stem)
    json_path = processed_json_path(stem)
    issues_path = diagnostics_csv_path(stem)

    records_df.to_csv(csv_path, index=False)
    records_df.to_json(json_path, orient="records", indent=2, force_ascii=True)
    diagnostics_df.to_csv(issues_path, index=False)

    return {"csv": csv_path, "json": json_path, "diagnostics": issues_path}


def run_pipeline(paths: Iterable[str], stem: str) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Path]]:
    sources = discover_sources(paths)
    extracted = extract_from_sources(sources)
    records_df, diagnostics_df = normalize_records(extracted)
    exports = export_results(records_df, diagnostics_df, stem)
    return records_df, diagnostics_df, exports


def build_summary(records_df: pd.DataFrame, diagnostics_df: pd.DataFrame) -> dict[str, object]:
    by_source = records_df.groupby("source_type").size().to_dict() if not records_df.empty else {}
    severities = diagnostics_df.groupby("severity").size().to_dict() if not diagnostics_df.empty else {}
    return {
        "record_count": int(len(records_df)),
        "issue_count": int(len(diagnostics_df)),
        "records_by_source_type": by_source,
        "issues_by_severity": severities,
    }


def summary_to_json(summary: dict[str, object]) -> str:
    return json.dumps(summary, indent=2, sort_keys=True)
