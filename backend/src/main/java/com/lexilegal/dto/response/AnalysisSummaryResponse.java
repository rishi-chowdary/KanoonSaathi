package com.lexilegal.dto.response;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonRawValue;
import java.math.BigDecimal;
import java.time.Instant;
import java.util.UUID;

public class AnalysisSummaryResponse {

    private UUID id;
    private UUID documentId;
    private String title;
    private String documentType;
    private String purpose;

    @JsonRawValue
    private String parties;

    private String shortSummary;
    private String detailedSummary;

    @JsonRawValue
    private String mainConditions;

    @JsonRawValue
    private String obligationsSummary;

    @JsonRawValue
    private String financialTermsSummary;

    private BigDecimal verificationRate;
    private String llmProvider;
    private String llmModel;
    private Instant createdAt;
    private Instant updatedAt;

    public AnalysisSummaryResponse() {}

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public UUID getDocumentId() {
        return documentId;
    }

    public void setDocumentId(UUID documentId) {
        this.documentId = documentId;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getDocumentType() {
        return documentType;
    }

    public void setDocumentType(String documentType) {
        this.documentType = documentType;
    }

    public String getPurpose() {
        return purpose;
    }

    public void setPurpose(String purpose) {
        this.purpose = purpose;
    }

    public String getParties() {
        return parties;
    }

    public void setParties(String parties) {
        this.parties = parties;
    }

    public String getShortSummary() {
        return shortSummary;
    }

    public void setShortSummary(String shortSummary) {
        this.shortSummary = shortSummary;
    }

    public String getDetailedSummary() {
        return detailedSummary;
    }

    public void setDetailedSummary(String detailedSummary) {
        this.detailedSummary = detailedSummary;
    }

    public String getMainConditions() {
        return mainConditions;
    }

    public void setMainConditions(String mainConditions) {
        this.mainConditions = mainConditions;
    }

    public String getObligationsSummary() {
        return obligationsSummary;
    }

    @JsonRawValue
    @JsonProperty("obligations")
    public String getObligations() {
        return obligationsSummary;
    }

    public void setObligationsSummary(String obligationsSummary) {
        this.obligationsSummary = obligationsSummary;
    }

    public String getFinancialTermsSummary() {
        return financialTermsSummary;
    }

    @JsonRawValue
    @JsonProperty("financialTerms")
    public String getFinancialTerms() {
        return financialTermsSummary;
    }

    public void setFinancialTermsSummary(String financialTermsSummary) {
        this.financialTermsSummary = financialTermsSummary;
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

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
