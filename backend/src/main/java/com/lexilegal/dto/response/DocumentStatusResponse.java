package com.lexilegal.dto.response;

import java.time.Instant;
import java.util.UUID;

public class DocumentStatusResponse {
    private UUID id;
    private String status;
    private Integer pageCount;
    private String failureReason;
    private Integer progressPercentage = 0;
    private String progressStep;
    private Boolean hasAnalysis = false;
    private Instant updatedAt;

    public DocumentStatusResponse() {}

    public DocumentStatusResponse(UUID id, String status, Integer pageCount, String failureReason, Instant updatedAt) {
        this.id = id;
        this.status = status;
        this.pageCount = pageCount;
        this.failureReason = failureReason;
        this.updatedAt = updatedAt;
        computeProgress(status);
    }

    public DocumentStatusResponse(UUID id, String status, Integer pageCount, String failureReason, Boolean hasAnalysis, Instant updatedAt) {
        this.id = id;
        this.status = status;
        this.pageCount = pageCount;
        this.failureReason = failureReason;
        this.hasAnalysis = hasAnalysis;
        this.updatedAt = updatedAt;
        computeProgress(status);
    }

    private void computeProgress(String status) {
        if (status == null) return;
        switch (status) {
            case "UPLOADED" -> {
                this.progressPercentage = 15;
                this.progressStep = "Document uploaded, queued for processing";
            }
            case "EXTRACTING" -> {
                this.progressPercentage = 40;
                this.progressStep = "Extracting text, sections, and OCR";
            }
            case "EXTRACTED" -> {
                this.progressPercentage = 65;
                this.progressStep = "Text extracted, preparing AI analysis";
            }
            case "ANALYZING" -> {
                this.progressPercentage = 80;
                this.progressStep = "Synthesizing executive summary and grounding quotes";
            }
            case "COMPLETED" -> {
                this.progressPercentage = 100;
                this.progressStep = "Analysis complete";
            }
            case "FAILED" -> {
                this.progressPercentage = 0;
                this.progressStep = "Processing failed";
            }
            default -> {
                this.progressPercentage = 50;
                this.progressStep = "Processing";
            }
        }
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
        computeProgress(status);
    }

    public Integer getPageCount() {
        return pageCount;
    }

    public void setPageCount(Integer pageCount) {
        this.pageCount = pageCount;
    }

    public String getFailureReason() {
        return failureReason;
    }

    public void setFailureReason(String failureReason) {
        this.failureReason = failureReason;
    }

    public Integer getProgressPercentage() {
        return progressPercentage;
    }

    public void setProgressPercentage(Integer progressPercentage) {
        this.progressPercentage = progressPercentage;
    }

    public String getProgressStep() {
        return progressStep;
    }

    public void setProgressStep(String progressStep) {
        this.progressStep = progressStep;
    }

    public Boolean getHasAnalysis() {
        return hasAnalysis;
    }

    public void setHasAnalysis(Boolean hasAnalysis) {
        this.hasAnalysis = hasAnalysis;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
