package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public class GroundedItemDto {
    private String text;

    @JsonProperty("evidence_quote")
    private String evidenceQuote;

    @JsonProperty("source_page")
    private Integer sourcePage;

    @JsonProperty("quote_verified")
    private Boolean quoteVerified;

    private String provenance;

    public GroundedItemDto() {}

    public GroundedItemDto(String text, String evidenceQuote, Integer sourcePage, Boolean quoteVerified, String provenance) {
        this.text = text;
        this.evidenceQuote = evidenceQuote;
        this.sourcePage = sourcePage;
        this.quoteVerified = quoteVerified;
        this.provenance = provenance;
    }

    public String getText() {
        return text;
    }

    public void setText(String text) {
        this.text = text;
    }

    public String getEvidenceQuote() {
        return evidenceQuote;
    }

    public void setEvidenceQuote(String evidenceQuote) {
        this.evidenceQuote = evidenceQuote;
    }

    public Integer getSourcePage() {
        return sourcePage;
    }

    public void setSourcePage(Integer sourcePage) {
        this.sourcePage = sourcePage;
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
