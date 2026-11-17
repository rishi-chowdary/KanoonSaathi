package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;

public class MissingProvisionItemDto {

    private String category;

    @JsonProperty("clause_name")
    private String clauseName;

    @JsonProperty("why_it_matters")
    private String whyItMatters;

    @JsonProperty("typical_provision")
    private String typicalProvision;

    @JsonProperty("risk_level")
    private String riskLevel = "MEDIUM";

    private String label = "Possible omission";

    public MissingProvisionItemDto() {}

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getClauseName() { return clauseName; }
    public void setClauseName(String clauseName) { this.clauseName = clauseName; }

    public String getWhyItMatters() { return whyItMatters; }
    public void setWhyItMatters(String whyItMatters) { this.whyItMatters = whyItMatters; }

    public String getTypicalProvision() { return typicalProvision; }
    public void setTypicalProvision(String typicalProvision) { this.typicalProvision = typicalProvision; }

    public String getRiskLevel() { return riskLevel; }
    public void setRiskLevel(String riskLevel) { this.riskLevel = riskLevel; }

    public String getLabel() { return label; }
    public void setLabel(String label) { this.label = label; }
}

