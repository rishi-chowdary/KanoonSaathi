package com.lexilegal.dto.response;

import java.time.Instant;
import java.util.UUID;

public class DocumentResponse {
    private UUID id;
    private String originalFilename;
    private String fileType;
    private Long fileSize;
    private Integer pageCount;
    private Boolean isScanned;
    private String status;
    private String failureReason;
    private Instant createdAt;
    private Instant updatedAt;

    public DocumentResponse() {}

    public DocumentResponse(UUID id, String originalFilename, String fileType, Long fileSize,
                            Integer pageCount, Boolean isScanned, String status,
                            String failureReason, Instant createdAt, Instant updatedAt) {
        this.id = id;
        this.originalFilename = originalFilename;
        this.fileType = fileType;
        this.fileSize = fileSize;
        this.pageCount = pageCount;
        this.isScanned = isScanned;
        this.status = status;
        this.failureReason = failureReason;
        this.createdAt = createdAt;
        this.updatedAt = updatedAt;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getOriginalFilename() {
        return originalFilename;
    }

    public void setOriginalFilename(String originalFilename) {
        this.originalFilename = originalFilename;
    }

    public String getFileType() {
        return fileType;
    }

    public void setFileType(String fileType) {
        this.fileType = fileType;
    }

    public Long getFileSize() {
        return fileSize;
    }

    public void setFileSize(Long fileSize) {
        this.fileSize = fileSize;
    }

    public Integer getPageCount() {
        return pageCount;
    }

    public void setPageCount(Integer pageCount) {
        this.pageCount = pageCount;
    }

    public Boolean getIsScanned() {
        return isScanned;
    }

    public void setIsScanned(Boolean isScanned) {
        this.isScanned = isScanned;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public String getFailureReason() {
        return failureReason;
    }

    public void setFailureReason(String failureReason) {
        this.failureReason = failureReason;
    }

    public Instant getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(Instant createdAt) {
        this.createdAt = createdAt;
    }

    public Instant getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(Instant updatedAt) {
        this.updatedAt = updatedAt;
    }
}
