import logging
import re
import time
from typing import TypeVar
from pydantic import BaseModel

from app.providers.base import LLMProvider
from app.schemas.summary import (
    DocumentSummaryResponse,
    ChunkSummaryExtraction,
    GroundedItem,
    PartyItem,
)
from app.schemas.clause import (
    ChunkClauseExtraction,
    RawClauseItem,
    BatchExplanationsResponse,
    ClauseExplanations,
)
from app.schemas.simplify import (
    LLMSimplifyResult,
    GlossaryTerm,
)

logger = logging.getLogger("ai_engine.mock_provider")
T = TypeVar("T", bound=BaseModel)


class MockProvider(LLMProvider):
    """Deterministic mock provider used strictly for automated unit and integration tests."""

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def model_name(self) -> str:
        return "mock-legal-v1"

    async def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        system_prompt: str | None = None,
        temperature: float = 0.1,
    ) -> T:
        start_time = time.perf_counter()

        # Extract content between delimiters if available
        doc_content = ""
        match = re.search(r"<document_content>(.*?)</document_content>", prompt, re.DOTALL)
        if match:
            doc_content = match.group(1).strip()

        latency_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info("mock provider generated structured response in %.2f ms for %s", latency_ms, schema.__name__)

        if schema is DocumentSummaryResponse:
            # Look for evidence in doc_content
            has_acme = "acme" in doc_content.lower()
            quote_party = "Acme Corp" if has_acme else "Disclosing Party"
            quote_conf = "Confidential Information" if "confidential" in doc_content.lower() else "Agreement"

            obj = DocumentSummaryResponse(
                title="Non-Disclosure and Confidentiality Agreement" if "disclosure" in doc_content.lower() else "Commercial Legal Agreement",
                document_type="Non-Disclosure Agreement (NDA)" if "disclosure" in doc_content.lower() else "Service Agreement",
                purpose="To govern and protect proprietary business and technical data exchanged between the parties.",
                parties=[
                    PartyItem(
                        name="Acme Corporation",
                        role="Disclosing Party",
                        evidence_quote="Acme Corporation (\"Disclosing Party\")" if "acme" in doc_content.lower() else quote_party,
                        source_page=1,
                        quote_verified=True,
                        provenance="EXTRACTED",
                    ),
                    PartyItem(
                        name="Beta Technologies LLC",
                        role="Receiving Party",
                        evidence_quote="Beta Technologies LLC (\"Receiving Party\")" if "beta" in doc_content.lower() else "Receiving Party",
                        source_page=1,
                        quote_verified=True,
                        provenance="EXTRACTED",
                    ),
                ],
                main_conditions=[
                    GroundedItem(
                        text="Recipient shall maintain confidentiality for a period of 2 years.",
                        evidence_quote="shall hold the Confidential Information in strict confidence" if "confidence" in doc_content.lower() else quote_conf,
                        source_page=1,
                        quote_verified=True,
                        provenance="EXTRACTED",
                    )
                ],
                obligations=[
                    GroundedItem(
                        text="Promptly notify the disclosing party in the event of unauthorized access.",
                        evidence_quote="notify the disclosing party immediately" if "immediately" in doc_content.lower() else "promptly notify",
                        source_page=2 if "delaware" in doc_content.lower() else 1,
                        quote_verified=True,
                        provenance="EXTRACTED",
                    )
                ],
                financial_terms=[
                    GroundedItem(
                        text="No fees or licensing payments are stipulated.",
                        evidence_quote="Not specified",
                        source_page=1,
                        quote_verified=False,
                        provenance="EXTRACTED",
                    )
                ],
                short_summary="A standard bilateral non-disclosure agreement establishing confidentiality covenants and non-use obligations.",
                detailed_summary="This agreement sets forth obligations between the parties to protect confidential business, technical, and operational disclosures. It defines the categories of protected information, exclusions from confidentiality, notice provisions in the event of compulsory legal process, and specifies dispute resolution procedures.",
                verification_rate=100.0,
                llm_provider=self.provider_name,
                llm_model=self.model_name,
                warnings=[],
            )
            return obj  # type: ignore

        if schema is ChunkSummaryExtraction:
            obj = ChunkSummaryExtraction(
                parties=[PartyItem(name="Acme Corp", role="Disclosing Party", evidence_quote="Acme Corp", source_page=1)],
                conditions=[GroundedItem(text="Confidential treatment required", evidence_quote="Confidential Information", source_page=1)],
                obligations=[GroundedItem(text="Shall not disclose", evidence_quote="shall not disclose", source_page=1)],
                financial_terms=[GroundedItem(text="Not specified", evidence_quote="Not specified", source_page=1)],
            )
            return obj  # type: ignore

        if schema is ChunkClauseExtraction:
            obj = ChunkClauseExtraction(
                clauses=[
                    RawClauseItem(
                        title="Confidential Information and Non-Disclosure",
                        category="Confidentiality",
                        custom_label=None,
                        original_text="Recipient agrees to hold all Confidential Information in strict confidence and not disclose it to any third party for a period of thirty (30) days.",
                        evidence_quote="hold all Confidential Information in strict confidence",
                        importance="HIGH",
                        affected_party="Receiving Party",
                        source_page=1,
                        section_reference="Section 2.1",
                    ),
                    RawClauseItem(
                        title="Termination for Convenience",
                        category="Termination",
                        custom_label=None,
                        original_text="Either party may terminate this Agreement by providing thirty (30) days prior written notice.",
                        evidence_quote="by providing thirty (30) days prior written notice",
                        importance="MEDIUM",
                        affected_party="Both parties",
                        source_page=1,
                        section_reference="Section 4.1",
                    ),
                    RawClauseItem(
                        title="Security Protocol Guidelines",
                        category="Other",
                        custom_label="Security Standards",
                        original_text="The contractor must adhere to the designated data isolation guidelines.",
                        evidence_quote="adhere to the designated data isolation guidelines",
                        importance="LOW",
                        affected_party="Contractor",
                        source_page=1,
                        section_reference="Section 6.1",
                    ),
                ]
            )
            return obj  # type: ignore

        if schema is BatchExplanationsResponse:
            obj = BatchExplanationsResponse(
                explanations=[
                    ClauseExplanations(
                        clause_index=0,
                        simplified_simple="You must keep all shared confidential information secret and not share it with others for 30 days.",
                        simplified_detailed="The receiving party is strictly prohibited from disclosing confidential information to third parties for a duration of thirty (30) days, unless authorized in writing.",
                        simplified_professional="Imposes a 30-day non-disclosure obligation on the receiving party protecting shared business and technical disclosures.",
                    ),
                    ClauseExplanations(
                        clause_index=1,
                        simplified_simple="Either party can cancel this agreement at any time by giving 30 days written notice.",
                        simplified_detailed="Allows unilateral termination for convenience by either party subject to a mandatory 30-day advance written notice requirement.",
                        simplified_professional="Provides bilateral termination for convenience with a standard 30-day notice period.",
                    ),
                    ClauseExplanations(
                        clause_index=2,
                        simplified_simple="The contractor must follow all required data safety rules.",
                        simplified_detailed="The contractor is required to strictly observe all designated security protocols regarding data isolation.",
                        simplified_professional="Mandates strict adherence to security and data isolation protocols for contractor personnel.",
                    ),
                ]
            )
            return obj  # type: ignore

        if schema is LLMSimplifyResult:
            obj = LLMSimplifyResult(
                explanation="The contractor must defend and protect the company against all legal claims and losses resulting from negligence, unless caused by the company's sole fault.",
                glossary=[
                    GlossaryTerm(
                        term="Indemnify",
                        definition="An obligation to compensate or protect another party against legal liability, loss, or damage.",
                    ),
                    GlossaryTerm(
                        term="Severability",
                        definition="A provision stating that if one part of the contract is found invalid, the remainder remains in full effect.",
                    ),
                ],
                what_could_be_missed=[
                    "The indemnity obligation does not cover claims arising from the company's own negligence.",
                    "Written notice of any claim must be provided promptly.",
                ],
            )
            return obj  # type: ignore

        # Fallback default instantiation
        try:
            return schema.model_validate({})
        except Exception:
            return schema.construct()  # type: ignore

