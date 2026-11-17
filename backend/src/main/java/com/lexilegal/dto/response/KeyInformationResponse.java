package com.lexilegal.dto.response;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.entity.ExtractedInformation;

import java.time.Instant;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class KeyInformationResponse {

    private static final ObjectMapper OBJECT_MAPPER = new ObjectMapper();

    private UUID id;
    private String contractAmount;
    private Integer contractAmountPage;
    private String paymentDeadlines;
    private Integer paymentDeadlinesPage;
    private String penalties;
    private Integer penaltiesPage;
    private String startDate;
    private Integer startDatePage;
    private String endDate;
    private Integer endDatePage;
    private String renewalDate;
    private Integer renewalDatePage;
    private String noticePeriod;
    private Integer noticePeriodPage;
    private String terminationConditions;
    private Integer terminationConditionsPage;
    private List<String> obligations = new ArrayList<>();
    private List<Map<String, Object>> importantDates = new ArrayList<>();
    private Instant updatedAt;

    public KeyInformationResponse() {}

    public static KeyInformationResponse fromEntity(ExtractedInformation entity) {
        KeyInformationResponse resp = new KeyInformationResponse();
        resp.setId(entity.getId());
        resp.setContractAmount(entity.getContractAmount());
        resp.setContractAmountPage(entity.getContractAmountPage());
        resp.setPaymentDeadlines(entity.getPaymentDeadlines());
        resp.setPaymentDeadlinesPage(entity.getPaymentDeadlinesPage());
        resp.setPenalties(entity.getPenalties());
        resp.setPenaltiesPage(entity.getPenaltiesPage());
        resp.setStartDate(entity.getStartDate());
        resp.setStartDatePage(entity.getStartDatePage());
        resp.setEndDate(entity.getEndDate());
        resp.setEndDatePage(entity.getEndDatePage());
        resp.setRenewalDate(entity.getRenewalDate());
        resp.setRenewalDatePage(entity.getRenewalDatePage());
        resp.setNoticePeriod(entity.getNoticePeriod());
        resp.setNoticePeriodPage(entity.getNoticePeriodPage());
        resp.setTerminationConditions(entity.getTerminationConditions());
        resp.setTerminationConditionsPage(entity.getTerminationConditionsPage());
        resp.setUpdatedAt(entity.getUpdatedAt());

        if (entity.getObligations() != null && !entity.getObligations().isBlank()) {
            try {
                List<String> list = OBJECT_MAPPER.readValue(
                        entity.getObligations(),
                        new TypeReference<List<String>>() {}
                );
                resp.setObligations(list);
            } catch (Exception e) {
                resp.setObligations(new ArrayList<>());
            }
        }

        if (entity.getImportantDates() != null && !entity.getImportantDates().isBlank()) {
            try {
                List<Map<String, Object>> list = OBJECT_MAPPER.readValue(
                        entity.getImportantDates(),
                        new TypeReference<List<Map<String, Object>>>() {}
                );
                resp.setImportantDates(list);
            } catch (Exception e) {
                resp.setImportantDates(new ArrayList<>());
            }
        }
        return resp;
    }

    public UUID getId() { return id; }
    public void setId(UUID id) { this.id = id; }

    public String getContractAmount() { return contractAmount; }
    public void setContractAmount(String contractAmount) { this.contractAmount = contractAmount; }

    public Integer getContractAmountPage() { return contractAmountPage; }
    public void setContractAmountPage(Integer contractAmountPage) { this.contractAmountPage = contractAmountPage; }

    public String getPaymentDeadlines() { return paymentDeadlines; }
    public void setPaymentDeadlines(String paymentDeadlines) { this.paymentDeadlines = paymentDeadlines; }

    public Integer getPaymentDeadlinesPage() { return paymentDeadlinesPage; }
    public void setPaymentDeadlinesPage(Integer paymentDeadlinesPage) { this.paymentDeadlinesPage = paymentDeadlinesPage; }

    public String getPenalties() { return penalties; }
    public void setPenalties(String penalties) { this.penalties = penalties; }

    public Integer getPenaltiesPage() { return penaltiesPage; }
    public void setPenaltiesPage(Integer penaltiesPage) { this.penaltiesPage = penaltiesPage; }

    public String getStartDate() { return startDate; }
    public void setStartDate(String startDate) { this.startDate = startDate; }

    public Integer getStartDatePage() { return startDatePage; }
    public void setStartDatePage(Integer startDatePage) { this.startDatePage = startDatePage; }

    public String getEndDate() { return endDate; }
    public void setEndDate(String endDate) { this.endDate = endDate; }

    public Integer getEndDatePage() { return endDatePage; }
    public void setEndDatePage(Integer endDatePage) { this.endDatePage = endDatePage; }

    public String getRenewalDate() { return renewalDate; }
    public void setRenewalDate(String renewalDate) { this.renewalDate = renewalDate; }

    public Integer getRenewalDatePage() { return renewalDatePage; }
    public void setRenewalDatePage(Integer renewalDatePage) { this.renewalDatePage = renewalDatePage; }

    public String getNoticePeriod() { return noticePeriod; }
    public void setNoticePeriod(String noticePeriod) { this.noticePeriod = noticePeriod; }

    public Integer getNoticePeriodPage() { return noticePeriodPage; }
    public void setNoticePeriodPage(Integer noticePeriodPage) { this.noticePeriodPage = noticePeriodPage; }

    public String getTerminationConditions() { return terminationConditions; }
    public void setTerminationConditions(String terminationConditions) { this.terminationConditions = terminationConditions; }

    public Integer getTerminationConditionsPage() { return terminationConditionsPage; }
    public void setTerminationConditionsPage(Integer terminationConditionsPage) { this.terminationConditionsPage = terminationConditionsPage; }

    public List<String> getObligations() { return obligations; }
    public void setObligations(List<String> obligations) { this.obligations = obligations; }

    public List<Map<String, Object>> getImportantDates() { return importantDates; }
    public void setImportantDates(List<Map<String, Object>> importantDates) { this.importantDates = importantDates; }

    public Instant getUpdatedAt() { return updatedAt; }
    public void setUpdatedAt(Instant updatedAt) { this.updatedAt = updatedAt; }
}

