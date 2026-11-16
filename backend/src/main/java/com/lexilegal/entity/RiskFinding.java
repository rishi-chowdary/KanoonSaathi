package com.lexilegal.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.UUID;

@Entity
@Table(name = "risk_findings")
public class RiskFinding extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "analysis_id", nullable = false)
    private DocumentAnalysis analysis;

    @Column(nullable = false, length = 50)
    private String category;

    @Column(nullable = false, length = 20)
    private String level;

    @Column(nullable = false)
    private String title;

    @Column(name = "original_clause", nullable = false, columnDefinition = "TEXT")
    private String originalClause;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String explanation;

    @Column(name = "why_it_matters", nullable = false, columnDefinition = "TEXT")
    private String whyItMatters;

    @Column(name = "possible_consequences", nullable = false, columnDefinition = "TEXT")
    private String possibleConsequences;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "suggested_questions", columnDefinition = "jsonb", nullable = false)
    private String suggestedQuestions = "[]";

    @Column(name = "source_page", nullable = false)
    private Integer sourcePage;

    @Column(name = "evidence_quote", nullable = false, columnDefinition = "TEXT")
    private String evidenceQuote;

    @Column(name = "quote_verified", nullable = false)
    private Boolean quoteVerified = false;

    @Column(name = "jurisdiction_caveat", columnDefinition = "TEXT")
    private String jurisdictionCaveat;

    @Column(nullable = false, length = 30)
    private String provenance = "AI_INTERPRETATION";

    public RiskFinding() {}

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

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getLevel() {
        return level;
    }

    public void setLevel(String level) {
        this.level = level;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getOriginalClause() {
        return originalClause;
    }

    public void setOriginalClause(String originalClause) {
        this.originalClause = originalClause;
    }

    public String getExplanation() {
        return explanation;
    }

    public void setExplanation(String explanation) {
        this.explanation = explanation;
    }

    public String getWhyItMatters() {
        return whyItMatters;
    }

    public void setWhyItMatters(String whyItMatters) {
        this.whyItMatters = whyItMatters;
    }

    public String getPossibleConsequences() {
        return possibleConsequences;
    }

    public void setPossibleConsequences(String possibleConsequences) {
        this.possibleConsequences = possibleConsequences;
    }

    public String getSuggestedQuestions() {
        return suggestedQuestions;
    }

    public void setSuggestedQuestions(String suggestedQuestions) {
        this.suggestedQuestions = suggestedQuestions;
    }

    public Integer getSourcePage() {
        return sourcePage;
    }

    public void setSourcePage(Integer sourcePage) {
        this.sourcePage = sourcePage;
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

    public String getJurisdictionCaveat() {
        return jurisdictionCaveat;
    }

    public void setJurisdictionCaveat(String jurisdictionCaveat) {
        this.jurisdictionCaveat = jurisdictionCaveat;
    }

    public String getProvenance() {
        return provenance;
    }

    public void setProvenance(String provenance) {
        this.provenance = provenance;
    }
}

