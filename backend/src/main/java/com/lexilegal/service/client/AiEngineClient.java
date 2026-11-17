package com.lexilegal.service.client;

import com.lexilegal.dto.ai.ChatRequestDto;
import com.lexilegal.dto.ai.ChatResponseDto;
import com.lexilegal.dto.ai.ChunkDto;
import com.lexilegal.dto.ai.ClauseAnalysisRequestDto;
import com.lexilegal.dto.ai.ClauseAnalysisResponseDto;
import com.lexilegal.dto.ai.DocumentSummaryRequestDto;
import com.lexilegal.dto.ai.DocumentSummaryResponseDto;
import com.lexilegal.dto.ai.ExtractionResponseDto;
import com.lexilegal.dto.ai.KeyInfoRequestDto;
import com.lexilegal.dto.ai.KeyInfoResponseDto;
import com.lexilegal.dto.ai.MissingProvisionsRequestDto;
import com.lexilegal.dto.ai.MissingProvisionsResponseDto;
import com.lexilegal.dto.ai.PageDto;
import com.lexilegal.dto.ai.RiskAnalysisRequestDto;
import com.lexilegal.dto.ai.RiskAnalysisResponseDto;
import com.lexilegal.dto.ai.SimplifyResponseDto;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.http.MediaType;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestClient;

import java.io.IOException;
import java.util.List;
import java.util.Map;

@Service
public class AiEngineClient {

    private static final org.slf4j.Logger log = org.slf4j.LoggerFactory.getLogger(AiEngineClient.class);
    private static final int MAX_RETRIES = 2; // Up to 2 retries (3 total attempts)
    private static final long INITIAL_BACKOFF_MS = 1000L;

    private final RestClient restClient;
    private final String internalApiKey;

    public AiEngineClient(
            @Value("${app.ai-engine.url:http://localhost:8000}") String aiEngineUrl,
            @Value("${app.ai-engine.internal-key:lexilegal_internal_service_key_secret_2026}") String internalApiKey) {
        this.internalApiKey = internalApiKey;
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(30000);
        factory.setReadTimeout(600000);
        this.restClient = RestClient.builder()
                .requestFactory(factory)
                .baseUrl(aiEngineUrl)
                .build();
    }

    private <T> T executeWithRetry(java.util.function.Supplier<T> action, String operationName) {
        int attempt = 0;
        long backoff = INITIAL_BACKOFF_MS;
        while (true) {
            attempt++;
            try {
                return action.get();
            } catch (Exception ex) {
                boolean isTransient = ex instanceof org.springframework.web.client.ResourceAccessException
                        || ex instanceof org.springframework.web.client.HttpServerErrorException;
                if (!isTransient || attempt > MAX_RETRIES) {
                    log.error("AI engine operation '{}' failed after {} attempt(s): {}", operationName, attempt, ex.getMessage());
                    throw ex;
                }
                log.warn("AI engine operation '{}' transient failure on attempt {}/{} ({}), retrying in {}ms...",
                        operationName, attempt, MAX_RETRIES + 1, ex.getMessage(), backoff);
                try {
                    Thread.sleep(backoff);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                    throw new RuntimeException("Interrupted during AI engine retry backoff", ie);
                }
                backoff *= 2;
            }
        }
    }

    public Map<String, Object> checkHealth() {
        return executeWithRetry(() -> restClient.get()
                .uri("/internal/health")
                .header("X-Internal-Api-Key", internalApiKey)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(new ParameterizedTypeReference<Map<String, Object>>() {}), "checkHealth");
    }

    public ExtractionResponseDto extract(Resource fileResource, String filename) {
        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        try {
            byte[] bytes = fileResource.getContentAsByteArray();
            ByteArrayResource resource = new ByteArrayResource(bytes) {
                @Override
                public String getFilename() {
                    return filename;
                }
            };
            body.add("file", resource);
        } catch (IOException e) {
            throw new RuntimeException("failed to read file content for extraction", e);
        }

        return executeWithRetry(() -> restClient.post()
                .uri("/internal/extract")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(body)
                .retrieve()
                .body(ExtractionResponseDto.class), "extract");
    }

    public DocumentSummaryResponseDto analyzeSummary(String documentId, List<PageDto> pages, List<ChunkDto> chunks) {
        DocumentSummaryRequestDto req = new DocumentSummaryRequestDto(documentId, pages, chunks);
        return executeWithRetry(() -> restClient.post()
                .uri("/internal/analyze/summary")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .body(DocumentSummaryResponseDto.class), "analyzeSummary");
    }

    public ClauseAnalysisResponseDto analyzeClauses(String documentId, List<PageDto> pages, List<ChunkDto> chunks) {
        ClauseAnalysisRequestDto req = new ClauseAnalysisRequestDto(documentId, pages, chunks);
        return executeWithRetry(() -> restClient.post()
                .uri("/internal/analyze/clauses")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .body(ClauseAnalysisResponseDto.class), "analyzeClauses");
    }

    public SimplifyResponseDto simplify(String text, String mode, String documentContext) {
        java.util.Map<String, Object> req = new java.util.HashMap<>();
        req.put("text", text);
        req.put("mode", mode != null ? mode : "simple_english");
        if (documentContext != null) {
            req.put("document_context", documentContext);
        }
        return executeWithRetry(() -> restClient.post()
                .uri("/internal/simplify")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .body(SimplifyResponseDto.class), "simplify");
    }

    public RiskAnalysisResponseDto analyzeRisks(String documentId, List<PageDto> pages, List<ChunkDto> chunks, Boolean governingLawFound) {
        RiskAnalysisRequestDto req = new RiskAnalysisRequestDto(documentId, pages, chunks, governingLawFound);
        return executeWithRetry(() -> restClient.post()
                .uri("/internal/analyze/risks")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .body(RiskAnalysisResponseDto.class), "analyzeRisks");
    }

    public KeyInfoResponseDto extractKeyInfo(String documentId, List<PageDto> pages, List<ChunkDto> chunks) {
        KeyInfoRequestDto req = new KeyInfoRequestDto(documentId, pages, chunks);
        return executeWithRetry(() -> restClient.post()
                .uri("/internal/analyze/key-info")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .body(KeyInfoResponseDto.class), "extractKeyInfo");
    }

    public MissingProvisionsResponseDto analyzeMissingProvisions(String documentId, List<PageDto> pages, List<ChunkDto> chunks, String documentTypeHint) {
        MissingProvisionsRequestDto req = new MissingProvisionsRequestDto(documentId, pages, chunks, documentTypeHint);
        return executeWithRetry(() -> restClient.post()
                .uri("/internal/analyze/missing")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .body(MissingProvisionsResponseDto.class), "analyzeMissingProvisions");
    }

    public ChatResponseDto chat(ChatRequestDto request) {
        return executeWithRetry(() -> restClient.post()
                .uri("/internal/chat")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(ChatResponseDto.class), "chat");
    }
}

