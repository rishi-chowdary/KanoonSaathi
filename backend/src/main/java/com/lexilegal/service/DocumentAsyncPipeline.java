package com.lexilegal.service;

import com.lexilegal.dto.ai.ChunkDto;
import com.lexilegal.dto.ai.ExtractionResponseDto;
import com.lexilegal.dto.ai.PageDto;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.DocumentChunk;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.service.client.AiEngineClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.core.io.FileSystemResource;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;
import java.util.concurrent.CompletableFuture;

@Service
public class DocumentAsyncPipeline {

    private static final Logger log = LoggerFactory.getLogger(DocumentAsyncPipeline.class);

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository documentChunkRepository;
    private final AiEngineClient aiEngineClient;

    public DocumentAsyncPipeline(
            DocumentRepository documentRepository,
            DocumentChunkRepository documentChunkRepository,
            AiEngineClient aiEngineClient) {
        this.documentRepository = documentRepository;
        this.documentChunkRepository = documentChunkRepository;
        this.aiEngineClient = aiEngineClient;
    }

    @Async
    public CompletableFuture<Void> processDocumentAsync(UUID documentId) {
        Document document = documentRepository.findById(documentId).orElse(null);
        if (document == null) {
            log.warn("document {} not found for async processing", documentId);
            return CompletableFuture.completedFuture(null);
        }

        try {
            document.setStatus("EXTRACTING");
            document = documentRepository.save(document);
            log.info("extracting document {}: {}", documentId, document.getOriginalFilename());

            Path path = Paths.get(document.getStoragePath());
            FileSystemResource resource = new FileSystemResource(path.toFile());

            ExtractionResponseDto extraction = aiEngineClient.extract(resource, document.getOriginalFilename());

            if (extraction.getChunks() != null && !extraction.getChunks().isEmpty()) {
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
                // If chunker returned empty chunks (e.g. text was very short), store pages directly
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
            documentRepository.save(document);
            log.info("document {} successfully extracted into {} pages", documentId, pageCount);

        } catch (Exception e) {
            log.error("extraction pipeline failed for document {}", documentId, e);
            document.setStatus("FAILED");
            document.setFailureReason("Extraction failed: " + e.getMessage());
            documentRepository.save(document);
        }

        return CompletableFuture.completedFuture(null);
    }
}
