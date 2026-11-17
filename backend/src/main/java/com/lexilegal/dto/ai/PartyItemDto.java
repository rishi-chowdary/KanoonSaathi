package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public class PartyItemDto {
    private String name;
    private String role;

    @JsonProperty("evidence_quote")
    private String evidenceQuote;

    @JsonProperty("source_page")
    private Integer sourcePage;

    @JsonProperty("quote_verified")
    private Boolean quoteVerified;

    private String provenance;

    public PartyItemDto() {}

    public PartyItemDto(String name, String role, String evidenceQuote, Integer sourcePage, Boolean quoteVerified, String provenance) {
        this.name = name;
        this.role = role;
        this.evidenceQuote = evidenceQuote;
        this.sourcePage = sourcePage;
        this.quoteVerified = quoteVerified;
        this.provenance = provenance;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getRole() {
        return role;
    }

    public void setRole(String role) {
        this.role = role;
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

