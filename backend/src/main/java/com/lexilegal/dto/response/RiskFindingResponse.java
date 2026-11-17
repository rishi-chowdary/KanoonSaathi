package com.lexilegal.dto.response;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.entity.RiskFinding;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;

public class RiskFindingResponse {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private UUID id;
    private String category;
    private String level;
    private String title;
    private String originalClause;
    private String explanation;
    private String whyItMatters;
    private String possibleConsequences;
    private List<String> suggestedQuestions = new ArrayList<>();
    private Integer sourcePage;
    private String evidenceQuote;
    private Boolean quoteVerified;
    private String jurisdictionCaveat;
    private String provenance;
    private Instant createdAt;

    public RiskFindingResponse() {}

    public static RiskFindingResponse fromEntity(RiskFinding entity) {
        RiskFindingResponse resp = new RiskFindingResponse();
        resp.setId(entity.getId());
        resp.setCategory(entity.getCategory());
        resp.setLevel(entity.getLevel());
        resp.setTitle(entity.getTitle());
        resp.setOriginalClause(entity.getOriginalClause());
        resp.setExplanation(entity.getExplanation());
        resp.setWhyItMatters(entity.getWhyItMatters());
        resp.setPossibleConsequences(entity.getPossibleConsequences());
        resp.setSourcePage(entity.getSourcePage());
        resp.setEvidenceQuote(entity.getEvidenceQuote());
        resp.setQuoteVerified(entity.getQuoteVerified());
        resp.setJurisdictionCaveat(entity.getJurisdictionCaveat());
        resp.setProvenance(entity.getProvenance());
        resp.setCreatedAt(entity.getCreatedAt());

        if (entity.getSuggestedQuestions() != null && !entity.getSuggestedQuestions().isBlank()) {
            try {
                List<String> questions = OBJECT_MAPPER.readValue(
                        entity.getSuggestedQuestions(),
                        new TypeReference<List<String>>() {}
                );
                resp.setSuggestedQuestions(questions);
            } catch (Exception e) {
                resp.setSuggestedQuestions(new ArrayList<>());
            }
        }
        return resp;
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getLevel() { return level; }
    public void setLevel(String level) { this.level = level; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getOriginalClause() { return originalClause; }
    public void setOriginalClause(String originalClause) { this.originalClause = originalClause; }

    public String getExplanation() { return explanation; }
    public void setExplanation(String explanation) { this.explanation = explanation; }

    public String getWhyItMatters() { return whyItMatters; }
    public void setWhyItMatters(String whyItMatters) { this.whyItMatters = whyItMatters; }

    public String getPossibleConsequences() { return possibleConsequences; }
    public void setPossibleConsequences(String possibleConsequences) { this.possibleConsequences = possibleConsequences; }

    public List<String> getSuggestedQuestions() { return suggestedQuestions; }
    public void setSuggestedQuestions(List<String> suggestedQuestions) { this.suggestedQuestions = suggestedQuestions; }

    public Integer getSourcePage() { return sourcePage; }
    public void setSourcePage(Integer sourcePage) { this.sourcePage = sourcePage; }

    public String getEvidenceQuote() { return evidenceQuote; }
    public void setEvidenceQuote(String evidenceQuote) { this.evidenceQuote = evidenceQuote; }

    public Boolean getQuoteVerified() { return quoteVerified; }
    public void setQuoteVerified(Boolean quoteVerified) { this.quoteVerified = quoteVerified; }

    public String getJurisdictionCaveat() { return jurisdictionCaveat; }
    public void setJurisdictionCaveat(String jurisdictionCaveat) { this.jurisdictionCaveat = jurisdictionCaveat; }

    public String getProvenance() { return provenance; }
    public void setProvenance(String provenance) { this.provenance = provenance; }

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}

