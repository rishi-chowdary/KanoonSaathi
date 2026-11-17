package com.lexilegal.dto.response;

import com.lexilegal.entity.MissingClauseWarning;
import java.time.Instant;
import java.util.UUID;

public class MissingClauseWarningResponse {

    private UUID id;
    private String category;
    private String clauseName;
    private String whyItMatters;
    private String typicalProvision;
    private String riskLevel;
    private String label;
    private Instant createdAt;

    public MissingClauseWarningResponse() {}

    public static MissingClauseWarningResponse fromEntity(MissingClauseWarning entity) {
        MissingClauseWarningResponse resp = new MissingClauseWarningResponse();
        resp.setId(entity.getId());
        resp.setCategory(entity.getCategory());
        resp.setClauseName(entity.getClauseName());
        resp.setWhyItMatters(entity.getWhyItMatters());
        resp.setTypicalProvision(entity.getTypicalProvision());
        resp.setRiskLevel(entity.getRiskLevel());
        resp.setLabel(entity.getLabel() != null ? entity.getLabel() : "Possible omission");
        resp.setCreatedAt(entity.getCreatedAt());
        return resp;
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

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

    public Instant getCreatedAt() { return createdAt; }
    public void setCreatedAt(Instant createdAt) { this.createdAt = createdAt; }
}

