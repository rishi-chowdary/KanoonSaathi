package com.lexilegal.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.dto.ai.ChatResponseDto;
import com.lexilegal.dto.ai.CitationItemDto;
import com.lexilegal.dto.request.ChatQuestionRequest;
import com.lexilegal.dto.request.RegisterRequest;
import com.lexilegal.dto.response.AuthResponse;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.DocumentChunk;
import com.lexilegal.entity.User;
import com.lexilegal.repository.ChatConversationRepository;
import com.lexilegal.repository.ChatMessageRepository;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.UserRepository;
import com.lexilegal.service.client.AiEngineClient;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.util.List;
import java.util.UUID;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class ChatControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private DocumentRepository documentRepository;

    @Autowired
    private DocumentChunkRepository documentChunkRepository;

    @Autowired
    private ChatConversationRepository chatConversationRepository;

    @Autowired
    private ChatMessageRepository chatMessageRepository;

    @Autowired
    private AiEngineClient aiEngineClient;

    private String userToken;
    private User testUser;
    private Document testDoc;

    @BeforeEach
    void setUp() throws Exception {
        chatMessageRepository.deleteAll();
        chatConversationRepository.deleteAll();
        documentChunkRepository.deleteAll();
        documentRepository.deleteAll();
        userRepository.deleteAll();

        // Register test user
        String email = "chatuser_" + UUID.randomUUID() + "@lexilegal.ai";
        RegisterRequest registerReq = new RegisterRequest(email, "Password123!", "Chat User");
        MvcResult authResult = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(registerReq)))
                .andExpect(status().isCreated())
                .andReturn();

        AuthResponse authResponse = objectMapper.readValue(
                authResult.getResponse().getContentAsString(),
                AuthResponse.class
        );
        userToken = authResponse.getToken();
        testUser = userRepository.findById(authResponse.getUser().getId()).orElseThrow();

        // Create a test document
        testDoc = new Document();
        testDoc.setUser(testUser);
        testDoc.setOriginalFilename("test_contract.pdf");
        testDoc.setStoragePath("/tmp/test_contract.pdf");
        testDoc.setFileType("pdf");
        testDoc.setFileSize(2048L);
        testDoc.setFileHash("hash_" + UUID.randomUUID());
        testDoc.setPageCount(2);
        testDoc.setStatus("COMPLETED");
        testDoc = documentRepository.save(testDoc);

        // Create test chunks
        DocumentChunk chunk1 = new DocumentChunk();
        chunk1.setDocument(testDoc);
        chunk1.setChunkIndex(0);
        chunk1.setPageNumber(1);
        chunk1.setContent("Tenant agrees to pay monthly rent of $2,400.00 on the first day of each month.");
        chunk1.setTokenCount(20);
        documentChunkRepository.save(chunk1);

        DocumentChunk chunk2 = new DocumentChunk();
        chunk2.setDocument(testDoc);
        chunk2.setChunkIndex(1);
        chunk2.setPageNumber(2);
        chunk2.setContent("Notice period for lease termination is thirty (30) days in writing.");
        chunk2.setTokenCount(18);
        documentChunkRepository.save(chunk2);
    }

    @Test
    void testChatEndpointRequiresAuth() throws Exception {
        ChatQuestionRequest req = new ChatQuestionRequest(null, "What is the monthly rent?");
        mockMvc.perform(post("/api/documents/" + testDoc.getId() + "/chat")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void testSendMessageSuccessAndCreatesConversation() throws Exception {
        ChatQuestionRequest req = new ChatQuestionRequest(null, "What is the monthly rent?");

        mockMvc.perform(post("/api/documents/" + testDoc.getId() + "/chat")
                        .header("Authorization", "Bearer " + userToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.role", is("assistant")))
                .andExpect(jsonPath("$.content", containsString("$2,400.00")))
                .andExpect(jsonPath("$.addressedInDocument", is(true)))
                .andExpect(jsonPath("$.citations", hasSize(1)))
                .andExpect(jsonPath("$.citations[0].page", is(1)))
                .andExpect(jsonPath("$.citations[0].quoteVerified", is(true)));

        // Verify conversation was created
        mockMvc.perform(get("/api/documents/" + testDoc.getId() + "/chat/conversations")
                        .header("Authorization", "Bearer " + userToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].title", containsString("What is the monthly rent?")));
    }

    @Test
    void testCrossTenantIsolationReturns404() throws Exception {
        // Register second user
        String email2 = "other_" + UUID.randomUUID() + "@lexilegal.ai";
        RegisterRequest registerReq2 = new RegisterRequest(email2, "Password123!", "Other User");
        MvcResult authResult2 = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(registerReq2)))
                .andExpect(status().isCreated())
                .andReturn();

        AuthResponse authResponse2 = objectMapper.readValue(
                authResult2.getResponse().getContentAsString(),
                AuthResponse.class
        );
        String otherToken = authResponse2.getToken();

        // Other user attempts to chat on testDoc -> strictly 404 (never 403 or 200)
        ChatQuestionRequest req = new ChatQuestionRequest(null, "What is the monthly rent?");
        mockMvc.perform(post("/api/documents/" + testDoc.getId() + "/chat")
                        .header("Authorization", "Bearer " + otherToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isNotFound());
    }

    @Test
    void testGetMessagesAndDeleteConversation() throws Exception {
        // Send first message to initialize conversation
        ChatQuestionRequest req = new ChatQuestionRequest(null, "What is the notice period?");
        MvcResult sendRes = mockMvc.perform(post("/api/documents/" + testDoc.getId() + "/chat")
                        .header("Authorization", "Bearer " + userToken)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(req)))
                .andExpect(status().isOk())
                .andReturn();

        UUID convId = objectMapper.readTree(sendRes.getResponse().getContentAsString()).get("conversationId").asText() != null
                ? UUID.fromString(objectMapper.readTree(sendRes.getResponse().getContentAsString()).get("conversationId").asText())
                : null;

        // Fetch messages for conversation
        mockMvc.perform(get("/api/documents/" + testDoc.getId() + "/chat/conversations/" + convId + "/messages")
                        .header("Authorization", "Bearer " + userToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2))) // User message + Assistant message
                .andExpect(jsonPath("$[0].role", is("user")))
                .andExpect(jsonPath("$[1].role", is("assistant")));

        // Delete conversation
        mockMvc.perform(delete("/api/documents/" + testDoc.getId() + "/chat/conversations/" + convId)
                        .header("Authorization", "Bearer " + userToken))
                .andExpect(status().isNoContent());

        // Verify conversation is gone
        mockMvc.perform(get("/api/documents/" + testDoc.getId() + "/chat/conversations")
                        .header("Authorization", "Bearer " + userToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(0)));
    }
}
