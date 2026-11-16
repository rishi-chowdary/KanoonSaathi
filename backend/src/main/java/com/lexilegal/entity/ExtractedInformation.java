package com.lexilegal.entity;

import jakarta.persistence.*;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.util.UUID;

@Entity
@Table(name = "extracted_information")
public class ExtractedInformation extends BaseEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @OneToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "analysis_id", nullable = false, unique = true)
    private DocumentAnalysis analysis;

    @Column(name = "contract_amount", nullable = false)
    private String contractAmount = "Not specified";

    @Column(name = "contract_amount_page")
    private Integer contractAmountPage;

    @Column(name = "payment_deadlines", nullable = false, columnDefinition = "TEXT")
    private String paymentDeadlines = "Not specified";

    @Column(name = "payment_deadlines_page")
    private Integer paymentDeadlinesPage;

    @Column(nullable = false, columnDefinition = "TEXT")
    private String penalties = "Not specified";

    @Column(name = "penalties_page")
    private Integer penaltiesPage;

    @Column(name = "start_date", nullable = false, length = 100)
    private String startDate = "Not specified";

    @Column(name = "start_date_page")
    private Integer startDatePage;

    @Column(name = "end_date", nullable = false, length = 100)
    private String endDate = "Not specified";

    @Column(name = "end_date_page")
    private Integer endDatePage;

    @Column(name = "renewal_date", nullable = false, length = 100)
    private String renewalDate = "Not specified";

    @Column(name = "renewal_date_page")
    private Integer renewalDatePage;

    @Column(name = "notice_period", nullable = false)
    private String noticePeriod = "Not specified";

    @Column(name = "notice_period_page")
    private Integer noticePeriodPage;

    @Column(name = "termination_conditions", nullable = false, columnDefinition = "TEXT")
    private String terminationConditions = "Not specified";

    @Column(name = "termination_conditions_page")
    private Integer terminationConditionsPage;

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(columnDefinition = "jsonb", nullable = false)
    private String obligations = "[]";

    @JdbcTypeCode(SqlTypes.JSON)
    @Column(name = "important_dates", columnDefinition = "jsonb", nullable = false)
    private String importantDates = "[]";

    public ExtractedInformation() {}

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

    public String getContractAmount() {
        return contractAmount;
    }

    public void setContractAmount(String contractAmount) {
        this.contractAmount = contractAmount;
    }

    public Integer getContractAmountPage() {
        return contractAmountPage;
    }

    public void setContractAmountPage(Integer contractAmountPage) {
        this.contractAmountPage = contractAmountPage;
    }

    public String getPaymentDeadlines() {
        return paymentDeadlines;
    }

    public void setPaymentDeadlines(String paymentDeadlines) {
        this.paymentDeadlines = paymentDeadlines;
    }

    public Integer getPaymentDeadlinesPage() {
        return paymentDeadlinesPage;
    }

    public void setPaymentDeadlinesPage(Integer paymentDeadlinesPage) {
        this.paymentDeadlinesPage = paymentDeadlinesPage;
    }

    public String getPenalties() {
        return penalties;
    }

    public void setPenalties(String penalties) {
        this.penalties = penalties;
    }

    public Integer getPenaltiesPage() {
        return penaltiesPage;
    }

    public void setPenaltiesPage(Integer penaltiesPage) {
        this.penaltiesPage = penaltiesPage;
    }

    public String getStartDate() {
        return startDate;
    }

    public void setStartDate(String startDate) {
        this.startDate = startDate;
    }

    public Integer getStartDatePage() {
        return startDatePage;
    }

    public void setStartDatePage(Integer startDatePage) {
        this.startDatePage = startDatePage;
    }

    public String getEndDate() {
        return endDate;
    }

    public void setEndDate(String endDate) {
        this.endDate = endDate;
    }

    public Integer getEndDatePage() {
        return endDatePage;
    }

    public void setEndDatePage(Integer endDatePage) {
        this.endDatePage = endDatePage;
    }

    public String getRenewalDate() {
        return renewalDate;
    }

    public void setRenewalDate(String renewalDate) {
        this.renewalDate = renewalDate;
    }

    public Integer getRenewalDatePage() {
        return renewalDatePage;
    }

    public void setRenewalDatePage(Integer renewalDatePage) {
        this.renewalDatePage = renewalDatePage;
    }

    public String getNoticePeriod() {
        return noticePeriod;
    }

    public void setNoticePeriod(String noticePeriod) {
        this.noticePeriod = noticePeriod;
    }

    public Integer getNoticePeriodPage() {
        return noticePeriodPage;
    }

    public void setNoticePeriodPage(Integer noticePeriodPage) {
        this.noticePeriodPage = noticePeriodPage;
    }

    public String getTerminationConditions() {
        return terminationConditions;
    }

    public void setTerminationConditions(String terminationConditions) {
        this.terminationConditions = terminationConditions;
    }

    public Integer getTerminationConditionsPage() {
        return terminationConditionsPage;
    }

    public void setTerminationConditionsPage(Integer terminationConditionsPage) {
        this.terminationConditionsPage = terminationConditionsPage;
    }

    public String getObligations() {
        return obligations;
    }

    public void setObligations(String obligations) {
        this.obligations = obligations;
    }

    public String getImportantDates() {
        return importantDates;
    }

    public void setImportantDates(String importantDates) {
        this.importantDates = importantDates;
    }
}
