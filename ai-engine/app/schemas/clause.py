from typing import Literal, Optional
from pydantic import BaseModel, Field
from app.schemas.extraction import PageExtraction, ChunkExtraction

STANDARD_CLAUSE_CATEGORIES = [
    "Confidentiality",
    "Termination",
    "Intellectual Property",
    "Liability and Indemnification",
    "Dispute Resolution",
    "Governing Law",
    "Payment Terms",
    "Representations and Warranties",
    "Non-Compete and Non-Solicitation",
    "Force Majeure",
    "Assignment",
    "Severability",
    "Amendment",
    "Notices",
    "Term and Renewal",
    "Data Protection and Privacy",
    "Insurance",
    "Other",
]


class RawClauseItem(BaseModel):
    title: str = Field(description="Concise title for the clause")
    category: str = Field(description="One of the 17 standard categories or Other")
    custom_label: Optional[str] = Field(default=None, description="Label when category is Other")
    original_text: str = Field(description="Exact or near-complete text of the clause from the document")
    evidence_quote: str = Field(description="Exact verbatim sentence or phrase from the document")
    importance: Literal["HIGH", "MEDIUM", "LOW"] = Field(default="MEDIUM", description="Importance rating")
    affected_party: str = Field(default="Both parties", description="Which party is primarily bound or affected")
    source_page: int = Field(default=1, description="Source page number where clause starts")
    section_reference: Optional[str] = Field(default=None, description="Section or article number/heading if present")


class ChunkClauseExtraction(BaseModel):
    clauses: list[RawClauseItem] = Field(default_factory=list)


class ClauseExplanations(BaseModel):
    clause_index: int = Field(description="0-based index of clause in batch")
    simplified_simple: str = Field(description="Simple English explanation without legalese, accessible to non-lawyers")
    simplified_detailed: str = Field(description="Detailed explanation preserving all conditions, exceptions, and limitations")
    simplified_professional: str = Field(description="Professional business executive summary")


class BatchExplanationsResponse(BaseModel):
    explanations: list[ClauseExplanations] = Field(default_factory=list)


class ClauseItem(BaseModel):
    title: str
    category: str
    custom_label: Optional[str] = None
    original_text: str
    simplified_simple: str
    simplified_detailed: str
    simplified_professional: str
    importance: Literal["HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    affected_party: str = "Both parties"
    source_page: int = 1
    section_reference: Optional[str] = None
    evidence_quote: str
    quote_verified: bool = False
    provenance: str = "EXTRACTED"
    numbers_dates_verified: bool = True
    warnings: list[str] = Field(default_factory=list)


class ClauseAnalysisRequest(BaseModel):
    document_id: str
    pages: list[PageExtraction] = Field(default_factory=list)
    chunks: list[ChunkExtraction] = Field(default_factory=list)


class ClauseAnalysisResponse(BaseModel):
    document_id: str
    clauses: list[ClauseItem] = Field(default_factory=list)
    total_clauses: int = 0
    verification_rate: float = 0.0
    llm_provider: str = "gemini"
    llm_model: str = "gemini-1.5-flash"
    warnings: list[str] = Field(default_factory=list)
