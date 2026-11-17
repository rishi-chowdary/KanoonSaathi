package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public class FactItemDto {

    private String value = "Not specified";

    @JsonProperty("source_page")
    private Integer sourcePage;

    @JsonProperty("evidence_quote")
    private String evidenceQuote;

    @JsonProperty("quote_verified")
    private Boolean quoteVerified = false;

    private String provenance = "EXTRACTED";

    public FactItemDto() {}

    public FactItemDto(String value, Integer sourcePage, String evidenceQuote, Boolean quoteVerified) {
        this.value = value;
        this.sourcePage = sourcePage;
        this.evidenceQuote = evidenceQuote;
        this.quoteVerified = quoteVerified;
    }

    public String getValue() { return value; }
    public void setValue(String value) { this.value = value; }

    public Integer getSourcePage() { return sourcePage; }
    public void setSourcePage(Integer sourcePage) { this.sourcePage = sourcePage; }

    public String getEvidenceQuote() { return evidenceQuote; }
    public void setEvidenceQuote(String evidenceQuote) { this.evidenceQuote = evidenceQuote; }

    public Boolean getQuoteVerified() { return quoteVerified; }
    public void setQuoteVerified(Boolean quoteVerified) { this.quoteVerified = quoteVerified; }

    public String getProvenance() { return provenance; }
    public void setProvenance(String provenance) { this.provenance = provenance; }
}

