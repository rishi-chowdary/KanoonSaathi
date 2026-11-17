package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.util.List;

public class ClauseAnalysisResponseDto {

    @JsonProperty("document_id")
    private String documentId;

    private List<ClauseItemDto> clauses;

    @JsonProperty("total_clauses")
    private Integer totalClauses;

    @JsonProperty("verification_rate")
    private BigDecimal verificationRate;

    @JsonProperty("llm_provider")
    private String llmProvider;

    @JsonProperty("llm_model")
    private String llmModel;

    private List<String> warnings;

    public ClauseAnalysisResponseDto() {}

    public String getDocumentId() {
        return documentId;
    }

    public void setDocumentId(String documentId) {
        this.documentId = documentId;
    }

    public List<ClauseItemDto> getClauses() {
        return clauses;
    }

    public void setClauses(List<ClauseItemDto> clauses) {
        this.clauses = clauses;
    }

    public Integer getTotalClauses() {
        return totalClauses;
    }

    public void setTotalClauses(Integer totalClauses) {
        this.totalClauses = totalClauses;
    }

    public BigDecimal getVerificationRate() {
        return verificationRate;
    }

    public void setVerificationRate(BigDecimal verificationRate) {
        this.verificationRate = verificationRate;
    }

    public String getLlmProvider() {
        return llmProvider;
    }

    public void setLlmProvider(String llmProvider) {
        this.llmProvider = llmProvider;
    }

    public String getLlmModel() {
        return llmModel;
    }

    public void setLlmModel(String llmModel) {
        this.llmModel = llmModel;
    }

    public List<String> getWarnings() {
        return warnings;
    }

    public void setWarnings(List<String> warnings) {
        this.warnings = warnings;
    }
}

