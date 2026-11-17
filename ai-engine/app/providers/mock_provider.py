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

        if schema.__name__ == "LLMRisksWrapper":
            from app.schemas.risk import RawRiskItem
            from app.services.risk_service import LLMRisksWrapper
            return LLMRisksWrapper(
                risks=[
                    RawRiskItem(
                        title="Uncapped Indemnification Exposure",
                        category="Liability",
                        level="HIGH",
                        original_clause="Contractor shall indemnify and hold harmless Company from any and all damages.",
                        evidence_quote="shall indemnify and hold harmless",
                        source_page=1,
                        explanation="This clause obligates the contractor to indemnify the company without any monetary liability cap.",
                        why_it_matters="Unlimited liability can jeopardize the commercial solvency of the indemnifying party.",
                        possible_consequences="Potentially catastrophic financial liabilities exceeding total contract value.",
                        suggested_questions=[
                            "Can an aggregate liability cap matching the fees paid be added?",
                            "Can carve-outs for client gross negligence be included?",
                        ],
                    ),
                    RawRiskItem(
                        title="Short Cure Notice Period",
                        category="Contractual",
                        level="MEDIUM",
                        original_clause="Non-breaching party may terminate immediately if breach is not cured within 5 days.",
                        evidence_quote="not cured within 5 days",
                        source_page=1,
                        explanation="A 5-day cure window may be operationally insufficient to remedy complex service defects.",
                        why_it_matters="Increases the likelihood of unintended contract termination.",
                        possible_consequences="Premature termination and abrupt loss of recurring business.",
                        suggested_questions=["Can the cure window be extended to 30 calendar days?"],
                    ),
                ]
            )  # type: ignore

        if schema.__name__ == "RawChatResult":
            from app.schemas.chat import RawChatResult, StructuredCitation
            q_lower = prompt.lower()
            if "notice period" in q_lower or "termination" in q_lower:
                return RawChatResult(
                    answer="The agreement requires thirty (30) days prior written notice for termination without cause.",
                    citations=[
                        StructuredCitation(
                            page=2,
                            section_ref="Section 6",
                            quote="thirty (30) days prior written notice",
                            quote_verified=True,
                        )
                    ],
                    confidence="supported",
                )  # type: ignore
            elif "unrelated" in q_lower or "dog" in q_lower or "weather" in q_lower:
                return RawChatResult(
                    answer="The document does not appear to address this question.",
                    citations=[],
                    confidence="not found",
                )  # type: ignore
            else:
                return RawChatResult(
                    answer="Based on the agreement terms, the obligations and commercial conditions apply as specified.",
                    citations=[
                        StructuredCitation(
                            page=1,
                            section_ref="Section 1",
                            quote="shall perform all duties",
                            quote_verified=True,
                        )
                    ],
                    confidence="supported",
                )  # type: ignore

        if schema.__name__ == "RawKeyInfoResult":
            from app.schemas.key_info import FactItem, ImportantDateItem, RawKeyInfoResult
            return RawKeyInfoResult(
                contract_amount=FactItem(
                    value="$50,000.00",
                    source_page=1,
                    evidence_quote="total fee of $50,000.00",
                    quote_verified=True,
                ),
                payment_deadlines=FactItem(
                    value="Net 30 days from invoice",
                    source_page=1,
                    evidence_quote="payable Net 30 days from invoice",
                    quote_verified=True,
                ),
                penalties=FactItem(
                    value="1.5% monthly late interest",
                    source_page=1,
                    evidence_quote="accruing 1.5% monthly late interest",
                    quote_verified=True,
                ),
                start_date=FactItem(
                    value="October 1, 2026",
                    source_page=1,
                    evidence_quote="commencing on October 1, 2026",
                    quote_verified=True,
                ),
                end_date=FactItem(
                    value="September 30, 2027",
                    source_page=2,
                    evidence_quote="terminating on September 30, 2027",
                    quote_verified=True,
                ),
                renewal_date=FactItem(value="Not specified"),
                notice_period=FactItem(
                    value="30 days written notice",
                    source_page=2,
                    evidence_quote="upon 30 days written notice",
                    quote_verified=True,
                ),
                termination_conditions=FactItem(
                    value="Material breach with 30-day cure period",
                    source_page=2,
                    evidence_quote="material breach following 30-day cure",
                    quote_verified=True,
                ),
                obligations=[
                    "Provide monthly technical progress reports.",
                    "Safeguard proprietary confidential information.",
                ],
                important_dates=[
                    ImportantDateItem(
                        event="Contract Effective Date",
                        date_value="October 1, 2026",
                        source_page=1,
                        evidence_quote="October 1, 2026",
                    ),
                    ImportantDateItem(
                        event="Scheduled Expiration Date",
                        date_value="September 30, 2027",
                        source_page=2,
                        evidence_quote="September 30, 2027",
                    ),
                ],
            )  # type: ignore

        if schema.__name__ == "RawMissingAnalysisResult":
            from app.schemas.missing import MissingProvisionItem, RawMissingAnalysisResult
            return RawMissingAnalysisResult(
                detected_document_type="service_agreement",
                missing_provisions=[
                    MissingProvisionItem(
                        category="Liability",
                        clause_name="Limitation of Liability",
                        why_it_matters="Protects parties against uncapped enterprise liability in the event of unforeseen breaches.",
                        typical_provision="Each party's aggregate liability under this Agreement shall not exceed fees paid.",
                        risk_level="HIGH",
                        label="Possible omission",
                    ),
                    MissingProvisionItem(
                        category="Legal",
                        clause_name="Governing Law and Dispute Resolution",
                        why_it_matters="Clarifies which jurisdiction's statutes apply and prevents costly procedural forum disputes.",
                        typical_provision="This Agreement is governed by the laws of the State of Delaware.",
                        risk_level="MEDIUM",
                        label="Possible omission",
                    ),
                ],
            )  # type: ignore

        # Fallback default instantiation
        try:
            return schema.model_validate({})
        except Exception:
            return schema.construct()  # type: ignore

