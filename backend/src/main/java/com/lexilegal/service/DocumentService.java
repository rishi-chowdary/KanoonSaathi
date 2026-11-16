package com.lexilegal.service;

import com.lexilegal.dto.response.*;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.DocumentChunk;
import com.lexilegal.entity.User;
import com.lexilegal.exception.ResourceNotFoundException;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.UserRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
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
    private final UserRepository userRepository;
    private final DocumentStorageService storageService;
    private final DocumentAsyncPipeline asyncPipeline;

    public DocumentService(
            DocumentRepository documentRepository,
            DocumentChunkRepository documentChunkRepository,
            UserRepository userRepository,
            DocumentStorageService storageService,
            DocumentAsyncPipeline asyncPipeline) {
        this.documentRepository = documentRepository;
        this.documentChunkRepository = documentChunkRepository;
        this.userRepository = userRepository;
        this.storageService = storageService;
        this.asyncPipeline = asyncPipeline;
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

        // Trigger asynchronous extraction pipeline
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
                    userId, status.toUpperCase(), search.trim(), pageable);
        } else if (hasSearch) {
            pageResult = documentRepository.findByUserIdAndOriginalFilenameContainingIgnoreCaseOrderByCreatedAtDesc(
                    userId, search.trim(), pageable);
        } else if (hasStatus) {
            pageResult = documentRepository.findByUserIdAndStatusOrderByCreatedAtDesc(
                    userId, status.toUpperCase(), pageable);
        } else {
            pageResult = documentRepository.findByUserIdOrderByCreatedAtDesc(userId, pageable);
        }

        List<DocumentResponse> list = pageResult.getContent().stream()
                .map(this::mapToResponse)
                .toList();

        return new PageResponse<>(
                list,
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
        return new DocumentStatusResponse(
                doc.getId(),
                doc.getStatus(),
                doc.getPageCount(),
                doc.getFailureReason(),
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
