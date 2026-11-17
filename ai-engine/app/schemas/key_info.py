from typing import Optional
from pydantic import BaseModel, Field


class FactItem(BaseModel):
    value: str = Field(default="Not specified", description="The extracted factual value or exactly 'Not specified' if absent")
    source_page: Optional[int] = Field(None, description="Page number where this fact appears, or None if Not specified")
    evidence_quote: Optional[str] = Field(None, description="Verbatim quote from source text, or None if Not specified")
    quote_verified: bool = Field(False, description="Whether quote was verified against page text")
    provenance: str = Field("EXTRACTED", description="Provenance marker: EXTRACTED or AI_INTERPRETATION")


class ImportantDateItem(BaseModel):
    event: str = Field(..., description="Description of the event or milestone (e.g. Effective Date, First Payment, Expiration)")
    date_value: str = Field(..., description="The calendar date or timeframe mentioned in the text")
    source_page: Optional[int] = Field(None, description="Page number where the date appears")
    evidence_quote: Optional[str] = Field(None, description="Verbatim quote containing this date")
    quote_verified: bool = Field(False, description="Whether quote was verified against page text")


class KeyInfoRequest(BaseModel):
    document_id: Optional[str] = None
    pages: list[dict] = Field(..., description="List of document pages with page_number and text")
    chunks: Optional[list[dict]] = None


class RawKeyInfoResult(BaseModel):
    contract_amount: FactItem = Field(default_factory=FactItem)
    payment_deadlines: FactItem = Field(default_factory=FactItem)
    penalties: FactItem = Field(default_factory=FactItem)
    start_date: FactItem = Field(default_factory=FactItem)
    end_date: FactItem = Field(default_factory=FactItem)
    renewal_date: FactItem = Field(default_factory=FactItem)
    notice_period: FactItem = Field(default_factory=FactItem)
    termination_conditions: FactItem = Field(default_factory=FactItem)
    obligations: list[str] = Field(default_factory=list, description="Key ongoing obligations stipulated in the agreement")
    important_dates: list[ImportantDateItem] = Field(default_factory=list, description="List of important dates and milestones")


class KeyInfoResponse(RawKeyInfoResult):
    document_id: Optional[str] = None

