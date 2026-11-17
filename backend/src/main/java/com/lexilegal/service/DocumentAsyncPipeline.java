package com.lexilegal.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.dto.ai.ChunkDto;
import com.lexilegal.dto.ai.ClauseAnalysisResponseDto;
import com.lexilegal.dto.ai.ClauseItemDto;
import com.lexilegal.dto.ai.DocumentSummaryResponseDto;
import com.lexilegal.dto.ai.ExtractionResponseDto;
import com.lexilegal.dto.ai.KeyInfoResponseDto;
import com.lexilegal.dto.ai.MissingProvisionItemDto;
import com.lexilegal.dto.ai.MissingProvisionsResponseDto;
import com.lexilegal.dto.ai.PageDto;
import com.lexilegal.dto.ai.RiskAnalysisResponseDto;
import com.lexilegal.dto.ai.RiskItemDto;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.DocumentAnalysis;
import com.lexilegal.entity.DocumentChunk;
import com.lexilegal.entity.ExtractedClause;
import com.lexilegal.entity.ExtractedInformation;
import com.lexilegal.entity.MissingClauseWarning;
import com.lexilegal.entity.RiskFinding;
import com.lexilegal.repository.DocumentAnalysisRepository;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.ExtractedClauseRepository;
import com.lexilegal.repository.ExtractedInformationRepository;
import com.lexilegal.repository.MissingClauseWarningRepository;
import com.lexilegal.repository.RiskFindingRepository;
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
    private final RiskFindingRepository riskFindingRepository;
    private final ExtractedInformationRepository extractedInformationRepository;
    private final MissingClauseWarningRepository missingClauseWarningRepository;
    private final AiEngineClient aiEngineClient;
    private final ObjectMapper objectMapper;

    public DocumentAsyncPipeline(
            DocumentRepository documentRepository,
            DocumentChunkRepository documentChunkRepository,
            DocumentAnalysisRepository documentAnalysisRepository,
            ExtractedClauseRepository extractedClauseRepository,
            RiskFindingRepository riskFindingRepository,
            ExtractedInformationRepository extractedInformationRepository,
            MissingClauseWarningRepository missingClauseWarningRepository,
            AiEngineClient aiEngineClient,
            ObjectMapper objectMapper) {
        this.documentRepository = documentRepository;
        this.documentChunkRepository = documentChunkRepository;
        this.documentAnalysisRepository = documentAnalysisRepository;
        this.extractedClauseRepository = extractedClauseRepository;
        this.riskFindingRepository = riskFindingRepository;
        this.extractedInformationRepository = extractedInformationRepository;
        this.missingClauseWarningRepository = missingClauseWarningRepository;
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

        // Step 3: Risk analysis
        log.info("running risk analysis for document {}", document.getId());
        try {
            RiskAnalysisResponseDto riskResponse = aiEngineClient.analyzeRisks(
                    document.getId().toString(),
                    pages != null ? pages : Collections.emptyList(),
                    chunks != null ? chunks : Collections.emptyList(),
                    null
            );
            riskFindingRepository.deleteByAnalysisId(analysis.getId());
            if (riskResponse != null && riskResponse.getRisks() != null && !riskResponse.getRisks().isEmpty()) {
                List<RiskFinding> riskEntities = new ArrayList<>();
                for (RiskItemDto item : riskResponse.getRisks()) {
                    RiskFinding rf = new RiskFinding();
                    rf.setAnalysis(analysis);
                    rf.setTitle(item.getTitle() != null ? item.getTitle() : "Unspecified Risk");
                    rf.setCategory(item.getCategory() != null ? item.getCategory() : "Contractual");
                    rf.setLevel(item.getLevel() != null ? item.getLevel() : "MEDIUM");
                    rf.setOriginalClause(item.getOriginalClause() != null ? item.getOriginalClause() : "");
                    rf.setExplanation(item.getExplanation() != null ? item.getExplanation() : "");
                    rf.setWhyItMatters(item.getWhyItMatters() != null ? item.getWhyItMatters() : "");
                    rf.setPossibleConsequences(item.getPossibleConsequences() != null ? item.getPossibleConsequences() : "");
                    rf.setSourcePage(item.getSourcePage() != null ? item.getSourcePage() : 1);
                    rf.setEvidenceQuote(item.getEvidenceQuote() != null ? item.getEvidenceQuote() : "");
                    rf.setQuoteVerified(Boolean.TRUE.equals(item.getQuoteVerified()));
                    rf.setJurisdictionCaveat(item.getJurisdictionCaveat());
                    rf.setProvenance(item.getProvenance() != null ? item.getProvenance() : "AI_INTERPRETATION");
                    if (item.getSuggestedQuestions() != null) {
                        rf.setSuggestedQuestions(objectMapper.writeValueAsString(item.getSuggestedQuestions()));
                    } else {
                        rf.setSuggestedQuestions("[]");
                    }
                    riskEntities.add(rf);
                }
                riskFindingRepository.saveAll(riskEntities);
                log.info("persisted {} risk findings for document {}", riskEntities.size(), document.getId());
            }
        } catch (Exception e) {
            log.error("risk analysis failed for document {}: {}", document.getId(), e.getMessage(), e);
        }

        // Step 4: Key information extraction
        log.info("running key info extraction for document {}", document.getId());
        try {
            KeyInfoResponseDto keyInfoResponse = aiEngineClient.extractKeyInfo(
                    document.getId().toString(),
                    pages != null ? pages : Collections.emptyList(),
                    chunks != null ? chunks : Collections.emptyList()
            );
            extractedInformationRepository.deleteByAnalysisId(analysis.getId());
            if (keyInfoResponse != null) {
                ExtractedInformation info = new ExtractedInformation();
                info.setAnalysis(analysis);
                if (keyInfoResponse.getContractAmount() != null) {
                    info.setContractAmount(keyInfoResponse.getContractAmount().getValue() != null ? keyInfoResponse.getContractAmount().getValue() : "Not specified");
                    info.setContractAmountPage(keyInfoResponse.getContractAmount().getSourcePage());
                }
                if (keyInfoResponse.getPaymentDeadlines() != null) {
                    info.setPaymentDeadlines(keyInfoResponse.getPaymentDeadlines().getValue() != null ? keyInfoResponse.getPaymentDeadlines().getValue() : "Not specified");
                    info.setPaymentDeadlinesPage(keyInfoResponse.getPaymentDeadlines().getSourcePage());
                }
                if (keyInfoResponse.getPenalties() != null) {
                    info.setPenalties(keyInfoResponse.getPenalties().getValue() != null ? keyInfoResponse.getPenalties().getValue() : "Not specified");
                    info.setPenaltiesPage(keyInfoResponse.getPenalties().getSourcePage());
                }
                if (keyInfoResponse.getStartDate() != null) {
                    info.setStartDate(keyInfoResponse.getStartDate().getValue() != null ? keyInfoResponse.getStartDate().getValue() : "Not specified");
                    info.setStartDatePage(keyInfoResponse.getStartDate().getSourcePage());
                }
                if (keyInfoResponse.getEndDate() != null) {
                    info.setEndDate(keyInfoResponse.getEndDate().getValue() != null ? keyInfoResponse.getEndDate().getValue() : "Not specified");
                    info.setEndDatePage(keyInfoResponse.getEndDate().getSourcePage());
                }
                if (keyInfoResponse.getRenewalDate() != null) {
                    info.setRenewalDate(keyInfoResponse.getRenewalDate().getValue() != null ? keyInfoResponse.getRenewalDate().getValue() : "Not specified");
                    info.setRenewalDatePage(keyInfoResponse.getRenewalDate().getSourcePage());
                }
                if (keyInfoResponse.getNoticePeriod() != null) {
                    info.setNoticePeriod(keyInfoResponse.getNoticePeriod().getValue() != null ? keyInfoResponse.getNoticePeriod().getValue() : "Not specified");
                    info.setNoticePeriodPage(keyInfoResponse.getNoticePeriod().getSourcePage());
                }
                if (keyInfoResponse.getTerminationConditions() != null) {
                    info.setTerminationConditions(keyInfoResponse.getTerminationConditions().getValue() != null ? keyInfoResponse.getTerminationConditions().getValue() : "Not specified");
                    info.setTerminationConditionsPage(keyInfoResponse.getTerminationConditions().getSourcePage());
                }
                if (keyInfoResponse.getObligations() != null) {
                    info.setObligations(objectMapper.writeValueAsString(keyInfoResponse.getObligations()));
                }
                if (keyInfoResponse.getImportantDates() != null) {
                    info.setImportantDates(objectMapper.writeValueAsString(keyInfoResponse.getImportantDates()));
                }
                extractedInformationRepository.save(info);
                log.info("persisted extracted information for document {}", document.getId());
            }
        } catch (Exception e) {
            log.error("key info extraction failed for document {}: {}", document.getId(), e.getMessage(), e);
        }

        // Step 5: Missing provisions analysis
        log.info("running missing provisions analysis for document {}", document.getId());
        try {
            MissingProvisionsResponseDto missingResponse = aiEngineClient.analyzeMissingProvisions(
                    document.getId().toString(),
                    pages != null ? pages : Collections.emptyList(),
                    chunks != null ? chunks : Collections.emptyList(),
                    summaryDto.getDocumentType()
            );
            missingClauseWarningRepository.deleteByAnalysisId(analysis.getId());
            if (missingResponse != null && missingResponse.getMissingProvisions() != null && !missingResponse.getMissingProvisions().isEmpty()) {
                List<MissingClauseWarning> warnings = new ArrayList<>();
                for (MissingProvisionItemDto item : missingResponse.getMissingProvisions()) {
                    MissingClauseWarning w = new MissingClauseWarning();
                    w.setAnalysis(analysis);
                    w.setCategory(item.getCategory() != null ? item.getCategory() : "General");
                    w.setClauseName(item.getClauseName() != null ? item.getClauseName() : "Unnamed Provision");
                    w.setWhyItMatters(item.getWhyItMatters() != null ? item.getWhyItMatters() : "");
                    w.setTypicalProvision(item.getTypicalProvision() != null ? item.getTypicalProvision() : "");
                    w.setRiskLevel(item.getRiskLevel() != null ? item.getRiskLevel() : "MEDIUM");
                    w.setLabel(item.getLabel() != null ? item.getLabel() : "Possible omission");
                    warnings.add(w);
                }
                missingClauseWarningRepository.saveAll(warnings);
                log.info("persisted {} missing clause warnings for document {}", warnings.size(), document.getId());
            }
        } catch (Exception e) {
            log.error("missing provisions analysis failed for document {}: {}", document.getId(), e.getMessage(), e);
        }

        document.setStatus("COMPLETED");
        document.setFailureReason(null);
        documentRepository.save(document);
        log.info("document {} analysis completed successfully, verification rate: {}%", document.getId(), analysis.getVerificationRate());
    }
}
