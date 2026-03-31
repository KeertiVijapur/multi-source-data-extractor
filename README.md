# Multi-Source Data Extractor

## What this project does

This project can:
- detect the type of input source
- extract text/data from multiple source formats
- handle structured and unstructured inputs
- normalize the extracted content into one common schema
- store the final output in CSV and JSON format
- generate a diagnostics file for warnings and errors

## Supported source types

The current version supports:
- website pages (`html`, `htm`, and URL input)
- PDF files
- CSV files
- Excel files (`xlsx`, `xls`)
- SQLite databases

## Tech stack used

- Python
- Pandas
- BeautifulSoup
- Requests
- PyPDF
- OpenPyXL
- Streamlit
- ReportLab

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

## How the system works

1. The user provides one or more source files or a website URL.
2. The system detects the source type.
3. A matching extractor is used for that source.
4. The extracted content is cleaned and normalized.
5. Each extracted item is converted into a common output format.
6. Final results are exported as CSV and JSON.
7. If any issue happens during extraction, it is stored separately in diagnostics.

## Output format

Each normalized record contains:
- `record_id`
- `source_name`
- `source_type`
- `source_location`
- `title`
- `content`
- `normalized_text`
- `metadata_json`

## Features

- Multi-source extraction in one pipeline
- Source type detection
- Separate extractors for each file type
- Normalized training-ready output
- Error and warning logging
- Streamlit UI for demo
- Sample data generator for testing

## Setup

Open terminal in the project folder and run:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

If needed:

```bash
copy .env.example .env
```

## How to run the project

### 1. Create sample input files

```bash
python -m scripts.create_sample_sources
```

### 2. Run the pipeline from terminal

```bash
python -m scripts.run_pipeline
```

### 3. Run the Streamlit app

```bash
python -m streamlit run app/streamlit_app.py
```

## Demo flow

For demo, I can show:
- sample HTML file
- sample PDF file
- sample CSV file
- sample Excel file
- sample SQLite database
- extraction result in the Streamlit UI
- exported CSV/JSON files
- diagnostics file

## What I learned

Through this project, I learned:
- how to work with multiple data formats in Python
- how to build modular extractors
- how to normalize mixed data into a standard format
- how to make a data pipeline more reliable with diagnostics
- how to convert a backend pipeline into a simple demo application using Streamlit

## Conclusion

This project is a practical multi-source data extraction system built with open-source tools. It can take different input formats, extract useful information, normalize the output, and prepare clean data files for further AI/LLM use.
