from datetime import date
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


AccessTier = Literal["public", "internal", "confidential", "restricted"]


class DocumentMetadata(BaseModel):
    """Metadata used for filtering and organizing client documents."""

    model_config = ConfigDict(extra="forbid")

    department: str = Field(min_length=1)
    access_tier: AccessTier
    document_date: date

    @field_validator("department")
    @classmethod
    def normalize_department(cls, value: str) -> str:
        return value.strip().lower()


class ExtractedDocument(BaseModel):
    """Normalized content extracted from a source document."""

    model_config = ConfigDict(extra="forbid")

    document_id: str = Field(min_length=1)
    source_path: str = Field(min_length=1)
    source_type: Literal["pdf", "csv", "markdown"]
    content: str = Field(min_length=1)
    metadata: DocumentMetadata

    @field_validator("document_id", "source_path")
    @classmethod
    def normalize_identifiers(cls, value: str) -> str:
        return value.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        content = value.strip()
        if not content:
            raise ValueError("Document content cannot be empty")
        return content

    @property
    def filename(self) -> str:
        return Path(self.source_path).name
