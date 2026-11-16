package com.lexilegal.dto.response;

import java.time.Instant;
import java.util.UUID;

public class DocumentStatusResponse {
    private UUID id;
    private String status;
    private Integer pageCount;
    private String failureReason;
    private Instant updatedAt;

    public DocumentStatusResponse() {}

    public DocumentStatusResponse(UUID id, String status, Integer pageCount, String failureReason, Instant updatedAt) {
        this.id = id;
        this.status = status;
        this.pageCount = pageCount;
        this.failureReason = failureReason;
        this.updatedAt = updatedAt;
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

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}

