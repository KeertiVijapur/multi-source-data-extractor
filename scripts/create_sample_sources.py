from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from app.config import RAW_SOURCES_DIR, ensure_directories


def create_html(path: Path) -> None:
    html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Open Source AI Readiness Bulletin</title>
  <meta name="description" content="Weekly operating notes, milestones, and action items for the internship project." />
</head>
<body>
  <h1>AI Ops Readiness Bulletin</h1>
  <p>The analytics team is preparing a reusable extraction pipeline for internal knowledge assets.</p>
  <p>Source reliability is graded weekly, and failed rows are tracked for later review.</p>
  <h2>Current focus areas</h2>
  <ul>
    <li>Website parsing with resilient HTML cleanup</li>
    <li>PDF chunking for downstream fine-tuning datasets</li>
    <li>Spreadsheet normalization across business teams</li>
  </ul>
  <table>
    <thead>
      <tr><th>owner</th><th>topic</th><th>status</th></tr>
    </thead>
    <tbody>
      <tr><td>Anika</td><td>Data contracts</td><td>active</td></tr>
      <tr><td>Rahul</td><td>Schema validation</td><td>review</td></tr>
    </tbody>
  </table>
</body>
</html>
"""
    path.write_text(html, encoding="utf-8")


def create_csv(path: Path) -> None:
    frame = pd.DataFrame(
        [
            {"ticket_id": "CS-101", "customer": "Mira Foods", "issue": "Delayed invoice parsing", "priority": "high"},
            {"ticket_id": "CS-102", "customer": "Northwind Labs", "issue": "CSV export missing dates", "priority": "medium"},
            {"ticket_id": "CS-103", "customer": "BluePeak", "issue": "Duplicate records in training set", "priority": "high"},
        ]
    )
    frame.to_csv(path, index=False)


def create_xlsx(path: Path) -> None:
    operations = pd.DataFrame(
        [
            {"name": "Ops checklist", "owner": "Rina", "milestone": "Parser QA", "due_date": "2026-04-01"},
            {"name": "Infra review", "owner": "Dev", "milestone": "SQLite sync", "due_date": "2026-04-03"},
        ]
    )
    research = pd.DataFrame(
        [
            {"title": "PDF extraction survey", "summary": "Compared pypdf, OCR fallbacks, and layout-aware parsers."},
            {"title": "Website extraction review", "summary": "Documented table parsing edge cases and malformed HTML handling."},
        ]
    )
    with pd.ExcelWriter(path) as writer:
        operations.to_excel(writer, sheet_name="operations", index=False)
        research.to_excel(writer, sheet_name="research", index=False)


def create_sqlite(path: Path) -> None:
    connection = sqlite3.connect(path)
    try:
        pd.DataFrame(
            [
                {"meeting_id": 1, "subject": "Pipeline review", "owner": "Ishaan", "notes": "Need stronger null handling."},
                {"meeting_id": 2, "subject": "Export format", "owner": "Sara", "notes": "JSON schema approved for training corpora."},
            ]
        ).to_sql("meetings", connection, index=False, if_exists="replace")
        pd.DataFrame(
            [
                {"incident_id": "INC-1", "severity": "warning", "description": "Spreadsheet sheet had unnamed column."},
                {"incident_id": "INC-2", "severity": "error", "description": "Source website returned malformed table markup."},
            ]
        ).to_sql("incidents", connection, index=False, if_exists="replace")
    finally:
        connection.close()


def create_pdf(path: Path) -> None:
    pdf = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    lines = [
        "Extraction Engine Notes",
        "The system collects structured and unstructured text from mixed enterprise sources.",
        "Normalization converts each item into a training-ready record with provenance metadata.",
        "Important checks include source-type detection, missing field handling, and issue logging.",
        "Failed rows should not stop the batch run; they should be surfaced in diagnostics instead.",
    ]
    y = height - 72
    for line in lines:
        pdf.drawString(72, y, line)
        y -= 22
    pdf.save()


def main() -> None:
    ensure_directories()
    create_html(RAW_SOURCES_DIR / "sample_portal.html")
    create_csv(RAW_SOURCES_DIR / "customer_tickets.csv")
    create_xlsx(RAW_SOURCES_DIR / "project_tracker.xlsx")
    create_sqlite(RAW_SOURCES_DIR / "team_notes.sqlite")
    create_pdf(RAW_SOURCES_DIR / "extraction_notes.pdf")
    print(f"Sample sources created in {RAW_SOURCES_DIR}")


if __name__ == "__main__":
    main()
