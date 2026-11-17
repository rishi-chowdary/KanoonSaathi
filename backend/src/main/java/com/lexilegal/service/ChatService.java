package com.lexilegal.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.dto.ai.ChatMessageHistoryDto;
import com.lexilegal.dto.ai.ChatRequestDto;
import com.lexilegal.dto.ai.ChatResponseDto;
import com.lexilegal.dto.ai.ChatRetrievedChunkDto;
import com.lexilegal.dto.ai.CitationItemDto;
import com.lexilegal.dto.request.ChatQuestionRequest;
import com.lexilegal.dto.response.ChatCitationResponse;
import com.lexilegal.dto.response.ChatConversationResponse;
import com.lexilegal.dto.response.ChatMessageResponse;
import com.lexilegal.entity.ChatConversation;
import com.lexilegal.entity.ChatMessage;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.DocumentChunk;
import com.lexilegal.exception.ResourceNotFoundException;
import com.lexilegal.repository.ChatConversationRepository;
import com.lexilegal.repository.ChatMessageRepository;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.service.client.AiEngineClient;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.UUID;

@Service
public class ChatService {

    private static final Logger log = LoggerFactory.getLogger(ChatService.class);

    private final DocumentRepository documentRepository;
    private final DocumentChunkRepository chunkRepository;
    private final ChatConversationRepository conversationRepository;
    private final ChatMessageRepository messageRepository;
    private final AiEngineClient aiEngineClient;
    private final ObjectMapper objectMapper;

    public ChatService(
            DocumentRepository documentRepository,
            DocumentChunkRepository chunkRepository,
            ChatConversationRepository conversationRepository,
            ChatMessageRepository messageRepository,
            AiEngineClient aiEngineClient,
            ObjectMapper objectMapper) {
        this.documentRepository = documentRepository;
        this.chunkRepository = chunkRepository;
        this.conversationRepository = conversationRepository;
        this.messageRepository = messageRepository;
        this.aiEngineClient = aiEngineClient;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public ChatMessageResponse sendMessage(UUID userId, UUID documentId, ChatQuestionRequest request) {
        Document document = documentRepository.findById(documentId)
                .filter(doc -> doc.getUser().getId().equals(userId))
                .orElseThrow(() -> new ResourceNotFoundException("document not found: " + documentId));

        ChatConversation conversation;
        if (request.conversationId() != null) {
            conversation = conversationRepository.findByIdAndUserId(request.conversationId(), userId)
                    .filter(c -> c.getDocument().getId().equals(documentId))
                    .orElseThrow(() -> new ResourceNotFoundException("conversation not found: " + request.conversationId()));
        } else {
            conversation = new ChatConversation();
            conversation.setDocument(document);
            conversation.setUser(document.getUser());
            String title = request.message().trim();
            if (title.length() > 60) {
                title = title.substring(0, 57) + "...";
            }
            conversation.setTitle(title);
            conversation = conversationRepository.save(conversation);
        }

        // 1. Persist User Message
        ChatMessage userMessage = new ChatMessage();
        userMessage.setConversation(conversation);
        userMessage.setRole("user");
        userMessage.setContent(request.message().trim());
        userMessage.setCitations("[]");
        userMessage.setAddressedInDocument(true);
        messageRepository.save(userMessage);

        // 2. Retrieve Top-k Document Chunks via Full-Text Search
        String query = request.message().trim();
        List<DocumentChunk> retrievedChunks = retrieveRelevantChunks(documentId, query);

        List<ChatRetrievedChunkDto> chunkDtos = retrievedChunks.stream()
                .map(c -> new ChatRetrievedChunkDto(
                        c.getId().toString(),
                        c.getPageNumber(),
                        c.getContent(),
                        "Page " + c.getPageNumber()
                ))
                .toList();

        // 3. Load Recent Conversation History (last 6 messages)
        List<ChatMessage> recentMessages = messageRepository.findTop6ByConversationIdOrderByCreatedAtDesc(conversation.getId());
        List<ChatMessage> chronological = new ArrayList<>(recentMessages);
        Collections.reverse(chronological);

        List<ChatMessageHistoryDto> historyDtos = chronological.stream()
                .map(m -> new ChatMessageHistoryDto(m.getRole(), m.getContent()))
                .toList();

        // 4. Call AI Engine Grounded Chat
        ChatResponseDto aiResponse;
        try {
            aiResponse = aiEngineClient.chat(new ChatRequestDto(query, chunkDtos, historyDtos));
        } catch (Exception e) {
            log.error("ai engine chat invocation failed for document {}", documentId, e);
            aiResponse = new ChatResponseDto(
                    "An error occurred while communicating with the document analysis engine. Please try again.",
                    List.of(),
                    "not found",
                    false
            );
        }

        // 5. Serialize Citations & Persist Assistant Message
        List<ChatCitationResponse> citationResponses = new ArrayList<>();
        if (aiResponse.citations() != null) {
            for (CitationItemDto c : aiResponse.citations()) {
                citationResponses.add(new ChatCitationResponse(
                        c.page(),
                        c.sectionRef(),
                        c.quote(),
                        c.quoteVerified() != null ? c.quoteVerified() : true
                ));
            }
        }

        String citationsJson = "[]";
        try {
            citationsJson = objectMapper.writeValueAsString(citationResponses);
        } catch (Exception e) {
            log.warn("failed to serialize citations json", e);
        }

        ChatMessage assistantMessage = new ChatMessage();
        assistantMessage.setConversation(conversation);
        assistantMessage.setRole("assistant");
        assistantMessage.setContent(aiResponse.answer() != null ? aiResponse.answer() : "No answer generated.");
        assistantMessage.setCitations(citationsJson);
        assistantMessage.setAddressedInDocument(Boolean.TRUE.equals(aiResponse.addressedInDocument()));
        assistantMessage = messageRepository.save(assistantMessage);

        // Update conversation timestamp
        conversation.setUpdatedAt(Instant.now());
        conversationRepository.save(conversation);

        return new ChatMessageResponse(
                assistantMessage.getId(),
                conversation.getId(),
                assistantMessage.getRole(),
                assistantMessage.getContent(),
                citationResponses,
                assistantMessage.getAddressedInDocument(),
                assistantMessage.getCreatedAt()
        );
    }

    private List<DocumentChunk> retrieveRelevantChunks(UUID documentId, String query) {
        // Step A: websearch_to_tsquery
        List<DocumentChunk> chunks = chunkRepository.searchChunksFullText(documentId, query, 5);
        if (!chunks.isEmpty()) {
            return chunks;
        }

        // Step B: plainto_tsquery fallback
        chunks = chunkRepository.searchChunksPlain(documentId, query, 5);
        if (!chunks.isEmpty()) {
            return chunks;
        }

        // Step C: Keyword extraction fallback (filter terms > 3 chars)
        String[] words = query.split("\\s+");
        List<String> keywords = Arrays.stream(words)
                .map(w -> w.replaceAll("[^a-zA-Z0-9]", ""))
                .filter(w -> w.length() > 3)
                .toList();

        if (!keywords.isEmpty()) {
            String orQuery = String.join(" | ", keywords);
            chunks = chunkRepository.searchChunksPlain(documentId, orQuery, 5);
            if (!chunks.isEmpty()) {
                return chunks;
            }
        }

        // Step D: Return first chunks so AI engine has context to evaluate
        return chunkRepository.findTop5ByDocumentIdOrderByChunkIndexAsc(documentId);
    }

    @Transactional(readOnly = true)
    public List<ChatConversationResponse> getConversations(UUID userId, UUID documentId) {
        // Validate document access
        documentRepository.findById(documentId)
                .filter(doc -> doc.getUser().getId().equals(userId))
                .orElseThrow(() -> new ResourceNotFoundException("document not found: " + documentId));

        List<ChatConversation> convs = conversationRepository.findByDocumentIdAndUserIdOrderByUpdatedAtDesc(documentId, userId);
        List<ChatConversationResponse> result = new ArrayList<>();

        for (ChatConversation c : convs) {
            long count = messageRepository.countByConversationId(c.getId());
            ChatMessageResponse lastMsgDto = messageRepository.findTopByConversationIdOrderByCreatedAtDesc(c.getId())
                    .map(this::mapToMessageResponse)
                    .orElse(null);

            result.add(new ChatConversationResponse(
                    c.getId(),
                    c.getDocument().getId(),
                    c.getTitle(),
                    c.getCreatedAt(),
                    c.getUpdatedAt(),
                    (int) count,
                    lastMsgDto
            ));
        }

        return result;
    }

    @Transactional(readOnly = true)
    public List<ChatMessageResponse> getMessages(UUID userId, UUID documentId, UUID conversationId) {
        // Validate document access
        documentRepository.findById(documentId)
                .filter(doc -> doc.getUser().getId().equals(userId))
                .orElseThrow(() -> new ResourceNotFoundException("document not found: " + documentId));

        // Validate conversation access
        ChatConversation conversation = conversationRepository.findByIdAndUserId(conversationId, userId)
                .filter(c -> c.getDocument().getId().equals(documentId))
                .orElseThrow(() -> new ResourceNotFoundException("conversation not found: " + conversationId));

        return messageRepository.findByConversationIdOrderByCreatedAtAsc(conversation.getId()).stream()
                .map(this::mapToMessageResponse)
                .toList();
    }

    @Transactional
    public void deleteConversation(UUID userId, UUID documentId, UUID conversationId) {
        documentRepository.findById(documentId)
                .filter(doc -> doc.getUser().getId().equals(userId))
                .orElseThrow(() -> new ResourceNotFoundException("document not found: " + documentId));

        ChatConversation conversation = conversationRepository.findByIdAndUserId(conversationId, userId)
                .filter(c -> c.getDocument().getId().equals(documentId))
                .orElseThrow(() -> new ResourceNotFoundException("conversation not found: " + conversationId));

        conversationRepository.delete(conversation);
    }

    private ChatMessageResponse mapToMessageResponse(ChatMessage m) {
        List<ChatCitationResponse> citations = new ArrayList<>();
        if (m.getCitations() != null && !m.getCitations().isBlank()) {
            try {
                citations = objectMapper.readValue(m.getCitations(), new TypeReference<List<ChatCitationResponse>>() {});
            } catch (Exception e) {
                log.warn("failed to deserialize citations for message {}", m.getId(), e);
            }
        }

        return new ChatMessageResponse(
                m.getId(),
                m.getConversation().getId(),
                m.getRole(),
                m.getContent(),
                citations,
                m.getAddressedInDocument(),
                m.getCreatedAt()
        );
    }
}
