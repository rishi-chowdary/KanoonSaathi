package com.lexilegal.dto.ai;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.ArrayList;
import java.util.List;

public class KeyInfoResponseDto {

    @JsonProperty("document_id")
    private String documentId;

    @JsonProperty("contract_amount")
    private FactItemDto contractAmount = new FactItemDto();

    @JsonProperty("payment_deadlines")
    private FactItemDto paymentDeadlines = new FactItemDto();

    private FactItemDto penalties = new FactItemDto();

    @JsonProperty("start_date")
    private FactItemDto startDate = new FactItemDto();

    @JsonProperty("end_date")
    private FactItemDto endDate = new FactItemDto();

    @JsonProperty("renewal_date")
    private FactItemDto renewalDate = new FactItemDto();

    @JsonProperty("notice_period")
    private FactItemDto noticePeriod = new FactItemDto();

    @JsonProperty("termination_conditions")
    private FactItemDto terminationConditions = new FactItemDto();

    private List<String> obligations = new ArrayList<>();

    @JsonProperty("important_dates")
    private List<ImportantDateDto> importantDates = new ArrayList<>();

    public KeyInfoResponseDto() {}

    public String getDocumentId() { return documentId; }
    public void setDocumentId(String documentId) { this.documentId = documentId; }

    public FactItemDto getContractAmount() { return contractAmount; }
    public void setContractAmount(FactItemDto contractAmount) { this.contractAmount = contractAmount; }

    public FactItemDto getPaymentDeadlines() { return paymentDeadlines; }
    public void setPaymentDeadlines(FactItemDto paymentDeadlines) { this.paymentDeadlines = paymentDeadlines; }

    public FactItemDto getPenalties() { return penalties; }
    public void setPenalties(FactItemDto penalties) { this.penalties = penalties; }

    public FactItemDto getStartDate() { return startDate; }
    public void setStartDate(FactItemDto startDate) { this.startDate = startDate; }

    public FactItemDto getEndDate() { return endDate; }
    public void setEndDate(FactItemDto endDate) { this.endDate = endDate; }

    public FactItemDto getRenewalDate() { return renewalDate; }
    public void setRenewalDate(FactItemDto renewalDate) { this.renewalDate = renewalDate; }

    public FactItemDto getNoticePeriod() { return noticePeriod; }
    public void setNoticePeriod(FactItemDto noticePeriod) { this.noticePeriod = noticePeriod; }

    public FactItemDto getTerminationConditions() { return terminationConditions; }
    public void setTerminationConditions(FactItemDto terminationConditions) { this.terminationConditions = terminationConditions; }

    public List<String> getObligations() { return obligations; }
    public void setObligations(List<String> obligations) { this.obligations = obligations; }

    public List<ImportantDateDto> getImportantDates() { return importantDates; }
    public void setImportantDates(List<ImportantDateDto> importantDates) { this.importantDates = importantDates; }
}

