from typing import Literal, Optional
from pydantic import BaseModel, Field


MissingRiskLevel = Literal["HIGH", "MEDIUM", "LOW", "INFORMATIONAL"]


class MissingProvisionItem(BaseModel):
    category: str = Field(..., description="Category of the missing provision (e.g. Financial, Contractual, Liability)")
    clause_name: str = Field(..., description="Title of the potentially missing clause or provision")
    why_it_matters: str = Field(..., description="Explanation of why this provision is normally expected and important")
    typical_provision: str = Field(..., description="Example of typical commercial language for such a provision")
    risk_level: MissingRiskLevel = Field("MEDIUM", description="Assessed risk level of omitting this provision: HIGH, MEDIUM, LOW, or INFORMATIONAL")
    label: str = Field("Possible omission", description="Standard compliance label, always 'Possible omission'")


class RawMissingAnalysisResult(BaseModel):
    detected_document_type: str = Field(..., description="Identified contract type (employment, rental_lease, nda, service_agreement, sale, loan, other)")
    missing_provisions: list[MissingProvisionItem] = Field(default_factory=list, description="List of expected provisions absent from the document")


class MissingProvisionsRequest(BaseModel):
    document_id: Optional[str] = None
    pages: list[dict] = Field(..., description="List of document pages with page_number and text")
    chunks: Optional[list[dict]] = None
    document_type_hint: Optional[str] = None


class MissingProvisionsResponse(BaseModel):
    document_id: Optional[str] = None
    detected_document_type: str = "other"
    missing_provisions: list[MissingProvisionItem] = Field(default_factory=list)
    total_missing: int = 0
    disclaimer: str = "Legal Disclaimer: LexiLegal AI provides automated analysis aid. Missing clause notices are labeled 'Possible omission' and do not constitute formal legal counsel."

