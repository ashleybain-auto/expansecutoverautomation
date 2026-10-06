"""Pydantic models for the ECCS Workbook Compiler."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class WorkbookMetadata(BaseModel):
    """Metadata describing the source workbook."""
    filename: str
    extension: str
    sha256: str
    file_size_bytes: int
    analyzed_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class WorksheetModel(BaseModel):
    """Normalized representation of an Excel worksheet."""
    name: str
    visibility: str = "unknown"
    used_range: str | None = None
    row_count: int = 0
    column_count: int = 0
    classification: str = "unknown"
    columns: list[dict[str, Any]] = Field(default_factory=list)


class VBAProcedureModel(BaseModel):
    """Normalized representation of a VBA procedure."""
    module: str
    name: str
    procedure_type: str | None = None
    classification: str = "OTHER"
    source_reference: str | None = None


class WorkbookIR(BaseModel):
    """Intermediate representation produced by the ECCS Workbook Compiler."""
    workbook: WorkbookMetadata
    worksheets: list[WorksheetModel] = Field(default_factory=list)
    vba_modules: list[dict[str, Any]] = Field(default_factory=list)
    procedures: list[VBAProcedureModel] = Field(default_factory=list)
    sql_references: list[dict[str, Any]] = Field(default_factory=list)
    api_references: list[dict[str, Any]] = Field(default_factory=list)
    actions: list[dict[str, Any]] = Field(default_factory=list)
    mappings: list[dict[str, Any]] = Field(default_factory=list)
    settings: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    unsupported: list[str] = Field(default_factory=list)
