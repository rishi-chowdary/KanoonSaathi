package com.lexilegal.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.dto.ai.ChunkDto;
import com.lexilegal.dto.ai.ClauseAnalysisResponseDto;
import com.lexilegal.dto.ai.ClauseItemDto;
import com.lexilegal.dto.ai.DocumentSummaryResponseDto;
import com.lexilegal.dto.ai.ExtractionResponseDto;
import com.lexilegal.dto.ai.PageDto;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.DocumentAnalysis;
import com.lexilegal.entity.DocumentChunk;
import com.lexilegal.entity.ExtractedClause;
import com.lexilegal.repository.DocumentAnalysisRepository;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.ExtractedClauseRepository;
import com.lexilegal.service.client.AiEngineClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.FileSystemResource;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.*;
import java.util.concurrent.CompletableFuture;

@Service
public class DocumentAsyncPipeline {

    private static final Logger log = LoggerFactory.getLogger(DocumentAsyncPipeline.class);

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository documentChunkRepository;
    private final DocumentAnalysisRepository documentAnalysisRepository;
    private final ExtractedClauseRepository extractedClauseRepository;
    private final AiEngineClient aiEngineClient;
    private final ObjectMapper objectMapper;

    public DocumentAsyncPipeline(
            DocumentRepository documentRepository,
            DocumentChunkRepository documentChunkRepository,
            DocumentAnalysisRepository documentAnalysisRepository,
            ExtractedClauseRepository extractedClauseRepository,
            AiEngineClient aiEngineClient,
            ObjectMapper objectMapper) {
        this.documentRepository = documentRepository;
        this.documentChunkRepository = documentChunkRepository;
        this.documentAnalysisRepository = documentAnalysisRepository;
        this.extractedClauseRepository = extractedClauseRepository;
        this.aiEngineClient = aiEngineClient;
        this.objectMapper = objectMapper;
    }

    @Async
    public CompletableFuture<Void> processDocumentAsync(UUID documentId) {
        Document document = documentRepository.findById(documentId).orElse(null);
        if (document == null) {
            log.warn("document {} not found for async processing", documentId);
            return CompletableFuture.completedFuture(null);
        }

        try {
            // Step 1: Extraction
            document.setStatus("EXTRACTING");
            document = documentRepository.save(document);
            log.info("extracting document {}: {}", documentId, document.getOriginalFilename());

            Path path = Paths.get(document.getStoragePath());
            FileSystemResource resource = new FileSystemResource(path.toFile());

            ExtractionResponseDto extraction = aiEngineClient.extract(resource, document.getOriginalFilename());

            List<ChunkDto> chunksList = new ArrayList<>();
            if (extraction.getChunks() != null && !extraction.getChunks().isEmpty()) {
                chunksList.addAll(extraction.getChunks());
                for (ChunkDto chunkDto : extraction.getChunks()) {
                    DocumentChunk chunk = new DocumentChunk();
                    chunk.setDocument(document);
                    chunk.setChunkIndex(chunkDto.getChunkIndex());
                    chunk.setPageNumber(chunkDto.getPageStart());
                    chunk.setContent(chunkDto.getContent());
                    chunk.setTokenCount(chunkDto.getTokenCount());
                    documentChunkRepository.save(chunk);
                }
            } else if (extraction.getPages() != null && !extraction.getPages().isEmpty()) {
                int idx = 0;
                for (PageDto pageDto : extraction.getPages()) {
                    if (pageDto.getText() != null && !pageDto.getText().isBlank()) {
                        DocumentChunk chunk = new DocumentChunk();
                        chunk.setDocument(document);
                        chunk.setChunkIndex(idx++);
                        chunk.setPageNumber(pageDto.getPageNumber());
                        chunk.setContent(pageDto.getText());
                        chunk.setTokenCount(Math.max(1, pageDto.getText().length() / 4));
                        documentChunkRepository.save(chunk);

                        ChunkDto cd = new ChunkDto();
                        cd.setChunkIndex(chunk.getChunkIndex());
                        cd.setPageStart(chunk.getPageNumber());
                        cd.setPageEnd(chunk.getPageNumber());
                        cd.setContent(chunk.getContent());
                        cd.setTokenCount(chunk.getTokenCount());
                        chunksList.add(cd);
                    }
                }
            }

            int pageCount = (extraction.getPages() != null && !extraction.getPages().isEmpty())
                    ? extraction.getPages().size()
                    : 1;

            boolean isScanned = extraction.getPages() != null &&
                    extraction.getPages().stream().anyMatch(PageDto::isOcrUsed);

            document.setPageCount(pageCount);
            document.setIsScanned(isScanned);
            document.setStatus("EXTRACTED");
            document.setFailureReason(null);
            document = documentRepository.save(document);
            log.info("document {} successfully extracted into {} pages", documentId, pageCount);

            // Step 2: Analysis (Summary)
            runAnalysis(document, extraction.getPages(), chunksList);

        } catch (Exception e) {
            log.error("pipeline failed for document {}", documentId, e);
            document.setStatus("FAILED");
            document.setFailureReason(e.getMessage());
            documentRepository.save(document);
        }
        return CompletableFuture.completedFuture(null);
    }

    @Async
    public CompletableFuture<Void> reanalyzeDocumentAsync(UUID documentId) {
        Document document = documentRepository.findById(documentId).orElse(null);
        if (document == null) {
            return CompletableFuture.completedFuture(null);
        }

        try {
            document.setStatus("ANALYZING");
            document.setFailureReason(null);
            document = documentRepository.save(document);

            List<DocumentChunk> dbChunks = documentChunkRepository.findByDocumentIdOrderByChunkIndexAsc(documentId);
            List<ChunkDto> chunksList = new ArrayList<>();
            Map<Integer, StringBuilder> pageMap = new TreeMap<>();

            for (DocumentChunk c : dbChunks) {
                ChunkDto cd = new ChunkDto();
                cd.setChunkIndex(c.getChunkIndex());
                cd.setPageStart(c.getPageNumber());
                cd.setPageEnd(c.getPageNumber());
                cd.setContent(c.getContent());
                cd.setTokenCount(c.getTokenCount());
                chunksList.add(cd);

                pageMap.computeIfAbsent(c.getPageNumber(), k -> new StringBuilder())
                        .append(c.getContent()).append("\n\n");
            }

            List<PageDto> pagesList = new ArrayList<>();
            for (Map.Entry<Integer, StringBuilder> entry : pageMap.entrySet()) {
                PageDto pd = new PageDto();
                pd.setPageNumber(entry.getKey());
                pd.setText(entry.getValue().toString().trim());
                pd.setOcrUsed(Boolean.TRUE.equals(document.getIsScanned()));
                pagesList.add(pd);
            }

            runAnalysis(document, pagesList, chunksList);

        } catch (Exception e) {
            log.error("reanalysis failed for document {}", documentId, e);
            document.setStatus("FAILED");
            document.setFailureReason("Reanalysis failed: " + e.getMessage());
            documentRepository.save(document);
        }
        return CompletableFuture.completedFuture(null);
    }

    @Transactional
    public void runAnalysis(Document document, List<PageDto> pages, List<ChunkDto> chunks) throws Exception {
        document.setStatus("ANALYZING");
        documentRepository.save(document);
        log.info("running summary analysis for document {}", document.getId());

        DocumentSummaryResponseDto summaryDto = aiEngineClient.analyzeSummary(
                document.getId().toString(),
                pages != null ? pages : Collections.emptyList(),
                chunks != null ? chunks : Collections.emptyList()
        );

        DocumentAnalysis analysis = documentAnalysisRepository.findByDocumentId(document.getId())
                .orElseGet(() -> {
                    DocumentAnalysis a = new DocumentAnalysis();
                    a.setDocument(document);
                    return a;
                });

        analysis.setTitle(summaryDto.getTitle());
        analysis.setDocumentType(summaryDto.getDocumentType());
        analysis.setPurpose(summaryDto.getPurpose());
        analysis.setSummaryShort(summaryDto.getShortSummary());
        analysis.setSummaryDetailed(summaryDto.getDetailedSummary());
        analysis.setParties(objectMapper.writeValueAsString(summaryDto.getParties()));
        analysis.setMainConditions(objectMapper.writeValueAsString(summaryDto.getMainConditions()));
        analysis.setObligationsSummary(objectMapper.writeValueAsString(summaryDto.getObligations()));
        analysis.setFinancialTermsSummary(objectMapper.writeValueAsString(summaryDto.getFinancialTerms()));
        analysis.setLlmProvider(summaryDto.getLlmProvider() != null ? summaryDto.getLlmProvider() : "gemini");
        analysis.setLlmModel(summaryDto.getLlmModel() != null ? summaryDto.getLlmModel() : "gemini-1.5-flash");
        analysis.setVerificationRate(summaryDto.getVerificationRate() != null ? summaryDto.getVerificationRate() : java.math.BigDecimal.ZERO);

        analysis = documentAnalysisRepository.save(analysis);

        // Run clause extraction pass
        log.info("running clause extraction for document {}", document.getId());
        try {
            ClauseAnalysisResponseDto clauseResponse = aiEngineClient.analyzeClauses(
                    document.getId().toString(),
                    pages != null ? pages : Collections.emptyList(),
                    chunks != null ? chunks : Collections.emptyList()
            );

            // Clean previous clauses if reanalyzing
            extractedClauseRepository.deleteByAnalysisId(analysis.getId());

            if (clauseResponse != null && clauseResponse.getClauses() != null && !clauseResponse.getClauses().isEmpty()) {
                List<ExtractedClause> clauseEntities = new ArrayList<>();
                for (ClauseItemDto item : clauseResponse.getClauses()) {
                    ExtractedClause entity = new ExtractedClause();
                    entity.setAnalysis(analysis);
                    entity.setTitle(item.getTitle() != null ? item.getTitle() : "Untitled Clause");
                    entity.setCategory(item.getCategory() != null ? item.getCategory() : "Other");
                    entity.setCustomLabel(item.getCustomLabel());
                    entity.setOriginalText(item.getOriginalText() != null ? item.getOriginalText() : "");
                    entity.setSimplifiedSimple(item.getSimplifiedSimple() != null ? item.getSimplifiedSimple() : "");
                    entity.setSimplifiedDetailed(item.getSimplifiedDetailed() != null ? item.getSimplifiedDetailed() : "");
                    entity.setSimplifiedProfessional(item.getSimplifiedProfessional() != null ? item.getSimplifiedProfessional() : "");
                    entity.setImportance(item.getImportance() != null ? item.getImportance() : "MEDIUM");
                    entity.setAffectedParty(item.getAffectedParty() != null ? item.getAffectedParty() : "Both parties");
                    entity.setSourcePage(item.getSourcePage() != null ? item.getSourcePage() : 1);
                    entity.setSectionReference(item.getSectionReference());
                    entity.setEvidenceQuote(item.getEvidenceQuote() != null ? item.getEvidenceQuote() : "");
                    entity.setQuoteVerified(Boolean.TRUE.equals(item.getQuoteVerified()));
                    entity.setProvenance(item.getProvenance() != null ? item.getProvenance() : "EXTRACTED");
                    clauseEntities.add(entity);
                }
                extractedClauseRepository.saveAll(clauseEntities);
                log.info("persisted {} extracted clauses for document {}", clauseEntities.size(), document.getId());
            }
        } catch (Exception e) {
            log.error("clause extraction failed for document {}: {}", document.getId(), e.getMessage(), e);
        }

        document.setStatus("COMPLETED");
        document.setFailureReason(null);
        documentRepository.save(document);
        log.info("document {} analysis completed successfully, verification rate: {}%", document.getId(), analysis.getVerificationRate());
    }
}
