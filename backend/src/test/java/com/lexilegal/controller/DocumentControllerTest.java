package com.lexilegal.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.dto.request.RegisterRequest;
import com.lexilegal.dto.response.AuthResponse;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.User;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.util.UUID;

import static org.hamcrest.Matchers.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class DocumentControllerTest {

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

    private String userAToken;
    private User userA;
    private String userBToken;
    private User userB;

    @BeforeEach
    void setUp() throws Exception {
        documentChunkRepository.deleteAll();
        documentRepository.deleteAll();
        userRepository.deleteAll();

        // Register user A
        RegisterRequest reqA = new RegisterRequest("usera@example.com", "Password123", "User A");
        MvcResult resA = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reqA)))
                .andExpect(status().isCreated())
                .andReturn();
        AuthResponse authA = objectMapper.readValue(resA.getResponse().getContentAsString(), AuthResponse.class);
        userAToken = authA.getToken();
        userA = userRepository.findByEmail("usera@example.com").orElseThrow();

        // Register user B
        RegisterRequest reqB = new RegisterRequest("userb@example.com", "Password123", "User B");
        MvcResult resB = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reqB)))
                .andExpect(status().isCreated())
                .andReturn();
        AuthResponse authB = objectMapper.readValue(resB.getResponse().getContentAsString(), AuthResponse.class);
        userBToken = authB.getToken();
        userB = userRepository.findByEmail("userb@example.com").orElseThrow();
    }

    @Test
    void testUploadPdfSuccess() throws Exception {
        byte[] pdfContent = "%PDF-1.4 sample pdf content for unit testing".getBytes();
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "contract.pdf",
                "application/pdf",
                pdfContent
        );

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.id", notNullValue()))
                .andExpect(jsonPath("$.originalFilename", is("contract.pdf")))
                .andExpect(jsonPath("$.duplicate", is(false)));
    }

    @Test
    void testUploadDuplicateDocument() throws Exception {
        byte[] pdfContent = "%PDF-1.4 identical sample contract".getBytes();
        MockMultipartFile file1 = new MockMultipartFile("file", "contract1.pdf", "application/pdf", pdfContent);
        MockMultipartFile file2 = new MockMultipartFile("file", "contract2.pdf", "application/pdf", pdfContent);

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file1)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.duplicate", is(false)));

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file2)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.duplicate", is(true)));
    }

    @Test
    void testUploadExecutableRejection() throws Exception {
        byte[] mzContent = new byte[] {0x4D, 0x5A, (byte) 0x90, 0x00, 0x03, 0x00, 0x00, 0x00};
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "malicious.pdf",
                "application/pdf",
                mzContent
        );

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message", containsString("executable files are not allowed")));
    }

    @Test
    void testUploadMismatchMagicBytes() throws Exception {
        byte[] badContent = "random text string without pdf header".getBytes();
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "fake.pdf",
                "application/pdf",
                badContent
        );

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message", containsString("does not match declared PDF format")));
    }

    @Test
    void testListDocuments() throws Exception {
        byte[] pdfContent = "%PDF-1.4 file content".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "test.pdf", "application/pdf", pdfContent);

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted());

        mockMvc.perform(get("/api/documents")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements", is(1)))
                .andExpect(jsonPath("$.content[0].originalFilename", is("test.pdf")));
    }

    @Test
    void testDocumentOwnershipIsolation() throws Exception {
        byte[] pdfContent = "%PDF-1.4 confidential file".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "secret.pdf", "application/pdf", pdfContent);

        MvcResult uploadResult = mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andReturn();

        String docId = objectMapper.readTree(uploadResult.getResponse().getContentAsString()).get("id").asText();

        // User A can access
        mockMvc.perform(get("/api/documents/" + docId)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id", is(docId)));

        // User B must get 404 (never 403 to prevent enumeration)
        mockMvc.perform(get("/api/documents/" + docId)
                        .header("Authorization", "Bearer " + userBToken))
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.message", is("document not found")));
    }

    @Test
    void testDeleteDocument() throws Exception {
        byte[] pdfContent = "%PDF-1.4 to be deleted".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "delete_me.pdf", "application/pdf", pdfContent);

        MvcResult uploadResult = mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andReturn();

        String docId = objectMapper.readTree(uploadResult.getResponse().getContentAsString()).get("id").asText();

        // Delete document
        mockMvc.perform(delete("/api/documents/" + docId)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isNoContent());

        // Subsequent access should return 404
        mockMvc.perform(get("/api/documents/" + docId)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isNotFound());
    }
}
