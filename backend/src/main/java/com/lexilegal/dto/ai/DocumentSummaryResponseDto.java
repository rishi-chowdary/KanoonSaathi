package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;

public class DocumentSummaryResponseDto {

    private String title;

    @JsonProperty("document_type")
    private String documentType;

    private String purpose;

    private List<PartyItemDto> parties = new ArrayList<>();

    @JsonProperty("main_conditions")
    private List<GroundedItemDto> mainConditions = new ArrayList<>();

    private List<GroundedItemDto> obligations = new ArrayList<>();

    @JsonProperty("financial_terms")
    private List<GroundedItemDto> financialTerms = new ArrayList<>();

    @JsonProperty("short_summary")
    private String shortSummary;

    @JsonProperty("detailed_summary")
    private String detailedSummary;

    @JsonProperty("verification_rate")
    private BigDecimal verificationRate = BigDecimal.ZERO;

    @JsonProperty("llm_provider")
    private String llmProvider;

    @JsonProperty("llm_model")
    private String llmModel;

    private List<String> warnings = new ArrayList<>();

    public DocumentSummaryResponseDto() {}

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

    public List<PartyItemDto> getParties() {
        return parties;
    }

    public void setParties(List<PartyItemDto> parties) {
        this.parties = parties;
    }

    public List<GroundedItemDto> getMainConditions() {
        return mainConditions;
    }

    public void setMainConditions(List<GroundedItemDto> mainConditions) {
        this.mainConditions = mainConditions;
    }

    public List<GroundedItemDto> getObligations() {
        return obligations;
    }

    public void setObligations(List<GroundedItemDto> obligations) {
        this.obligations = obligations;
    }

    public List<GroundedItemDto> getFinancialTerms() {
        return financialTerms;
    }

    public void setFinancialTerms(List<GroundedItemDto> financialTerms) {
        this.financialTerms = financialTerms;
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
