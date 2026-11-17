package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public class ImportantDateDto {

    private String event;

    @JsonProperty("date_value")
    private String dateValue;

    @JsonProperty("source_page")
    private Integer sourcePage;

    @JsonProperty("evidence_quote")
    private String evidenceQuote;

    @JsonProperty("quote_verified")
    private Boolean quoteVerified = false;

    public ImportantDateDto() {}

    public ImportantDateDto(String event, String dateValue, Integer sourcePage, String evidenceQuote, Boolean quoteVerified) {
        this.event = event;
        this.dateValue = dateValue;
        this.sourcePage = sourcePage;
        this.evidenceQuote = evidenceQuote;
        this.quoteVerified = quoteVerified;
    }

    public String getEvent() { return event; }
    public void setEvent(String event) { this.event = event; }

    public String getDateValue() { return dateValue; }
    public void setDateValue(String dateValue) { this.dateValue = dateValue; }

    public Integer getSourcePage() { return sourcePage; }
    public void setSourcePage(Integer sourcePage) { this.sourcePage = sourcePage; }

    public String getEvidenceQuote() { return evidenceQuote; }
    public void setEvidenceQuote(String evidenceQuote) { this.evidenceQuote = evidenceQuote; }

    public Boolean getQuoteVerified() { return quoteVerified; }
    public void setQuoteVerified(Boolean quoteVerified) { this.quoteVerified = quoteVerified; }
}

