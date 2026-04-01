# Multi-Source Data Extractor
A Python-based pipeline that extracts and standardizes data from multiple file formats into a unified structure.
(My focus was prioritized on functionality, requirements, and outcomes rather than visual design or UI aesthetics)

## What it does
* Detects input source type automatically
* Extracts data from different formats
* Cleans and normalizes content
* Outputs structured data in **CSV & JSON**
* Logs errors and warnings in a diagnostics file

## Demo Video
[https://drive.google.com/file/d/1mOGPcza6Q3HrkjkeZiZ_JqtKkI2P9DyR/view?usp=sharing](https://drive.google.com/file/d/1mOGPcza6Q3HrkjkeZiZ_JqtKkI2P9DyR/view?usp=sharing)

## Supported Sources
* HTML / Web URLs
* PDF
* CSV
* Excel (`.xlsx`, `.xls`)
* SQLite databases

## Tech Stack
* Python
* Pandas
* BeautifulSoup
* Requests
* PyPDF
* OpenPyXL
* Streamlit

## How it works
1. Input files or URL
2. Detect source type
3. Use appropriate extractor
4. Clean & normalize data
5. Export to CSV/JSON
6. Generate diagnostics (if issues occur)

## Output Format

Each record contains:

* `record_id`
* `source_name`
* `source_type`
* `source_location`
* `title`
* `content`
* `normalized_text`
* `metadata_json`

## Run the Project

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Generate sample data

```bash
python -m scripts.create_sample_sources
```

### Run pipeline

```bash
python -m scripts.run_pipeline
```

### Run UI

```bash
python -m streamlit run app/streamlit_app.py
```

## Key Learnings
* Handling multiple data formats
* Building modular data pipelines
* Data normalization techniques
* Adding reliability with logging
* Creating simple UI using Streamlit
