package com.lexilegal.dto.response;

import com.lexilegal.entity.ExtractedClause;
import java.time.Instant;
import java.util.UUID;

public class ClauseResponse {

    private UUID id;
    private String title;
    private String category;
    private String customLabel;
    private String originalText;
    private String simplifiedSimple;
    private String simplifiedDetailed;
    private String simplifiedProfessional;
    private String importance;
    private String affectedParty;
    private Integer sourcePage;
    private String sectionReference;
    private String evidenceQuote;
    private Boolean quoteVerified;
    private String provenance;
    private Instant createdAt;

    public ClauseResponse() {}

    public static ClauseResponse fromEntity(ExtractedClause clause) {
        ClauseResponse res = new ClauseResponse();
        res.setId(clause.getId());
        res.setTitle(clause.getTitle());
        res.setCategory(clause.getCategory());
        res.setCustomLabel(clause.getCustomLabel());
        res.setOriginalText(clause.getOriginalText());
        res.setSimplifiedSimple(clause.getSimplifiedSimple());
        res.setSimplifiedDetailed(clause.getSimplifiedDetailed());
        res.setSimplifiedProfessional(clause.getSimplifiedProfessional());
        res.setImportance(clause.getImportance());
        res.setAffectedParty(clause.getAffectedParty());
        res.setSourcePage(clause.getSourcePage());
        res.setSectionReference(clause.getSectionReference());
        res.setEvidenceQuote(clause.getEvidenceQuote());
        res.setQuoteVerified(clause.getQuoteVerified());
        res.setProvenance(clause.getProvenance());
        res.setCreatedAt(clause.getCreatedAt());
        return res;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
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

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }
}

