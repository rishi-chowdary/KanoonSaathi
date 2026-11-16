package com.lexilegal.dto.response;

import java.util.UUID;

public class DocumentUploadResponse {
    private UUID id;
    private String originalFilename;
    private Long fileSize;
    private String status;
    private boolean duplicate;

    public DocumentUploadResponse() {}

    public DocumentUploadResponse(UUID id, String originalFilename, Long fileSize, String status, boolean duplicate) {
        this.id = id;
        this.originalFilename = originalFilename;
        this.fileSize = fileSize;
        this.status = status;
        this.duplicate = duplicate;
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

    public Long getFileSize() {
        return fileSize;
    }

    public void setFileSize(Long fileSize) {
        this.fileSize = fileSize;
    }

    public String getStatus() {
        return status;
    }

    public void setStatus(String status) {
        this.status = status;
    }

    public boolean isDuplicate() {
        return duplicate;
    }

    public void setDuplicate(boolean duplicate) {
        this.duplicate = duplicate;
    }
}

