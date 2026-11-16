package com.lexilegal.service.client;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import java.util.Map;

@Service
public class AiEngineClient {

    private final RestClient restClient;
    private final String internalApiKey;

    public AiEngineClient(
            @Value("${app.ai-engine.url:http://localhost:8000}") String aiEngineUrl,
            @Value("${app.ai-engine.internal-key:lexilegal_internal_service_key_secret_2026}") String internalApiKey) {
        this.internalApiKey = internalApiKey;
        this.restClient = RestClient.builder()
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
}
