package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class RiskItemDto {

    private String title;
    private String category;
    private String level;

    @JsonProperty("original_clause")
    private String originalClause;

    @JsonProperty("evidence_quote")
    private String evidenceQuote;

    @JsonProperty("source_page")
    private Integer sourcePage = 1;

    @JsonProperty("quote_verified")
    private Boolean quoteVerified = false;

    private String explanation;

    @JsonProperty("why_it_matters")
    private String whyItMatters;

    @JsonProperty("possible_consequences")
    private String possibleConsequences;

    @JsonProperty("suggested_questions")
    private List<String> suggestedQuestions = new ArrayList<>();

    @JsonProperty("jurisdiction_caveat")
    private String jurisdictionCaveat;

    private String provenance = "AI_INTERPRETATION";

    public RiskItemDto() {}

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getLevel() { return level; }
    public void setLevel(String level) { this.level = level; }

    public String getOriginalClause() { return originalClause; }
    public void setOriginalClause(String originalClause) { this.originalClause = originalClause; }

    public String getEvidenceQuote() { return evidenceQuote; }
    public void setEvidenceQuote(String evidenceQuote) { this.evidenceQuote = evidenceQuote; }

    public Integer getSourcePage() { return sourcePage; }
    public void setSourcePage(Integer sourcePage) { this.sourcePage = sourcePage; }

    public Boolean getQuoteVerified() { return quoteVerified; }
    public void setQuoteVerified(Boolean quoteVerified) { this.quoteVerified = quoteVerified; }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }

    public String getWhyItMatters() { return whyItMatters; }
    public void setWhyItMatters(String whyItMatters) { this.whyItMatters = whyItMatters; }

    public String getPossibleConsequences() { return possibleConsequences; }
    public void setPossibleConsequences(String possibleConsequences) { this.possibleConsequences = possibleConsequences; }

    public List<String> getSuggestedQuestions() { return suggestedQuestions; }
    public void setSuggestedQuestions(List<String> suggestedQuestions) { this.suggestedQuestions = suggestedQuestions; }

    public String getJurisdictionCaveat() { return jurisdictionCaveat; }
    public void setJurisdictionCaveat(String jurisdictionCaveat) { this.jurisdictionCaveat = jurisdictionCaveat; }

    public String getProvenance() { return provenance; }
    public void setProvenance(String provenance) { this.provenance = provenance; }
}

