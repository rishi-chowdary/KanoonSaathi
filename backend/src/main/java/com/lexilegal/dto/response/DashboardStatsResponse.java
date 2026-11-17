package com.lexilegal.dto.response;

import java.math.BigDecimal;
import java.time.Instant;
import java.util.List;
import java.util.Map;
import java.util.UUID;

public class DashboardStatsResponse {

    private long totalDocuments;
    private long analyzedDocuments;
    private long failedDocuments;
    private long totalClauses;
    private long totalRisks;
    private Map<String, Long> riskDistributionByLevel;
    private Map<String, Long> riskDistributionByCategory;
    private List<RecentDocumentItem> recentDocuments;
    private List<RecentAnalysisItem> recentAnalyses;

    public DashboardStatsResponse() {}

    public long getTotalDocuments() {
        return totalDocuments;
    }

    public void setTotalDocuments(long totalDocuments) {
        this.totalDocuments = totalDocuments;
    }

    public long getAnalyzedDocuments() {
        return analyzedDocuments;
    }

    public void setAnalyzedDocuments(long analyzedDocuments) {
        this.analyzedDocuments = analyzedDocuments;
    }

    public long getFailedDocuments() {
        return failedDocuments;
    }

    public void setFailedDocuments(long failedDocuments) {
        this.failedDocuments = failedDocuments;
    }

    public long getTotalClauses() {
        return totalClauses;
    }

    public void setTotalClauses(long totalClauses) {
        this.totalClauses = totalClauses;
    }

    public long getTotalRisks() {
        return totalRisks;
    }

    public void setTotalRisks(long totalRisks) {
        this.totalRisks = totalRisks;
    }

    public Map<String, Long> getRiskDistributionByLevel() {
        return riskDistributionByLevel;
    }

    public void setRiskDistributionByLevel(Map<String, Long> riskDistributionByLevel) {
        this.riskDistributionByLevel = riskDistributionByLevel;
    }

    public Map<String, Long> getRiskDistributionByCategory() {
        return riskDistributionByCategory;
    }

    public void setRiskDistributionByCategory(Map<String, Long> riskDistributionByCategory) {
        this.riskDistributionByCategory = riskDistributionByCategory;
    }

    public List<RecentDocumentItem> getRecentDocuments() {
        return recentDocuments;
    }

    public void setRecentDocuments(List<RecentDocumentItem> recentDocuments) {
        this.recentDocuments = recentDocuments;
    }

    public List<RecentAnalysisItem> getRecentAnalyses() {
        return recentAnalyses;
    }

    public void setRecentAnalyses(List<RecentAnalysisItem> recentAnalyses) {
        this.recentAnalyses = recentAnalyses;
    }

    public static class RecentDocumentItem {
        private UUID id;
        private String originalFilename;
        private String fileType;
        private Long fileSize;
        private String status;
        private Integer pageCount;
        private Instant createdAt;

        public RecentDocumentItem() {}

        public RecentDocumentItem(UUID id, String originalFilename, String fileType, Long fileSize, String status, Integer pageCount, Instant createdAt) {
            this.id = id;
            this.originalFilename = originalFilename;
            this.fileType = fileType;
            this.fileSize = fileSize;
            this.status = status;
            this.pageCount = pageCount;
            this.createdAt = createdAt;
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

        public Instant getCreatedAt() {
            return createdAt;
        }

        public void setCreatedAt(Instant createdAt) {
            this.createdAt = createdAt;
        }
    }

    public static class RecentAnalysisItem {
        private UUID id;
        private UUID documentId;
        private String title;
        private String documentType;
        private BigDecimal verificationRate;
        private Instant createdAt;

        public RecentAnalysisItem() {}

        public RecentAnalysisItem(UUID id, UUID documentId, String title, String documentType, BigDecimal verificationRate, Instant createdAt) {
            this.id = id;
            this.documentId = documentId;
            this.title = title;
            this.documentType = documentType;
            this.verificationRate = verificationRate;
            this.createdAt = createdAt;
        }

        public UUID getId() {
            return id;
        }

        public void setId(UUID id) {
            this.id = id;
        }

        public UUID getDocumentId() {
            return documentId;
        }

        public void setDocumentId(UUID documentId) {
            this.documentId = documentId;
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

        public BigDecimal getVerificationRate() {
            return verificationRate;
        }

        public void setVerificationRate(BigDecimal verificationRate) {
            this.verificationRate = verificationRate;
        }

        public Instant getCreatedAt() {
            return createdAt;
        }

        public void setCreatedAt(Instant createdAt) {
            this.createdAt = createdAt;
        }
    }
}

