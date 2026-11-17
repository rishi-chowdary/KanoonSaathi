from app.extensions import db
from app.models.analysis import DocumentAnalysis
from app.models.chat import ChatConversation, ChatMessage
from app.models.chunk import DocumentChunk
from app.models.clause import ExtractedClause
from app.models.document import Document
from app.models.key_info import ExtractedInformation
from app.models.missing_warning import MissingClauseWarning
from app.models.risk import RiskFinding
from app.models.user import User


def test_complete_entity_graph_persistence_and_cascade(app):
    """Test instantiating and persisting all 10 legal entities and cascading deletes."""
    with app.app_context():
        # 1. User
        user = User(
            email="partner@legalcorp.com",
            full_name="Partner Sterling",
            role="ADMIN",
        )
        user.set_password("SterlingSecure2026")
        db.session.add(user)
        db.session.commit()
        assert user.id is not None
        assert user.created_at is not None

        # 2. Document
        doc = Document(
            user_id=user.id,
            original_filename="master_service_agreement.pdf",
            storage_path="uploads/test_msa.pdf",
            file_type="PDF",
            file_size=204850,
            file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            page_count=4,
            is_scanned=False,
            status="ANALYZED",
        )
        db.session.add(doc)
        db.session.commit()
        assert doc.id is not None

        # 3. DocumentAnalysis
        analysis = DocumentAnalysis(
            document_id=doc.id,
            title="Master Service Agreement",
            document_type="Master Services Agreement (MSA)",
            purpose="Provision of cloud consulting services",
            parties=[
                {"name": "Client Corp", "role": "Client"},
                {"name": "Vendor LLC", "role": "Vendor"},
            ],
            summary_short="Consulting agreement for cloud migration services.",
            summary_detailed="Detailed obligations across milestone delivery, compensation, and IP.",
            main_conditions=[{"condition": "Quarterly review of deliverables"}],
            obligations_summary=[
                {"party": "Vendor", "obligation": "Deliver sprint reports"}
            ],
            financial_terms_summary=[{"term": "Net 30 payment schedule"}],
            llm_provider="local_nlp",
            llm_model="hybrid_extractive",
            verification_rate=100.0,
        )
        db.session.add(analysis)
        db.session.commit()
        assert analysis.id is not None

        # 4. ExtractedClause
        clause = ExtractedClause(
            analysis_id=analysis.id,
            title="Limitation of Liability",
            category="Limitation of Liability",
            custom_label="Liability Cap",
            original_text="Vendor liability shall not exceed fees paid in prior 12 months.",
            simplified_simple="Vendor's maximum penalty is capped at 1 year of fees.",
            simplified_detailed="Neither party is liable for consequential damages; total cap is 12 months fees.",
            simplified_professional="Mutual cap on aggregate damages equal to 12 months fees paid.",
            importance="HIGH",
            affected_party="Vendor",
            source_page=3,
            section_reference="Section 8.1",
            evidence_quote="shall not exceed fees paid in prior 12 months",
            quote_verified=True,
            provenance="EXTRACTED",
        )
        db.session.add(clause)

        # 5. RiskFinding
        risk = RiskFinding(
            analysis_id=analysis.id,
            category="Indemnity",
            level="HIGH",
            title="Broad Uncapped Indemnity",
            original_clause="Client shall indemnify Vendor against any third-party claims.",
            explanation="Uncapped indemnification poses substantial financial exposure.",
            why_it_matters="Client could be liable for defense costs without limits.",
            possible_consequences="Significant legal expenses in case of patent disputes.",
            suggested_questions=["Can we add a financial ceiling to this indemnity?"],
            source_page=4,
            evidence_quote="indemnify Vendor against any third-party claims",
            quote_verified=True,
            provenance="AI_INTERPRETATION",
        )
        db.session.add(risk)

        # 6. ExtractedInformation
        info = ExtractedInformation(
            analysis_id=analysis.id,
            contract_amount="$150,000 USD",
            contract_amount_page=1,
            payment_deadlines="Within 30 calendar days of invoice",
            payment_deadlines_page=2,
            penalties="1.5% monthly late interest",
            penalties_page=2,
            start_date="2026-01-01",
            start_date_page=1,
            end_date="2027-01-01",
            end_date_page=1,
            renewal_date="2026-12-01",
            renewal_date_page=1,
            notice_period="30 days written notice",
            notice_period_page=3,
            termination_conditions="30 days notice for convenience",
            termination_conditions_page=3,
            obligations=[{"obligation": "Deliver monthly status report"}],
            important_dates=[{"event": "First milestone", "date": "2026-03-31"}],
        )
        db.session.add(info)

        # 7. MissingClauseWarning
        warning = MissingClauseWarning(
            analysis_id=analysis.id,
            category="Dispute Resolution",
            clause_name="Governing Law & Jurisdiction",
            why_it_matters="Without governing law, cross-border disputes face conflict-of-law confusion.",
            typical_provision="This Agreement shall be governed by Delaware law.",
            risk_level="MEDIUM",
            label="Missing clause warning",
        )
        db.session.add(warning)

        # 8. DocumentChunk
        chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=0,
            page_number=1,
            content="This Master Services Agreement is entered into by Client Corp and Vendor LLC.",
            token_count=15,
        )
        db.session.add(chunk)

        # 9. ChatConversation
        conv = ChatConversation(
            document_id=doc.id,
            user_id=user.id,
            title="Liability Review",
        )
        db.session.add(conv)
        db.session.commit()

        # 10. ChatMessage
        msg = ChatMessage(
            conversation_id=conv.id,
            role="assistant",
            content="The liability is capped at 12 months fees under Section 8.1.",
            citations=[
                {"page": 3, "section": "8.1", "quote": "fees paid in prior 12 months"}
            ],
            addressed_in_document=True,
        )
        db.session.add(msg)
        db.session.commit()

        # Verify all 10 records exist
        assert ExtractedClause.query.filter_by(analysis_id=analysis.id).count() == 1
        assert RiskFinding.query.filter_by(analysis_id=analysis.id).count() == 1
        assert (
            ExtractedInformation.query.filter_by(analysis_id=analysis.id).count() == 1
        )
        assert (
            MissingClauseWarning.query.filter_by(analysis_id=analysis.id).count() == 1
        )
        assert DocumentChunk.query.filter_by(document_id=doc.id).count() == 1
        assert ChatConversation.query.filter_by(document_id=doc.id).count() == 1
        assert ChatMessage.query.filter_by(conversation_id=conv.id).count() == 1

        # Test Cascade Deletion: deleting the User must cascade-delete Document, Analysis, Clauses, Risks, Chunks, etc.
        db.session.delete(user)
        db.session.commit()

        assert Document.query.count() == 0
        assert DocumentAnalysis.query.count() == 0
        assert ExtractedClause.query.count() == 0
        assert RiskFinding.query.count() == 0
        assert ExtractedInformation.query.count() == 0
        assert MissingClauseWarning.query.count() == 0
        assert DocumentChunk.query.count() == 0
        assert ChatConversation.query.count() == 0
        assert ChatMessage.query.count() == 0
