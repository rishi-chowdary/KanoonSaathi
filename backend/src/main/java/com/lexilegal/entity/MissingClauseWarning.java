package com.lexilegal.entity;

import jakarta.persistence.*;
import java.util.UUID;

@Entity
@Table(name = "missing_clause_warnings")
public class MissingClauseWarning extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "analysis_id", nullable = false)
    private DocumentAnalysis analysis;

    @Column(nullable = false, length = 100)
    private String category;

    @Column(name = "clause_name", nullable = false)
    private String clauseName;

    @Column(name = "why_it_matters", nullable = false, columnDefinition = "TEXT")
    private String whyItMatters;

    @Column(name = "typical_provision", nullable = false, columnDefinition = "TEXT")
    private String typicalProvision;

    @Column(name = "risk_level", nullable = false, length = 20)
    private String riskLevel;

    @Column(nullable = false, length = 50)
    private String label = "Possible omission";

    public MissingClauseWarning() {}

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public DocumentAnalysis getAnalysis() {
        return analysis;
    }

    public void setAnalysis(DocumentAnalysis analysis) {
        this.analysis = analysis;
    }

    public String getCategory() {
        return category;
    }

    public void setCategory(String category) {
        this.category = category;
    }

    public String getClauseName() {
        return clauseName;
    }

    public void setClauseName(String clauseName) {
        this.clauseName = clauseName;
    }

    public String getWhyItMatters() {
        return whyItMatters;
    }

    public void setWhyItMatters(String whyItMatters) {
        this.whyItMatters = whyItMatters;
    }

    public String getTypicalProvision() {
        return typicalProvision;
    }

    public void setTypicalProvision(String typicalProvision) {
        this.typicalProvision = typicalProvision;
    }

    public String getRiskLevel() {
        return riskLevel;
    }

    public void setRiskLevel(String riskLevel) {
        this.riskLevel = riskLevel;
    }

    public String getLabel() {
        return label;
    }

    public void setLabel(String label) {
        this.label = label;
    }
}
