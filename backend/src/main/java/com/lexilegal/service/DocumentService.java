package com.lexilegal.service;

import com.lexilegal.dto.ai.SimplifyResponseDto;
import com.lexilegal.dto.response.*;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.DocumentAnalysis;
import com.lexilegal.entity.DocumentChunk;
import com.lexilegal.entity.ExtractedClause;
import com.lexilegal.entity.User;
import com.lexilegal.exception.ResourceNotFoundException;
import com.lexilegal.repository.DocumentAnalysisRepository;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.ExtractedClauseRepository;
import com.lexilegal.repository.UserRepository;
import com.lexilegal.service.client.AiEngineClient;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Path;
import java.util.*;
import java.util.stream.Collectors;

@Service
public class DocumentService {

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository documentChunkRepository;
    private final DocumentAnalysisRepository documentAnalysisRepository;
    private final ExtractedClauseRepository extractedClauseRepository;
    private final UserRepository userRepository;
    private final DocumentStorageService storageService;
    private final DocumentAsyncPipeline asyncPipeline;
    private final AiEngineClient aiEngineClient;

    public DocumentService(
            DocumentRepository documentRepository,
            DocumentChunkRepository documentChunkRepository,
            DocumentAnalysisRepository documentAnalysisRepository,
            ExtractedClauseRepository extractedClauseRepository,
            UserRepository userRepository,
            DocumentStorageService storageService,
            DocumentAsyncPipeline asyncPipeline,
            AiEngineClient aiEngineClient) {
        this.documentRepository = documentRepository;
        this.documentChunkRepository = documentChunkRepository;
        this.documentAnalysisRepository = documentAnalysisRepository;
        this.extractedClauseRepository = extractedClauseRepository;
        this.userRepository = userRepository;
        this.storageService = storageService;
        this.asyncPipeline = asyncPipeline;
        this.aiEngineClient = aiEngineClient;
    }

    public DocumentUploadResponse upload(UUID userId, MultipartFile file) {
        storageService.validate(file);
        String hash = storageService.computeSha256(file);

        Optional<Document> existing = documentRepository.findByUserIdAndFileHash(userId, hash);
        if (existing.isPresent()) {
            Document doc = existing.get();
            return new DocumentUploadResponse(
                    doc.getId(),
                    doc.getOriginalFilename(),
                    doc.getFileSize(),
                    doc.getStatus(),
                    true
            );
        }

        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("user not found"));

        Path storedPath = storageService.store(file);
        String originalFilename = file.getOriginalFilename();
        String ext = getExtension(originalFilename);

        Document document = new Document();
        document.setUser(user);
        document.setOriginalFilename(originalFilename);
        document.setStoragePath(storedPath.toString());
        document.setFileType(ext);
        document.setFileSize(file.getSize());
        document.setFileHash(hash);
        document.setPageCount(0);
        document.setIsScanned(false);
        document.setStatus("UPLOADED");

        Document saved = documentRepository.save(document);

        // Trigger asynchronous extraction + summarization pipeline
        asyncPipeline.processDocumentAsync(saved.getId());

        return new DocumentUploadResponse(
                saved.getId(),
                saved.getOriginalFilename(),
                saved.getFileSize(),
                saved.getStatus(),
                false
        );
    }

    public PageResponse<DocumentResponse> listDocuments(
            UUID userId, int page, int size, String search, String status) {
        Pageable pageable = PageRequest.of(Math.max(0, page), Math.max(1, size));
        Page<Document> pageResult;

        boolean hasSearch = search != null && !search.isBlank();
        boolean hasStatus = status != null && !status.isBlank() && !status.equalsIgnoreCase("ALL");

        if (hasSearch && hasStatus) {
            pageResult = documentRepository.findByUserIdAndStatusAndOriginalFilenameContainingIgnoreCaseOrderByCreatedAtDesc(
                    userId, status.trim().toUpperCase(), search.trim(), pageable);
        } else if (hasSearch) {
            pageResult = documentRepository.findByUserIdAndOriginalFilenameContainingIgnoreCaseOrderByCreatedAtDesc(
                    userId, search.trim(), pageable);
        } else if (hasStatus) {
            pageResult = documentRepository.findByUserIdAndStatusOrderByCreatedAtDesc(
                    userId, status.trim().toUpperCase(), pageable);
        } else {
            pageResult = documentRepository.findByUserIdOrderByCreatedAtDesc(userId, pageable);
        }

        List<DocumentResponse> dtoList = pageResult.getContent().stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());

        return new PageResponse<>(
                dtoList,
                pageResult.getNumber(),
                pageResult.getSize(),
                pageResult.getTotalElements(),
                pageResult.getTotalPages()
        );
    }

    public DocumentResponse getDocument(UUID userId, UUID id) {
        Document doc = documentRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ResourceNotFoundException("document not found"));
        return mapToResponse(doc);
    }

    public DocumentStatusResponse getStatus(UUID userId, UUID id) {
        Document doc = documentRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ResourceNotFoundException("document not found"));
        boolean hasAnalysis = documentAnalysisRepository.findByDocumentId(id).isPresent();
        return new DocumentStatusResponse(
                doc.getId(),
                doc.getStatus(),
                doc.getPageCount(),
                doc.getFailureReason(),
                hasAnalysis,
                doc.getUpdatedAt()
        );
    }

    public DocumentTextResponse getText(UUID userId, UUID id, Integer pageNumber) {
        Document doc = documentRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ResourceNotFoundException("document not found"));

        DocumentTextResponse response = new DocumentTextResponse();
        response.setDocumentId(doc.getId());
        response.setPageCount(doc.getPageCount());

        if (pageNumber != null) {
            response.setPage(pageNumber);
            List<DocumentChunk> chunks = documentChunkRepository.findByDocumentIdAndPageNumberOrderByChunkIndexAsc(doc.getId(), pageNumber);
            String joined = chunks.stream()
                    .map(DocumentChunk::getContent)
                    .collect(Collectors.joining("\n\n"));
            response.setText(joined);
        } else {
            List<DocumentChunk> allChunks = documentChunkRepository.findByDocumentIdOrderByChunkIndexAsc(doc.getId());
            Map<Integer, List<String>> pageMap = new TreeMap<>();
            for (DocumentChunk chunk : allChunks) {
                pageMap.computeIfAbsent(chunk.getPageNumber(), k -> new ArrayList<>())
                        .add(chunk.getContent());
            }

            List<DocumentTextResponse.PageTextDto> pages = new ArrayList<>();
            for (Map.Entry<Integer, List<String>> entry : pageMap.entrySet()) {
                pages.add(new DocumentTextResponse.PageTextDto(
                        entry.getKey(),
                        String.join("\n\n", entry.getValue())
                ));
            }
            response.setPages(pages);
            response.setText(pages.stream().map(DocumentTextResponse.PageTextDto::getText).collect(Collectors.joining("\n\n")));
        }

        return response;
    }

    public AnalysisSummaryResponse getAnalysis(UUID userId, UUID id) {
        Document doc = documentRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ResourceNotFoundException("document not found"));

        DocumentAnalysis analysis = documentAnalysisRepository.findByDocumentId(doc.getId())
                .orElseThrow(() -> new ResourceNotFoundException("analysis not found for this document"));

        AnalysisSummaryResponse resp = new AnalysisSummaryResponse();
        resp.setId(analysis.getId());
        resp.setDocumentId(doc.getId());
        resp.setTitle(analysis.getTitle());
        resp.setDocumentType(analysis.getDocumentType());
        resp.setPurpose(analysis.getPurpose());
        resp.setParties(analysis.getParties());
        resp.setShortSummary(analysis.getSummaryShort());
        resp.setDetailedSummary(analysis.getSummaryDetailed());
        resp.setMainConditions(analysis.getMainConditions());
        resp.setObligationsSummary(analysis.getObligationsSummary());
        resp.setFinancialTermsSummary(analysis.getFinancialTermsSummary());
        resp.setVerificationRate(analysis.getVerificationRate());
        resp.setLlmProvider(analysis.getLlmProvider());
        resp.setLlmModel(analysis.getLlmModel());
        resp.setCreatedAt(analysis.getCreatedAt());
        resp.setUpdatedAt(analysis.getUpdatedAt());
        return resp;
    }

    public void reanalyze(UUID userId, UUID id) {
        Document doc = documentRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ResourceNotFoundException("document not found"));

        asyncPipeline.reanalyzeDocumentAsync(doc.getId());
    }

    public PageResponse<ClauseResponse> getClauses(
            UUID userId,
            UUID documentId,
            String category,
            String importance,
            String search,
            int page,
            int size) {
        Document doc = documentRepository.findByIdAndUserId(documentId, userId)
                .orElseThrow(() -> new ResourceNotFoundException("document not found"));

        DocumentAnalysis analysis = documentAnalysisRepository.findByDocumentId(doc.getId()).orElse(null);
        if (analysis == null) {
            return new PageResponse<>(Collections.emptyList(), page, size, 0, 0);
        }

        Pageable pageable = PageRequest.of(
                Math.max(0, page),
                Math.max(1, size),
                Sort.by(Sort.Direction.ASC, "sourcePage", "createdAt")
        );

        Specification<ExtractedClause> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            predicates.add(cb.equal(root.get("analysis").get("id"), analysis.getId()));

            if (category != null && !category.isBlank() && !category.equalsIgnoreCase("ALL")) {
                predicates.add(cb.equal(cb.lower(root.get("category")), category.trim().toLowerCase()));
            }

            if (importance != null && !importance.isBlank() && !importance.equalsIgnoreCase("ALL")) {
                predicates.add(cb.equal(cb.upper(root.get("importance")), importance.trim().toUpperCase()));
            }

            if (search != null && !search.isBlank()) {
                String pattern = "%" + search.trim().toLowerCase() + "%";
                Predicate titleMatch = cb.like(cb.lower(root.get("title")), pattern);
                Predicate textMatch = cb.like(cb.lower(root.get("originalText")), pattern);
                Predicate simpleMatch = cb.like(cb.lower(root.get("simplifiedSimple")), pattern);
                Predicate refMatch = cb.like(cb.lower(root.get("sectionReference")), pattern);
                predicates.add(cb.or(titleMatch, textMatch, simpleMatch, refMatch));
            }

            return cb.and(predicates.toArray(new Predicate[0]));
        };

        Page<ExtractedClause> pageResult = extractedClauseRepository.findAll(spec, pageable);
        List<ClauseResponse> dtos = pageResult.getContent().stream()
                .map(ClauseResponse::fromEntity)
                .collect(Collectors.toList());

        return new PageResponse<>(
                dtos,
                pageResult.getNumber(),
                pageResult.getSize(),
                pageResult.getTotalElements(),
                pageResult.getTotalPages()
        );
    }

    @Transactional
    public ReExplainClauseResponse reExplainClause(UUID userId, UUID documentId, UUID clauseId, String mode) {
        Document doc = documentRepository.findByIdAndUserId(documentId, userId)
                .orElseThrow(() -> new ResourceNotFoundException("document not found"));

        DocumentAnalysis analysis = documentAnalysisRepository.findByDocumentId(doc.getId())
                .orElseThrow(() -> new ResourceNotFoundException("analysis not found for this document"));

        ExtractedClause clause = extractedClauseRepository.findById(clauseId)
                .orElseThrow(() -> new ResourceNotFoundException("clause not found"));

        if (!clause.getAnalysis().getId().equals(analysis.getId())) {
            throw new ResourceNotFoundException("clause does not belong to this document");
        }

        String validMode = (mode != null && (mode.equals("detailed") || mode.equals("professional")))
                ? mode : "simple_english";

        String context = "Document: " + (analysis.getTitle() != null ? analysis.getTitle() : doc.getOriginalFilename())
                + " (" + (analysis.getDocumentType() != null ? analysis.getDocumentType() : "Legal Agreement") + "). "
                + "Clause: " + clause.getTitle() + " [" + clause.getCategory() + "]";

        SimplifyResponseDto simplifyResult = aiEngineClient.simplify(clause.getOriginalText(), validMode, context);

        if (simplifyResult != null && simplifyResult.getExplanation() != null && !simplifyResult.getExplanation().isBlank()) {
            if ("detailed".equalsIgnoreCase(validMode)) {
                clause.setSimplifiedDetailed(simplifyResult.getExplanation());
            } else if ("professional".equalsIgnoreCase(validMode)) {
                clause.setSimplifiedProfessional(simplifyResult.getExplanation());
            } else {
                clause.setSimplifiedSimple(simplifyResult.getExplanation());
            }
            clause = extractedClauseRepository.save(clause);
        }

        ClauseResponse clauseResponse = ClauseResponse.fromEntity(clause);
        return new ReExplainClauseResponse(
                clauseResponse,
                validMode,
                simplifyResult != null ? simplifyResult.getExplanation() : "",
                simplifyResult != null ? simplifyResult.getGlossary() : Collections.emptyList(),
                simplifyResult != null ? simplifyResult.getWhatCouldBeMissed() : Collections.emptyList(),
                simplifyResult != null ? simplifyResult.getWarnings() : Collections.emptyList(),
                simplifyResult != null ? simplifyResult.getIsGrounded() : true
        );
    }

    @Transactional
    public void deleteDocument(UUID userId, UUID id) {
        Document doc = documentRepository.findByIdAndUserId(id, userId)
                .orElseThrow(() -> new ResourceNotFoundException("document not found"));

        storageService.deleteFile(doc.getStoragePath());
        documentRepository.delete(doc);
    }

    private DocumentResponse mapToResponse(Document doc) {
        return new DocumentResponse(
                doc.getId(),
                doc.getOriginalFilename(),
                doc.getFileType(),
                doc.getFileSize(),
                doc.getPageCount(),
                doc.getIsScanned(),
                doc.getStatus(),
                doc.getFailureReason(),
                doc.getCreatedAt(),
                doc.getUpdatedAt()
        );
    }

    private String getExtension(String filename) {
        if (filename == null) return "bin";
        int idx = filename.lastIndexOf('.');
        return (idx > 0 && idx < filename.length() - 1) ? filename.substring(idx + 1).toLowerCase() : "bin";
    }
}
