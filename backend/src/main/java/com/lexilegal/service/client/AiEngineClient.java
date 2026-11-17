package com.lexilegal.service.client;

import com.lexilegal.dto.ai.ChunkDto;
import com.lexilegal.dto.ai.ClauseAnalysisRequestDto;
import com.lexilegal.dto.ai.ClauseAnalysisResponseDto;
import com.lexilegal.dto.ai.DocumentSummaryRequestDto;
import com.lexilegal.dto.ai.DocumentSummaryResponseDto;
import com.lexilegal.dto.ai.ExtractionResponseDto;
import com.lexilegal.dto.ai.PageDto;
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

    private final RestClient restClient;
    private final String internalApiKey;

    public AiEngineClient(
            @Value("${app.ai-engine.url:http://localhost:8000}") String aiEngineUrl,
            @Value("${app.ai-engine.internal-key:lexilegal_internal_service_key_secret_2026}") String internalApiKey) {
        this.internalApiKey = internalApiKey;
        SimpleClientHttpRequestFactory factory = new SimpleClientHttpRequestFactory();
        factory.setConnectTimeout(15000);
        factory.setReadTimeout(180000);
        this.restClient = RestClient.builder()
                .requestFactory(factory)
                .baseUrl(aiEngineUrl)
                .build();
    }

    public Map<String, Object> checkHealth() {
        return restClient.get()
                .uri("/internal/health")
                .header("X-Internal-Api-Key", internalApiKey)
                .accept(MediaType.APPLICATION_JSON)
                .retrieve()
                .body(new ParameterizedTypeReference<Map<String, Object>>() {});
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

        return restClient.post()
                .uri("/internal/extract")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(body)
                .retrieve()
                .body(ExtractionResponseDto.class);
    }

    public DocumentSummaryResponseDto analyzeSummary(String documentId, List<PageDto> pages, List<ChunkDto> chunks) {
        DocumentSummaryRequestDto req = new DocumentSummaryRequestDto(documentId, pages, chunks);
        return restClient.post()
                .uri("/internal/analyze/summary")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .body(DocumentSummaryResponseDto.class);
    }

    public ClauseAnalysisResponseDto analyzeClauses(String documentId, List<PageDto> pages, List<ChunkDto> chunks) {
        ClauseAnalysisRequestDto req = new ClauseAnalysisRequestDto(documentId, pages, chunks);
        return restClient.post()
                .uri("/internal/analyze/clauses")
                .header("X-Internal-Api-Key", internalApiKey)
                .contentType(MediaType.APPLICATION_JSON)
                .body(req)
                .retrieve()
                .body(ClauseAnalysisResponseDto.class);
    }
}

