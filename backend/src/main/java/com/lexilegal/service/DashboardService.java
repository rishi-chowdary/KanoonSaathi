package com.lexilegal.service;

import com.lexilegal.dto.response.DashboardStatsResponse;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.DocumentAnalysis;
import com.lexilegal.repository.DocumentAnalysisRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.ExtractedClauseRepository;
import com.lexilegal.repository.RiskFindingRepository;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import java.util.stream.Collectors;

@Service
@Transactional(readOnly = true)
public class DashboardService {

    private final DocumentRepository documentRepository;
    private final DocumentAnalysisRepository documentAnalysisRepository;
    private final ExtractedClauseRepository extractedClauseRepository;
    private final RiskFindingRepository riskFindingRepository;

    public DashboardService(DocumentRepository documentRepository,
                            DocumentAnalysisRepository documentAnalysisRepository,
                            ExtractedClauseRepository extractedClauseRepository,
                            RiskFindingRepository riskFindingRepository) {
        this.documentRepository = documentRepository;
        this.documentAnalysisRepository = documentAnalysisRepository;
        this.extractedClauseRepository = extractedClauseRepository;
        this.riskFindingRepository = riskFindingRepository;
    }

    public DashboardStatsResponse getStatsForUser(UUID userId) {
        DashboardStatsResponse response = new DashboardStatsResponse();

        long totalDocuments = documentRepository.countByUserId(userId);
        long completedAnalyses = documentRepository.countByUserIdAndStatus(userId, "COMPLETED");
        long failedDocuments = documentRepository.countByUserIdAndStatus(userId, "FAILED");
        long totalClauses = extractedClauseRepository.countByUserId(userId);
        long totalRisks = riskFindingRepository.countByUserId(userId);

        response.setTotalDocuments(totalDocuments);
        response.setAnalyzedDocuments(completedAnalyses);
        response.setFailedDocuments(failedDocuments);
        response.setTotalClauses(totalClauses);
        response.setTotalRisks(totalRisks);

        // Level distribution
        Map<String, Long> levelMap = new LinkedHashMap<>();
        levelMap.put("HIGH", 0L);
        levelMap.put("MEDIUM", 0L);
        levelMap.put("LOW", 0L);
        levelMap.put("INFORMATIONAL", 0L);

        List<Object[]> levelCounts = riskFindingRepository.countRisksByLevelForUser(userId);
        for (Object[] row : levelCounts) {
            if (row != null && row.length >= 2 && row[0] != null) {
                String level = row[0].toString().toUpperCase();
                Long count = ((Number) row[1]).longValue();
                levelMap.put(level, count);
            }
        }
        response.setRiskDistributionByLevel(levelMap);

        // Category distribution
        Map<String, Long> categoryMap = new LinkedHashMap<>();
        List<Object[]> categoryCounts = riskFindingRepository.countRisksByCategoryForUser(userId);
        for (Object[] row : categoryCounts) {
            if (row != null && row.length >= 2 && row[0] != null) {
                String category = row[0].toString();
                Long count = ((Number) row[1]).longValue();
                categoryMap.put(category, count);
            }
        }
        response.setRiskDistributionByCategory(categoryMap);

        // Recent 5 documents
        List<Document> recentDocs = documentRepository.findTop5ByUserIdOrderByCreatedAtDesc(userId);
        List<DashboardStatsResponse.RecentDocumentItem> recentDocItems = recentDocs.stream()
                .map(d -> new DashboardStatsResponse.RecentDocumentItem(
                        d.getId(),
                        d.getOriginalFilename(),
                        d.getFileType(),
                        d.getFileSize(),
                        d.getStatus(),
                        d.getPageCount(),
                        d.getCreatedAt()
                ))
                .collect(Collectors.toList());
        response.setRecentDocuments(recentDocItems);

        // Recent 5 analyses
        List<DocumentAnalysis> recentAnalyses = documentAnalysisRepository.findRecentAnalysesForUser(
                userId, PageRequest.of(0, 5)
        );
        List<DashboardStatsResponse.RecentAnalysisItem> recentAnalysisItems = recentAnalyses.stream()
                .map(a -> new DashboardStatsResponse.RecentAnalysisItem(
                        a.getId(),
                        a.getDocument().getId(),
                        a.getTitle() != null ? a.getTitle() : a.getDocument().getOriginalFilename(),
                        a.getDocumentType(),
                        a.getVerificationRate(),
                        a.getCreatedAt()
                ))
                .collect(Collectors.toList());
        response.setRecentAnalyses(recentAnalysisItems);

        return response;
    }
}

