package com.lexilegal.controller;

import com.lexilegal.dto.request.ChatQuestionRequest;
import com.lexilegal.dto.response.ChatConversationResponse;
import com.lexilegal.dto.response.ChatMessageResponse;
import com.lexilegal.security.UserPrincipal;
import com.lexilegal.service.ChatService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/documents/{id}/chat")
public class ChatController {

    private final ChatService chatService;

    public ChatController(ChatService chatService) {
        this.chatService = chatService;
    }

    @PostMapping
    public ResponseEntity<ChatMessageResponse> sendMessage(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID documentId,
            @Valid @RequestBody ChatQuestionRequest request) {
        ChatMessageResponse response = chatService.sendMessage(principal.getId(), documentId, request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/conversations")
    public ResponseEntity<List<ChatConversationResponse>> getConversations(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID documentId) {
        List<ChatConversationResponse> response = chatService.getConversations(principal.getId(), documentId);
        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<List<ChatConversationResponse>> getConversationsDefault(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID documentId) {
        return getConversations(principal, documentId);
    }

    @GetMapping("/conversations/{conversationId}/messages")
    public ResponseEntity<List<ChatMessageResponse>> getMessages(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID documentId,
            @PathVariable("conversationId") UUID conversationId) {
        List<ChatMessageResponse> response = chatService.getMessages(principal.getId(), documentId, conversationId);
        return ResponseEntity.ok(response);
    }

    @DeleteMapping("/conversations/{conversationId}")
    public ResponseEntity<Void> deleteConversation(
            @AuthenticationPrincipal UserPrincipal principal,
            @PathVariable("id") UUID documentId,
            @PathVariable("conversationId") UUID conversationId) {
        chatService.deleteConversation(principal.getId(), documentId, conversationId);
        return ResponseEntity.noContent().build();
    }
}
