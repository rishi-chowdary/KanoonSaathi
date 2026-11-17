package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class RiskAnalysisResponseDto {

    @JsonProperty("document_id")
    private String documentId;

    private List<RiskItemDto> risks = new ArrayList<>();

    @JsonProperty("total_risks")
    private Integer totalRisks = 0;

    @JsonProperty("high_risks")
    private Integer highRisks = 0;

    @JsonProperty("medium_risks")
    private Integer mediumRisks = 0;

    @JsonProperty("low_risks")
    private Integer lowRisks = 0;

    @JsonProperty("informational_risks")
    private Integer informationalRisks = 0;

    @JsonProperty("governing_law_found")
    private Boolean governingLawFound = true;

    @JsonProperty("jurisdiction_warning")
    private String jurisdictionWarning;

    @JsonProperty("overall_risk_score")
    private Double overallRiskScore = 0.0;

    public RiskAnalysisResponseDto() {}

    public String getDocumentId() { return documentId; }
    public void setDocumentId(String documentId) { this.documentId = documentId; }

    public List<RiskItemDto> getRisks() { return risks; }
    public void setRisks(List<RiskItemDto> risks) { this.risks = risks; }

    public Integer getTotalRisks() { return totalRisks; }
    public void setTotalRisks(Integer totalRisks) { this.totalRisks = totalRisks; }

    public Integer getHighRisks() { return highRisks; }
    public void setHighRisks(Integer highRisks) { this.highRisks = highRisks; }

    public Integer getMediumRisks() { return mediumRisks; }
    public void setMediumRisks(Integer mediumRisks) { this.mediumRisks = mediumRisks; }

    public Integer getLowRisks() { return lowRisks; }
    public void setLowRisks(Integer lowRisks) { this.lowRisks = lowRisks; }

    public Integer getInformationalRisks() { return informationalRisks; }
    public void setInformationalRisks(Integer informationalRisks) { this.informationalRisks = informationalRisks; }

    public Boolean getGoverningLawFound() { return governingLawFound; }
    public void setGoverningLawFound(Boolean governingLawFound) { this.governingLawFound = governingLawFound; }

    public String getJurisdictionWarning() { return jurisdictionWarning; }
    public void setJurisdictionWarning(String jurisdictionWarning) { this.jurisdictionWarning = jurisdictionWarning; }

    public Double getOverallRiskScore() { return overallRiskScore; }
    public void setOverallRiskScore(Double overallRiskScore) { this.overallRiskScore = overallRiskScore; }
}

