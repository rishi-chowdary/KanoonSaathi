package com.lexilegal.service;

import com.lexilegal.dto.ai.SimplifyResponseDto;
import com.lexilegal.dto.request.SimplifyRequest;
import com.lexilegal.service.client.AiEngineClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;

@Service
public class SimplifyService {

    private static final Logger log = LoggerFactory.getLogger(SimplifyService.class);

    private final AiEngineClient aiEngineClient;

    public SimplifyService(AiEngineClient aiEngineClient) {
        this.aiEngineClient = aiEngineClient;
    }

    public SimplifyResponseDto simplify(SimplifyRequest request) {
        log.info("simplifying legal text (length: {}, mode: {})",
                request.getText() != null ? request.getText().length() : 0,
                request.getMode());

        return aiEngineClient.simplify(
                request.getText(),
                request.getMode(),
                request.getDocumentContext()
        );
    }
}

