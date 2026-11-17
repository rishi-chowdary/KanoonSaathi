package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class ClauseItemDto {

    private String title;
    private String category;

    @JsonProperty("custom_label")
    private String customLabel;

    @JsonProperty("original_text")
    private String originalText;

    @JsonProperty("simplified_simple")
    private String simplifiedSimple;

    @JsonProperty("simplified_detailed")
    private String simplifiedDetailed;

    @JsonProperty("simplified_professional")
    private String simplifiedProfessional;

    private String importance;

    @JsonProperty("affected_party")
    private String affectedParty;

    @JsonProperty("source_page")
    private Integer sourcePage;

    @JsonProperty("section_reference")
    private String sectionReference;

    @JsonProperty("evidence_quote")
    private String evidenceQuote;

    @JsonProperty("quote_verified")
    private Boolean quoteVerified;

    private String provenance;

    @JsonProperty("numbers_dates_verified")
    private Boolean numbersDatesVerified;

    private List<String> warnings;

    public ClauseItemDto() {}

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

    public Boolean getNumbersDatesVerified() {
        return numbersDatesVerified;
    }

    public void setNumbersDatesVerified(Boolean numbersDatesVerified) {
        this.numbersDatesVerified = numbersDatesVerified;
    }

    public List<String> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }
}
