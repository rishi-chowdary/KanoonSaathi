package com.lexilegal.controller;

import com.lexilegal.dto.response.*;
import com.lexilegal.security.UserPrincipal;
import com.lexilegal.service.DocumentService;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.Map;
import java.util.UUID;

@RestController
@RequestMapping("/api/documents")
public class DocumentController {

    private final DocumentService documentService;

    public DocumentController(DocumentService documentService) {
        this.documentService = documentService;
    }

    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<DocumentUploadResponse> upload(
            @AuthenticationPrincipal UserPrincipal principal,
            @RequestParam("file") MultipartFile file) {
        DocumentUploadResponse response = documentService.upload(principal.getId(), file);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(response);
    }

    @GetMapping
    public ResponseEntity<PageResponse<DocumentResponse>> list(
            @AuthenticationPrincipal UserPrincipal principal,
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "10") int size,
            @RequestParam(name = "search", required = false) String search,
            @RequestParam(name = "status", required = false) String status) {
        PageResponse<DocumentResponse> response = documentService.listDocuments(principal.getId(), page, size, search, status);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<DocumentResponse> getDocument(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id) {
        DocumentResponse response = documentService.getDocument(principal.getId(), id);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}/status")
    public ResponseEntity<DocumentStatusResponse> getStatus(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id) {
        DocumentStatusResponse response = documentService.getStatus(principal.getId(), id);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}/text")
    public ResponseEntity<DocumentTextResponse> getText(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id,
            @RequestParam(name = "page", required = false) Integer page) {
        DocumentTextResponse response = documentService.getText(principal.getId(), id, page);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}/analysis")
    public ResponseEntity<AnalysisSummaryResponse> getAnalysis(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id) {
        AnalysisSummaryResponse response = documentService.getAnalysis(principal.getId(), id);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}/clauses")
    public ResponseEntity<PageResponse<ClauseResponse>> getClauses(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id,
            @RequestParam(name = "category", required = false) String category,
            @RequestParam(name = "importance", required = false) String importance,
            @RequestParam(name = "search", required = false) String search,
            @RequestParam(name = "page", defaultValue = "0") int page,
            @RequestParam(name = "size", defaultValue = "10") int size) {
        PageResponse<ClauseResponse> response = documentService.getClauses(
                principal.getId(), id, category, importance, search, page, size
        );
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}/risks")
    public ResponseEntity<java.util.List<RiskFindingResponse>> getRisks(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id,
            @RequestParam(name = "level", required = false) String level,
            @RequestParam(name = "category", required = false) String category) {
        java.util.List<RiskFindingResponse> response = documentService.getRiskFindings(principal.getId(), id, level, category);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}/key-info")
    public ResponseEntity<KeyInformationResponse> getKeyInfo(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id) {
        KeyInformationResponse response = documentService.getKeyInformation(principal.getId(), id);
        return ResponseEntity.ok(response != null ? response : new KeyInformationResponse());
    }

    @GetMapping("/{id}/missing")
    public ResponseEntity<java.util.List<MissingClauseWarningResponse>> getMissing(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id) {
        java.util.List<MissingClauseWarningResponse> response = documentService.getMissingClauseWarnings(principal.getId(), id);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{id}/clauses/{clauseId}/re-explain")
    public ResponseEntity<ReExplainClauseResponse> reExplainClause(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id,
            @PathVariable("clauseId") UUID clauseId,
            @RequestParam(name = "mode", defaultValue = "simple_english") String mode) {
        ReExplainClauseResponse response = documentService.reExplainClause(principal.getId(), id, clauseId, mode);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/{id}/reanalyze")
    public ResponseEntity<Map<String, String>> reanalyze(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id) {
        documentService.reanalyze(principal.getId(), id);
        return ResponseEntity.status(HttpStatus.ACCEPTED).body(Map.of(
                "status", "ANALYZING",
                "message", "Document reanalysis triggered successfully"
        ));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID id) {
        documentService.deleteDocument(principal.getId(), id);
        return ResponseEntity.noContent().build();
    }
}
