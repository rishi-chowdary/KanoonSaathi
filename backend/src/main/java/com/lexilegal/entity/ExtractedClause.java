package com.lexilegal.entity;

import jakarta.persistence.*;
import java.util.UUID;

@Entity
@Table(name = "extracted_clauses")
public class ExtractedClause extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "analysis_id", nullable = false)
    private DocumentAnalysis analysis;

    @Column(nullable = false)
    private String title;

    @Column(nullable = false, length = 100)
    private String category;

    @Column(name = "custom_label", length = 100)
    private String customLabel;

    @Column(name = "original_text", nullable = false, columnDefinition = "TEXT")
    private String originalText;

    @Column(name = "simplified_simple", nullable = false, columnDefinition = "TEXT")
    private String simplifiedSimple;

    @Column(name = "simplified_detailed", nullable = false, columnDefinition = "TEXT")
    private String simplifiedDetailed;

    @Column(name = "simplified_professional", nullable = false, columnDefinition = "TEXT")
    private String simplifiedProfessional;

    @Column(nullable = false, length = 20)
    private String importance;

    @Column(name = "affected_party")
    private String affectedParty;

    @Column(name = "source_page", nullable = false)
    private Integer sourcePage;

    @Column(name = "section_reference", length = 100)
    private String sectionReference;

    @Column(name = "evidence_quote", nullable = false, columnDefinition = "TEXT")
    private String evidenceQuote;

    @Column(name = "quote_verified", nullable = false)
    private Boolean quoteVerified = false;

    @Column(nullable = false, length = 30)
    private String provenance = "EXTRACTED";

    public ExtractedClause() {}

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public DocumentAnalysis getAnalysis() {
        return analysis;
    }

    public void setAnalysis(DocumentAnalysis analysis) {
        this.analysis = analysis;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getCustomLabel() {
        return customLabel;
    }

    public void setCustomLabel(String customLabel) {
        this.customLabel = customLabel;
    }

    public String getOriginalText() {
        return originalText;
    }

    public void setOriginalText(String originalText) {
        this.originalText = originalText;
    }

    public String getSimplifiedSimple() {
        return simplifiedSimple;
    }

    public void setSimplifiedSimple(String simplifiedSimple) {
        this.simplifiedSimple = simplifiedSimple;
    }

    public String getSimplifiedDetailed() {
        return simplifiedDetailed;
    }

    public void setSimplifiedDetailed(String simplifiedDetailed) {
        this.simplifiedDetailed = simplifiedDetailed;
    }

    public String getSimplifiedProfessional() {
        return simplifiedProfessional;
    }

    public void setSimplifiedProfessional(String simplifiedProfessional) {
        this.simplifiedProfessional = simplifiedProfessional;
    }

    public String getImportance() {
        return importance;
    }

    public void setImportance(String importance) {
        this.importance = importance;
    }

    public String getAffectedParty() {
        return affectedParty;
    }

    public void setAffectedParty(String affectedParty) {
        this.affectedParty = affectedParty;
    }

    public Integer getSourcePage() {
        return sourcePage;
    }

    public void setSourcePage(Integer sourcePage) {
        this.sourcePage = sourcePage;
    }

    public String getSectionReference() {
        return sectionReference;
    }

    public void setSectionReference(String sectionReference) {
        this.sectionReference = sectionReference;
    }

    public String getEvidenceQuote() {
        return evidenceQuote;
    }

    public void setEvidenceQuote(String evidenceQuote) {
        this.evidenceQuote = evidenceQuote;
    }

    public Boolean getQuoteVerified() {
        return quoteVerified;
    }

    public void setQuoteVerified(Boolean quoteVerified) {
        this.quoteVerified = quoteVerified;
    }

    public String getProvenance() {
        return provenance;
    }

    public void setProvenance(String provenance) {
        this.provenance = provenance;
    }
}

