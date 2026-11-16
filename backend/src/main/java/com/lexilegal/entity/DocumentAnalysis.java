package com.lexilegal.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.math.BigDecimal;
import java.util.UUID;

@Entity
@Table(name = "document_analyses")
public class DocumentAnalysis extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "document_id", nullable = false, unique = true)
    private Document document;

    @Column
    private String title;

    @Column(name = "document_type", length = 100)
    private String documentType;

    @Column(columnDefinition = "TEXT")
    private String purpose;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb", nullable = false)
    private String parties = "[]";

    @Column(name = "summary_short", nullable = false, columnDefinition = "TEXT")
    private String summaryShort;

    @Column(name = "summary_detailed", nullable = false, columnDefinition = "TEXT")
    private String summaryDetailed;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "main_conditions", columnDefinition = "jsonb", nullable = false)
    private String mainConditions = "[]";

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "obligations_summary", columnDefinition = "jsonb", nullable = false)
    private String obligationsSummary = "[]";

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "financial_terms_summary", columnDefinition = "jsonb", nullable = false)
    private String financialTermsSummary = "[]";

    @Column(name = "llm_provider", nullable = false, length = 50)
    private String llmProvider;

    @Column(name = "llm_model", nullable = false, length = 100)
    private String llmModel;

    @Column(name = "verification_rate", nullable = false, precision = 5, scale = 2)
    private BigDecimal verificationRate = BigDecimal.ZERO;

    public DocumentAnalysis() {}

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public Document getDocument() {
        return document;
    }

    public void setDocument(Document document) {
        this.document = document;
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

    public String getSummaryShort() {
        return summaryShort;
    }

    public void setSummaryShort(String summaryShort) {
        this.summaryShort = summaryShort;
    }

    public String getSummaryDetailed() {
        return summaryDetailed;
    }

    public void setSummaryDetailed(String summaryDetailed) {
        this.summaryDetailed = summaryDetailed;
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

    public void setObligationsSummary(String obligationsSummary) {
        this.obligationsSummary = obligationsSummary;
    }

    public String getFinancialTermsSummary() {
        return financialTermsSummary;
    }

    public void setFinancialTermsSummary(String financialTermsSummary) {
        this.financialTermsSummary = financialTermsSummary;
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

    public BigDecimal getVerificationRate() {
        return verificationRate;
    }

    public void setVerificationRate(BigDecimal verificationRate) {
        this.verificationRate = verificationRate;
    }
}
