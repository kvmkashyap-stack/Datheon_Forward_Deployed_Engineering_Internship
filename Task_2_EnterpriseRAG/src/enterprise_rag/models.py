from enum import IntEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field


class ClearanceLevel(IntEnum):
    """Hierarchical document classification levels."""

    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    RESTRICTED = 3


class UserContext(BaseModel):
    """User identity and trusted access permissions."""

    model_config = ConfigDict(frozen=True)

    user_id: Annotated[str, Field(min_length=1)]
    tenant_id: Annotated[str, Field(min_length=1)]
    clearance: ClearanceLevel


class DocumentChunk(BaseModel):
    """Document chunk with security and citation metadata."""

    model_config = ConfigDict(frozen=True)

    chunk_id: Annotated[str, Field(min_length=1)]
    content: Annotated[str, Field(min_length=1)]
    tenant_id: Annotated[str, Field(min_length=1)]
    classification: ClearanceLevel
    source_id: Annotated[str, Field(min_length=1)]
    source_name: Annotated[str, Field(min_length=1)]
    page_number: Annotated[int, Field(ge=1)]