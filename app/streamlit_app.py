from __future__ import annotations

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from app.config import AppConfig, RAW_SOURCES_DIR, TEMP_UPLOADS_DIR, ensure_directories
from app.pipeline import build_summary, run_pipeline, summary_to_json

ensure_directories()
config = AppConfig()

st.set_page_config(page_title="Multi-Source Data Extraction Engine", layout="wide")
st.title("Multi-Source Data Extraction Engine")
st.caption("Extract, normalize, validate, and export training-ready data from websites, PDFs, CSVs, spreadsheets, and SQLite databases.")

st.sidebar.header("Inputs")
available_files = sorted(path for path in RAW_SOURCES_DIR.iterdir() if path.is_file())
selected_files = st.sidebar.multiselect(
    "Sample/local sources",
    options=available_files,
    format_func=lambda path: path.name,
)
website_url = st.sidebar.text_input("Website URL", placeholder="https://example.com/page")
uploaded_files = st.sidebar.file_uploader(
    "Upload files",
    type=["pdf", "csv", "xlsx", "xls", "db", "sqlite", "sqlite3", "html", "htm"],
    accept_multiple_files=True,
)
output_stem = st.sidebar.text_input("Export name", value=config.output_stem)
run_clicked = st.sidebar.button("Run extraction")

st.markdown(
    """
This app normalizes every extracted item into a compact schema:
`record_id`, `source_name`, `source_type`, `source_location`, `title`, `content`, `normalized_text`, and `metadata_json`.
"""
)

source_locations: list[str] = [str(path) for path in selected_files]
if website_url.strip():
    source_locations.append(website_url.strip())

for uploaded in uploaded_files or []:
    suffix = Path(uploaded.name).suffix or ".bin"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=TEMP_UPLOADS_DIR) as handle:
        handle.write(uploaded.read())
        source_locations.append(handle.name)

if run_clicked:
    if not source_locations:
        st.error("Select at least one source file or enter one website URL.")
    else:
        with st.spinner("Running extraction and normalization pipeline..."):
            records_df, diagnostics_df, exports = run_pipeline(source_locations, stem=output_stem)
            summary = build_summary(records_df, diagnostics_df)

        metrics = st.columns(3)
        metrics[0].metric("Records", summary["record_count"])
        metrics[1].metric("Issues", summary["issue_count"])
        metrics[2].metric("Source Types", len(summary["records_by_source_type"]))

        st.subheader("Summary")
        st.code(summary_to_json(summary), language="json")

        st.subheader("Normalized Records")
        st.dataframe(records_df, use_container_width=True, hide_index=True)

        st.subheader("Diagnostics")
        if diagnostics_df.empty:
            st.success("No extraction issues were recorded in this run.")
        else:
            st.dataframe(diagnostics_df, use_container_width=True, hide_index=True)

        st.subheader("Exports")
        for label, path in exports.items():
            st.write(f"{label.upper()}: {path}")
            st.download_button(
                label=f"Download {label.upper()}",
                data=path.read_bytes(),
                file_name=path.name,
                mime="application/octet-stream",
                key=f"download-{label}",
            )
else:
    st.info("Choose one or more sources from the sidebar and run the pipeline to preview normalized output.")
