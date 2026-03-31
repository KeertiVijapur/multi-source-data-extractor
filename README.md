# Multi-Source Data Extraction Engine

This repository now implements Problem Statement 1 from the internship brief: a modular engine that collects information from heterogeneous sources, normalizes it into a training-ready schema, and exports reproducible CSV and JSON files using open-source tools only.

## Problem alignment

The project supports these source types:
- websites (`.html`, `.htm`, and live `http/https` URLs)
- PDFs
- CSV files
- spreadsheets (`.xlsx`, `.xls`)
- SQLite databases (`.db`, `.sqlite`, `.sqlite3`)

For every extracted item, the system preserves provenance and converts content into one compact format suitable for downstream LLM training or fine-tuning workflows.

## What the system does

1. Detects source type from a file path or URL.
2. Uses a dedicated extractor for each source family.
3. Handles mixed structured and unstructured content.
4. Normalizes output into a shared schema.
5. Logs warnings and errors instead of failing the whole batch.
6. Exports clean records to CSV and JSON.
7. Exports diagnostics separately for debugging and QA.

## Normalized schema

Each output row contains:
- `record_id`
- `source_name`
- `source_type`
- `source_location`
- `title`
- `content`
- `normalized_text`
- `metadata_json`

This keeps the exported data simple enough for model training while still preserving detailed metadata for auditability.

## Project structure

```text
app/
  config.py
  extractors.py
  models.py
  pipeline.py
  streamlit_app.py
  utils.py
scripts/
  create_sample_sources.py
  run_pipeline.py
data/
  raw/sources/
  processed/
  exports/
```

## Setup

```bash
cd C:\Users\keert\Documents\Playground
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Optional environment values:

```bash
copy .env.example .env
```

## Quick start

Generate demo sources:

```bash
python -m scripts.create_sample_sources
```

Run the extraction pipeline:

```bash
python -m scripts.run_pipeline
```

Launch the Streamlit app:

```bash
streamlit run app/streamlit_app.py
```

## Sample sources included by script

The sample generator creates:
- an HTML page with paragraphs and a table
- a CSV file with support tickets
- an Excel workbook with two sheets
- a SQLite database with two tables
- a PDF containing operational notes

This makes the project easy to demo locally even without internet access.

## Design notes

### Extractor strategy
- `WebsiteExtractor` parses page text and HTML tables.
- `PdfExtractor` reads page text and chunks longer content.
- `CsvExtractor` converts each row into a training record.
- `SpreadsheetExtractor` processes every sheet in a workbook.
- `SQLiteExtractor` scans all user tables and extracts rows.

### Error handling
- source-specific issues are captured as diagnostics
- empty or malformed content produces warnings instead of aborting the run
- the pipeline still exports successful records even if one source partially fails

### Reproducibility
- sample data is generated locally
- outputs are written to deterministic file locations
- dependencies are open source only

## Research summary

Before implementation, I mapped the assignment against common approaches used in document ETL systems and training-data preparation tools. The design here follows a simple, explainable extractor-per-source model instead of a black-box ingestion framework so the full pipeline stays easy to understand and present during evaluation.

## Iterations and failed attempts

1. Initial repo state was a lost-and-found multimodal search project, which did not match any of the internship problem statements.
2. I briefly evaluated reusing the old semantic-search pipeline, but it would have forced the assignment into the wrong problem category.
3. The final direction replaced that logic with a purpose-built extraction engine centered on source detection, normalization, and diagnostics.

## Known limitations

- PDF extraction is text-based and does not include OCR for scanned documents.
- Website extraction works best on static HTML pages.
- SQLite is the supported database target in this version; other databases can be added through new extractor classes.

## Next improvements

- add OCR fallback for scanned PDFs
- add schema validation rules per source domain
- add deduplication scoring across sources
- add scheduling/automation for recurring ingestion
- add unit tests around each extractor
