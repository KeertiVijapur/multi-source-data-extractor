from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceDescriptor:
    location: str
    source_type: str
    source_name: str


@dataclass
class ExtractedRecord:
    source_name: str
    source_type: str
    source_location: str
    record_index: int
    title: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExtractionIssue:
    source_name: str
    source_type: str
    source_location: str
    severity: str
    message: str
    context: str = ""


@dataclass
class ExtractionResult:
    records: list[ExtractedRecord] = field(default_factory=list)
    issues: list[ExtractionIssue] = field(default_factory=list)
