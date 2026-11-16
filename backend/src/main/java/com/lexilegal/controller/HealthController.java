package com.lexilegal.controller;

import com.lexilegal.service.client.AiEngineClient;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/health")
public class HealthController {

    private final JdbcTemplate jdbcTemplate;
    private final AiEngineClient aiEngineClient;

    public HealthController(JdbcTemplate jdbcTemplate, AiEngineClient aiEngineClient) {
        this.jdbcTemplate = jdbcTemplate;
        this.aiEngineClient = aiEngineClient;
    }

    @GetMapping
    public ResponseEntity<Map<String, Object>> health() {
        Map<String, Object> response = new HashMap<>();
        response.put("status", "ok");
        response.put("service", "lexilegal-backend");

        try {
            Integer result = jdbcTemplate.queryForObject("SELECT 1", Integer.class);
            boolean dbOk = result != null && result == 1;
            response.put("database", dbOk ? "connected" : "unexpected_result");
            return ResponseEntity.ok(response);
        } catch (Exception ex) {
            response.put("status", "degraded");
            response.put("database", "disconnected: " + ex.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(response);
        }
    }

    @GetMapping("/ai")
    public ResponseEntity<Map<String, Object>> aiHealth() {
        Map<String, Object> response = new HashMap<>();
        response.put("service", "lexilegal-backend");

        try {
            Map<String, Object> aiResult = aiEngineClient.checkHealth();
            response.put("status", "ok");
            response.put("service_to_service_auth", "verified");
            response.put("ai_engine", aiResult);
            return ResponseEntity.ok(response);
        } catch (Exception ex) {
            response.put("status", "error");
            response.put("service_to_service_auth", "failed");
            response.put("error", ex.getMessage());
            return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE).body(response);
        }
    }
}
