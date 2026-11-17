from pydantic import BaseModel, Field
from app.schemas.extraction import PageExtraction, ChunkExtraction


class PartyItem(BaseModel):
    name: str
    role: str
    evidence_quote: str = "Not specified"
    source_page: int = 1
    quote_verified: bool = False
    provenance: str = "EXTRACTED"


class GroundedItem(BaseModel):
    text: str
    evidence_quote: str = "Not specified"
    source_page: int = 1
    quote_verified: bool = False
    provenance: str = "EXTRACTED"


class ChunkSummaryExtraction(BaseModel):
    parties: list[PartyItem] = Field(default_factory=list)
    conditions: list[GroundedItem] = Field(default_factory=list)
    obligations: list[GroundedItem] = Field(default_factory=list)
    financial_terms: list[GroundedItem] = Field(default_factory=list)


class DocumentSummaryResponse(BaseModel):
    title: str
    document_type: str
    purpose: str
    parties: list[PartyItem] = Field(default_factory=list)
    main_conditions: list[GroundedItem] = Field(default_factory=list)
    obligations: list[GroundedItem] = Field(default_factory=list)
    financial_terms: list[GroundedItem] = Field(default_factory=list)
    short_summary: str
    detailed_summary: str
    verification_rate: float = 0.0
    llm_provider: str = "gemini"
    llm_model: str = "gemini-1.5-flash"
    warnings: list[str] = Field(default_factory=list)


class DocumentSummaryRequest(BaseModel):
    document_id: str
    pages: list[PageExtraction] = Field(default_factory=list)
    chunks: list[ChunkExtraction] = Field(default_factory=list)

