from typing import Literal, Optional
from pydantic import BaseModel, Field


RiskCategory = Literal["Financial", "Legal", "Privacy", "Contractual", "Employment", "Liability"]
RiskLevel = Literal["HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]


class RawRiskItem(BaseModel):
    title: str = Field(..., description="Short descriptive title of the risk finding")
    category: RiskCategory = Field(..., description="Risk category: Financial, Legal, Privacy, Contractual, Employment, or Liability")
    level: RiskLevel = Field(..., description="Severity level: HIGH, MEDIUM, LOW, or INFORMATIONAL")
    original_clause: str = Field(..., description="The original contract language containing the risk")
    evidence_quote: str = Field(..., description="Exact verbatim quote from the document supporting this risk finding")
    source_page: int = Field(1, description="Source page number where the evidence quote appears")
    explanation: str = Field(..., description="Clear explanation of why this clause presents a risk, avoiding legal conclusions like 'illegal/void'")
    why_it_matters: str = Field(..., description="Practical reason why this matters to the contracting party")
    possible_consequences: str = Field(..., description="Potential adverse outcomes, operational problems, or financial burdens")
    suggested_questions: list[str] = Field(default_factory=list, description="Questions the party should ask or negotiate regarding this clause")


class RiskFindingItem(RawRiskItem):
    quote_verified: bool = Field(False, description="Whether the evidence quote was verified against page text")
    jurisdiction_caveat: Optional[str] = Field(None, description="Caveat regarding governing law if not specified in the agreement")
    provenance: str = Field("AI_INTERPRETATION", description="Provenance marker: AI_INTERPRETATION or EXTRACTED")


class RiskAnalysisRequest(BaseModel):
    document_id: Optional[str] = None
    pages: list[dict] = Field(..., description="List of document pages with page_number and text")
    chunks: Optional[list[dict]] = None
    governing_law_found: Optional[bool] = None


class RiskAnalysisResponse(BaseModel):
    document_id: Optional[str] = None
    risks: list[RiskFindingItem] = Field(default_factory=list)
    total_risks: int = 0
    high_risks: int = 0
    medium_risks: int = 0
    low_risks: int = 0
    informational_risks: int = 0
    governing_law_found: bool = True
    jurisdiction_warning: Optional[str] = None
    overall_risk_score: float = 0.0

