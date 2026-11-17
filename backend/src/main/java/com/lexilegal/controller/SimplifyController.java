package com.lexilegal.controller;

import com.lexilegal.dto.ai.SimplifyResponseDto;
import com.lexilegal.dto.request.SimplifyRequest;
import com.lexilegal.service.SimplifyService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/simplify")
public class SimplifyController {

    private final SimplifyService simplifyService;

    public SimplifyController(SimplifyService simplifyService) {
        this.simplifyService = simplifyService;
    }

    @PostMapping
    public ResponseEntity<SimplifyResponseDto> simplify(@Valid @RequestBody SimplifyRequest request) {
        SimplifyResponseDto response = simplifyService.simplify(request);
        return ResponseEntity.ok(response);
    }
}

