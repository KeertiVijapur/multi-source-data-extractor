from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests
from bs4 import BeautifulSoup
from pypdf import PdfReader

from app.config import AppConfig
from app.models import ExtractedRecord, ExtractionIssue, ExtractionResult, SourceDescriptor
from app.utils import choose_title, compact_whitespace, split_text


class BaseExtractor:
    source_type = "base"

    def extract(self, source: SourceDescriptor, config: AppConfig) -> ExtractionResult:
        raise NotImplementedError


class WebsiteExtractor(BaseExtractor):
    source_type = "website"

    def extract(self, source: SourceDescriptor, config: AppConfig) -> ExtractionResult:
        result = ExtractionResult()
        try:
            html = self._load_html(source.location)
            soup = BeautifulSoup(html, "html.parser")
            page_title = compact_whitespace(soup.title.string if soup.title else source.source_name)

            paragraphs = [compact_whitespace(node.get_text(" ", strip=True)) for node in soup.find_all(["p", "li"])]
            headings = [compact_whitespace(node.get_text(" ", strip=True)) for node in soup.find_all(["h1", "h2", "h3"])]
            meta_description = ""
            description_node = soup.find("meta", attrs={"name": "description"})
            if description_node:
                meta_description = compact_whitespace(description_node.get("content"))

            page_text = " ".join(part for part in [page_title, meta_description, *headings, *paragraphs] if part)
            for index, chunk in enumerate(split_text(page_text, config.chunk_size, config.chunk_overlap), start=1):
                result.records.append(
                    ExtractedRecord(
                        source_name=source.source_name,
                        source_type=source.source_type,
                        source_location=source.location,
                        record_index=index,
                        title=page_title or source.source_name,
                        content=chunk,
                        metadata={
                            "kind": "page_chunk",
                            "headings": headings,
                            "meta_description": meta_description,
                        },
                    )
                )

            table_offset = len(result.records)
            for table_idx, table_rows in enumerate(self._parse_tables(soup), start=1):
                for row_idx, row in enumerate(table_rows, start=1):
                    title = choose_title(row, f"{page_title} table {table_idx} row {row_idx}")
                    result.records.append(
                        ExtractedRecord(
                            source_name=source.source_name,
                            source_type=source.source_type,
                            source_location=source.location,
                            record_index=table_offset + table_idx * 100 + row_idx,
                            title=title,
                            content=" | ".join(
                                f"{column}: {compact_whitespace(value)}" for column, value in row.items() if compact_whitespace(value)
                            ),
                            metadata={
                                "kind": "table_row",
                                "table_index": table_idx,
                                "row_number": row_idx,
                                "fields": row,
                            },
                        )
                    )
        except Exception as exc:
            result.issues.append(
                ExtractionIssue(
                    source_name=source.source_name,
                    source_type=source.source_type,
                    source_location=source.location,
                    severity="error",
                    message=f"Failed to parse website: {exc}",
                )
            )
        if not result.records:
            result.issues.append(
                ExtractionIssue(
                    source_name=source.source_name,
                    source_type=source.source_type,
                    source_location=source.location,
                    severity="warning",
                    message="Website produced no extractable records.",
                )
            )
        return result

    def _load_html(self, location: str) -> str:
        if location.startswith(("http://", "https://")):
            response = requests.get(location, timeout=20)
            response.raise_for_status()
            return response.text
        return Path(location).read_text(encoding="utf-8")

    def _parse_tables(self, soup: BeautifulSoup) -> list[list[dict[str, str]]]:
        parsed_tables: list[list[dict[str, str]]] = []
        for table in soup.find_all("table"):
            headers = [compact_whitespace(cell.get_text(" ", strip=True)) for cell in table.find_all("th")]
            rows: list[dict[str, str]] = []
            for row_number, tr in enumerate(table.find_all("tr"), start=1):
                cells = [compact_whitespace(cell.get_text(" ", strip=True)) for cell in tr.find_all(["td", "th"])]
                if not cells:
                    continue
                if headers and cells == headers:
                    continue
                row_headers = headers or [f"column_{index}" for index in range(1, len(cells) + 1)]
                rows.append(dict(zip(row_headers, cells)))
            if rows:
                parsed_tables.append(rows)
        return parsed_tables


class PdfExtractor(BaseExtractor):
    source_type = "pdf"

    def extract(self, source: SourceDescriptor, config: AppConfig) -> ExtractionResult:
        result = ExtractionResult()
        try:
            reader = PdfReader(source.location)
            for page_number, page in enumerate(reader.pages, start=1):
                page_text = compact_whitespace(page.extract_text() or "")
                if not page_text:
                    result.issues.append(
                        ExtractionIssue(
                            source_name=source.source_name,
                            source_type=source.source_type,
                            source_location=source.location,
                            severity="warning",
                            message=f"No text detected on page {page_number}.",
                        )
                    )
                    continue

                for chunk_number, chunk in enumerate(split_text(page_text, config.chunk_size, config.chunk_overlap), start=1):
                    result.records.append(
                        ExtractedRecord(
                            source_name=source.source_name,
                            source_type=source.source_type,
                            source_location=source.location,
                            record_index=(page_number * 100) + chunk_number,
                            title=f"{source.source_name} page {page_number}",
                            content=chunk,
                            metadata={
                                "kind": "pdf_page_chunk",
                                "page_number": page_number,
                                "chunk_number": chunk_number,
                            },
                        )
                    )
        except Exception as exc:
            result.issues.append(
                ExtractionIssue(
                    source_name=source.source_name,
                    source_type=source.source_type,
                    source_location=source.location,
                    severity="error",
                    message=f"Failed to parse PDF: {exc}",
                )
            )
        return result


class TabularExtractor(BaseExtractor):
    source_type = "tabular"

    def _records_from_rows(
        self,
        rows: Iterable[dict[str, object]],
        source: SourceDescriptor,
        context: dict[str, object],
        start_index: int = 1,
    ) -> list[ExtractedRecord]:
        records: list[ExtractedRecord] = []
        for offset, row in enumerate(rows, start=start_index):
            clean_row = {str(column): compact_whitespace(value) for column, value in row.items()}
            non_empty = {key: value for key, value in clean_row.items() if value}
            if not non_empty:
                continue
            title = choose_title(non_empty, f"{source.source_name} row {offset}")
            content = " | ".join(f"{column}: {value}" for column, value in non_empty.items())
            records.append(
                ExtractedRecord(
                    source_name=source.source_name,
                    source_type=source.source_type,
                    source_location=source.location,
                    record_index=offset,
                    title=title,
                    content=content,
                    metadata={**context, "fields": non_empty},
                )
            )
        return records


class CsvExtractor(TabularExtractor):
    source_type = "csv"

    def extract(self, source: SourceDescriptor, config: AppConfig) -> ExtractionResult:
        result = ExtractionResult()
        try:
            frame = pd.read_csv(source.location).fillna("")
            result.records.extend(
                self._records_from_rows(
                    frame.to_dict(orient="records"),
                    source,
                    context={"kind": "csv_row", "columns": frame.columns.tolist()},
                )
            )
        except Exception as exc:
            result.issues.append(
                ExtractionIssue(
                    source_name=source.source_name,
                    source_type=source.source_type,
                    source_location=source.location,
                    severity="error",
                    message=f"Failed to parse CSV: {exc}",
                )
            )
        return result


class SpreadsheetExtractor(TabularExtractor):
    source_type = "spreadsheet"

    def extract(self, source: SourceDescriptor, config: AppConfig) -> ExtractionResult:
        result = ExtractionResult()
        try:
            workbook = pd.ExcelFile(source.location)
            offset = 0
            for sheet_name in workbook.sheet_names:
                frame = workbook.parse(sheet_name=sheet_name).fillna("")
                records = self._records_from_rows(
                    frame.to_dict(orient="records"),
                    source,
                    context={"kind": "spreadsheet_row", "sheet_name": sheet_name, "columns": frame.columns.tolist()},
                    start_index=offset + 1,
                )
                result.records.extend(records)
                offset += len(records)
        except Exception as exc:
            result.issues.append(
                ExtractionIssue(
                    source_name=source.source_name,
                    source_type=source.source_type,
                    source_location=source.location,
                    severity="error",
                    message=f"Failed to parse spreadsheet: {exc}",
                )
            )
        return result


class SQLiteExtractor(TabularExtractor):
    source_type = "database"

    def extract(self, source: SourceDescriptor, config: AppConfig) -> ExtractionResult:
        result = ExtractionResult()
        try:
            connection = sqlite3.connect(source.location)
            try:
                tables = pd.read_sql_query(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name",
                    connection,
                )
                offset = 0
                for table_name in tables["name"].tolist():
                    frame = pd.read_sql_query(f"SELECT * FROM [{table_name}]", connection).fillna("")
                    records = self._records_from_rows(
                        frame.to_dict(orient="records"),
                        source,
                        context={"kind": "database_row", "table_name": table_name, "columns": frame.columns.tolist()},
                        start_index=offset + 1,
                    )
                    result.records.extend(records)
                    offset += len(records)
            finally:
                connection.close()
        except Exception as exc:
            result.issues.append(
                ExtractionIssue(
                    source_name=source.source_name,
                    source_type=source.source_type,
                    source_location=source.location,
                    severity="error",
                    message=f"Failed to parse SQLite database: {exc}",
                )
            )
        return result


EXTRACTORS: dict[str, BaseExtractor] = {
    "website": WebsiteExtractor(),
    "pdf": PdfExtractor(),
    "csv": CsvExtractor(),
    "spreadsheet": SpreadsheetExtractor(),
    "database": SQLiteExtractor(),
}
