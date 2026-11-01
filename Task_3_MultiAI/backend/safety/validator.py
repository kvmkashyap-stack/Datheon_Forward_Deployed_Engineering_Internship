import re
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_validator

class InventoryQuerySchema(BaseModel):
    product_identifier: str = Field(..., description="Product SKU (e.g. SKU-1001) or product name/keyword")

    @field_validator("product_identifier")
    @classmethod
    def validate_identifier(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("Product identifier cannot be empty.")
        if len(clean) > 100:
            raise ValueError("Product identifier is too long (max 100 characters).")
        return clean

class StockAvailabilitySchema(BaseModel):
    product_identifier: str = Field(..., description="Product SKU or product name")
    requested_quantity: int = Field(..., description="Desired quantity to verify")

    @field_validator("requested_quantity")
    @classmethod
    def validate_quantity(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("Requested quantity must be a positive integer greater than 0.")
        if v > 1_000_000:
            raise ValueError("Requested quantity exceeds maximum batch limit (1,000,000).")
        return v

class LeadLookupSchema(BaseModel):
    lead_id: str = Field(..., description="Unique customer lead ID (e.g. LEAD-501)")

    @field_validator("lead_id")
    @classmethod
    def validate_lead_id(cls, v: str) -> str:
        clean = v.strip().upper()
        if not re.match(r"^LEAD-\d+$", clean):
            raise ValueError("Invalid Lead ID format. Expected format like 'LEAD-501'.")
        return clean

class LeadStatusUpdateSchema(BaseModel):
    lead_id: str = Field(..., description="Unique customer lead ID (e.g. LEAD-501)")
    new_status: Literal["new", "contacted", "qualified", "proposal", "won", "lost"] = Field(
        ..., description="Target lead status"
    )
    notes: Optional[str] = Field(None, description="Optional notes explaining the status update")
    idempotency_key: Optional[str] = Field(None, description="Optional idempotency key to prevent duplicate updates")

    @field_validator("lead_id")
    @classmethod
    def validate_lead_id(cls, v: str) -> str:
        clean = v.strip().upper()
        if not re.match(r"^LEAD-\d+$", clean):
            raise ValueError("Invalid Lead ID format. Expected format like 'LEAD-501'.")
        return clean

class CreateTicketSchema(BaseModel):
    title: str = Field(..., min_length=3, max_length=150, description="Short title describing the ticket issue")
    description: str = Field(..., min_length=5, max_length=2000, description="Detailed problem statement or request")
    customer_name: str = Field(..., min_length=2, max_length=100, description="Customer or organization name")
    priority: Literal["low", "medium", "high", "urgent"] = Field(
        default="medium", description="Ticket urgency level"
    )
    idempotency_key: Optional[str] = Field(None, description="Optional idempotency key to prevent duplicate creation")
