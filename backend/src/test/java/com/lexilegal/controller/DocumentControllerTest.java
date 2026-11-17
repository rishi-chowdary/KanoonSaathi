package com.lexilegal.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.dto.request.RegisterRequest;
import com.lexilegal.dto.response.AuthResponse;
import com.lexilegal.entity.Document;
import com.lexilegal.entity.User;
import com.lexilegal.entity.DocumentAnalysis;
import com.lexilegal.entity.ExtractedClause;
import com.lexilegal.entity.ExtractedInformation;
import com.lexilegal.entity.MissingClauseWarning;
import com.lexilegal.entity.RiskFinding;
import com.lexilegal.repository.DocumentAnalysisRepository;
import com.lexilegal.repository.DocumentChunkRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.ExtractedClauseRepository;
import com.lexilegal.repository.ExtractedInformationRepository;
import com.lexilegal.repository.MissingClauseWarningRepository;
import com.lexilegal.repository.RiskFindingRepository;
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

    @Autowired
    private DocumentAnalysisRepository documentAnalysisRepository;

    @Autowired
    private ExtractedClauseRepository extractedClauseRepository;

    @Autowired
    private RiskFindingRepository riskFindingRepository;

    @Autowired
    private ExtractedInformationRepository extractedInformationRepository;

    @Autowired
    private MissingClauseWarningRepository missingClauseWarningRepository;

    private String userAToken;
    private User userA;
    private String userBToken;
    private User userB;

    @BeforeEach
    void setUp() throws Exception {
        riskFindingRepository.deleteAll();
        extractedInformationRepository.deleteAll();
        missingClauseWarningRepository.deleteAll();
        extractedClauseRepository.deleteAll();
        documentAnalysisRepository.deleteAll();
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
    void testUploadOversizeFile() throws Exception {
        // 11 MB file exceeds 10MB limit
        byte[] oversizeContent = new byte[11 * 1024 * 1024];
        oversizeContent[0] = 0x25;
        oversizeContent[1] = 0x50;
        oversizeContent[2] = 0x44;
        oversizeContent[3] = 0x46; // %PDF
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "large.pdf",
                "application/pdf",
                oversizeContent
        );

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message", containsString("exceeds maximum allowed size")));
    }

    @Test
    void testUploadBadExtension() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "script.py",
                "text/x-python",
                "print('hello')".getBytes()
        );

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.message", containsString("unsupported file extension")));
    }

    @Test
    void testUploadUnauthenticated() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
                "file",
                "contract.pdf",
                "application/pdf",
                "%PDF-1.4 test".getBytes()
        );

        mockMvc.perform(multipart("/api/documents/upload")
                        .file(file))
                .andExpect(status().isUnauthorized());
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

    @Test
    void testGetAnalysisSuccess() throws Exception {
        byte[] pdfContent = "%PDF-1.4 sample for analysis".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "contract.pdf", "application/pdf", pdfContent);

        MvcResult uploadResult = mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andReturn();

        String docId = objectMapper.readTree(uploadResult.getResponse().getContentAsString()).get("id").asText();
        Document doc = documentRepository.findById(UUID.fromString(docId)).orElseThrow();

        // Create and save a DocumentAnalysis entity
        DocumentAnalysis analysis = new DocumentAnalysis();
        analysis.setDocument(doc);
        analysis.setTitle("Sample NDA");
        analysis.setDocumentType("Non-Disclosure Agreement (NDA)");
        analysis.setPurpose("Protection of proprietary trade secrets");
        analysis.setSummaryShort("A 2-year mutual non-disclosure agreement.");
        analysis.setSummaryDetailed("This agreement establishes reciprocal covenants between the parties.");
        analysis.setParties("[{\"name\":\"Acme Corp\",\"role\":\"Discloser\"}]");
        analysis.setMainConditions("[{\"text\":\"Keep secret\",\"provenance\":\"EXTRACTED\"}]");
        analysis.setObligationsSummary("[]");
        analysis.setFinancialTermsSummary("[]");
        analysis.setLlmProvider("mock");
        analysis.setLlmModel("mock-v1");
        analysis.setVerificationRate(new java.math.BigDecimal("100.00"));
        documentAnalysisRepository.save(analysis);

        // Fetch analysis as User A
        mockMvc.perform(get("/api/documents/" + docId + "/analysis")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.title", is("Sample NDA")))
                .andExpect(jsonPath("$.documentType", is("Non-Disclosure Agreement (NDA)")))
                .andExpect(jsonPath("$.shortSummary", containsString("2-year mutual")))
                .andExpect(jsonPath("$.llmProvider", is("mock")));
    }

    @Test
    void testGetAnalysisCrossTenant404() throws Exception {
        byte[] pdfContent = "%PDF-1.4 sample for tenant isolation".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "tenant.pdf", "application/pdf", pdfContent);

        MvcResult uploadResult = mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andReturn();

        String docId = objectMapper.readTree(uploadResult.getResponse().getContentAsString()).get("id").asText();

        // User B requesting User A's analysis must return 404
        mockMvc.perform(get("/api/documents/" + docId + "/analysis")
                        .header("Authorization", "Bearer " + userBToken))
                .andExpect(status().isNotFound());
    }

    @Test
    void testReanalyzeEndpoint() throws Exception {
        byte[] pdfContent = "%PDF-1.4 sample for reanalyze".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "reanalyze.pdf", "application/pdf", pdfContent);

        MvcResult uploadResult = mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andReturn();

        String docId = objectMapper.readTree(uploadResult.getResponse().getContentAsString()).get("id").asText();

        // User A calls reanalyze -> 202 Accepted
        mockMvc.perform(post("/api/documents/" + docId + "/reanalyze")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andExpect(jsonPath("$.status", is("ANALYZING")));

        // User B calls reanalyze on User A's doc -> 404
        mockMvc.perform(post("/api/documents/" + docId + "/reanalyze")
                        .header("Authorization", "Bearer " + userBToken))
                .andExpect(status().isNotFound());
    }

    @Test
    void testGetClausesSuccessAndFiltering() throws Exception {
        byte[] pdfContent = "%PDF-1.4 sample for clause filtering".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "clauses.pdf", "application/pdf", pdfContent);

        MvcResult uploadResult = mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andReturn();

        String docId = objectMapper.readTree(uploadResult.getResponse().getContentAsString()).get("id").asText();
        Document doc = documentRepository.findById(UUID.fromString(docId)).orElseThrow();

        DocumentAnalysis analysis = new DocumentAnalysis();
        analysis.setDocument(doc);
        analysis.setTitle("Clause Test Agreement");
        analysis.setDocumentType("Contract");
        analysis.setPurpose("Testing");
        analysis.setSummaryShort("Short");
        analysis.setSummaryDetailed("Detailed");
        analysis.setLlmProvider("mock");
        analysis.setLlmModel("mock-v1");
        analysis = documentAnalysisRepository.save(analysis);

        // Clause 1: Confidentiality, HIGH
        ExtractedClause c1 = new ExtractedClause();
        c1.setAnalysis(analysis);
        c1.setTitle("Mutual Confidentiality");
        c1.setCategory("Confidentiality");
        c1.setOriginalText("Parties agree to hold all confidential information secret.");
        c1.setSimplifiedSimple("You must keep information secret.");
        c1.setSimplifiedDetailed("Comprehensive detailed confidentiality terms.");
        c1.setSimplifiedProfessional("Professional confidentiality covenants.");
        c1.setImportance("HIGH");
        c1.setAffectedParty("Both parties");
        c1.setSourcePage(1);
        c1.setEvidenceQuote("hold all confidential information secret");
        c1.setQuoteVerified(true);
        c1.setProvenance("EXTRACTED");
        extractedClauseRepository.save(c1);

        // Clause 2: Termination, MEDIUM
        ExtractedClause c2 = new ExtractedClause();
        c2.setAnalysis(analysis);
        c2.setTitle("Termination for Convenience");
        c2.setCategory("Termination");
        c2.setOriginalText("Either party may cancel with 30 days notice.");
        c2.setSimplifiedSimple("Either party can cancel anytime with notice.");
        c2.setSimplifiedDetailed("Termination requires thirty days advance notice.");
        c2.setSimplifiedProfessional("Provides unilateral termination rights.");
        c2.setImportance("MEDIUM");
        c2.setAffectedParty("Both parties");
        c2.setSourcePage(2);
        c2.setEvidenceQuote("cancel with 30 days notice");
        c2.setQuoteVerified(true);
        c2.setProvenance("EXTRACTED");
        extractedClauseRepository.save(c2);

        // 1. Fetch all clauses
        mockMvc.perform(get("/api/documents/" + docId + "/clauses")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements", is(2)))
                .andExpect(jsonPath("$.content", hasSize(2)))
                .andExpect(jsonPath("$.content[0].category", is("Confidentiality")))
                .andExpect(jsonPath("$.content[0].importance", is("HIGH")))
                .andExpect(jsonPath("$.content[0].quoteVerified", is(true)))
                .andExpect(jsonPath("$.content[0].simplifiedSimple", is("You must keep information secret.")));

        // 2. Filter by category
        mockMvc.perform(get("/api/documents/" + docId + "/clauses")
                        .param("category", "Termination")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements", is(1)))
                .andExpect(jsonPath("$.content[0].category", is("Termination")))
                .andExpect(jsonPath("$.content[0].title", is("Termination for Convenience")));

        // 3. Filter by importance
        mockMvc.perform(get("/api/documents/" + docId + "/clauses")
                        .param("importance", "HIGH")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements", is(1)))
                .andExpect(jsonPath("$.content[0].category", is("Confidentiality")));

        // 4. Search text
        mockMvc.perform(get("/api/documents/" + docId + "/clauses")
                        .param("search", "cancel")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalElements", is(1)))
                .andExpect(jsonPath("$.content[0].title", is("Termination for Convenience")));

        // 5. Cross-tenant access: User B requesting User A's clauses returns 404
        mockMvc.perform(get("/api/documents/" + docId + "/clauses")
                        .header("Authorization", "Bearer " + userBToken))
                .andExpect(status().isNotFound());

        // 6. Unauthenticated returns 401
        mockMvc.perform(get("/api/documents/" + docId + "/clauses"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void testGetRiskFindingsSuccessAndFilter() throws Exception {
        byte[] pdfContent = "%PDF-1.4 risk document test".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "contract.pdf", "application/pdf", pdfContent);
        MvcResult uploadRes = mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andReturn();
        String uploadJson = uploadRes.getResponse().getContentAsString();
        String docId = objectMapper.readTree(uploadJson).get("id").asText();

        Document doc = documentRepository.findById(UUID.fromString(docId)).orElseThrow();
        DocumentAnalysis analysis = new DocumentAnalysis();
        analysis.setDocument(doc);
        analysis.setTitle("Vendor Agreement");
        analysis.setDocumentType("service_agreement");
        analysis.setSummaryShort("Short");
        analysis.setSummaryDetailed("Detailed");
        analysis.setLlmProvider("gemini");
        analysis.setLlmModel("gemini-1.5-flash");
        analysis = documentAnalysisRepository.save(analysis);

        RiskFinding r1 = new RiskFinding();
        r1.setAnalysis(analysis);
        r1.setTitle("Uncapped Indemnification");
        r1.setCategory("Liability");
        r1.setLevel("HIGH");
        r1.setOriginalClause("Vendor indemnifies Customer against all claims without limit.");
        r1.setExplanation("This exposes Vendor to potentially unlimited financial liability.");
        r1.setWhyItMatters("A single lawsuit could exceed the entire contract value.");
        r1.setPossibleConsequences("Significant cash flow disruption or bankruptcy.");
        r1.setSuggestedQuestions("[\"Can we cap indemnification at 12 months fees?\",\"Can we exclude consequential damages?\"]");
        r1.setSourcePage(2);
        r1.setEvidenceQuote("indemnifies Customer against all claims without limit");
        r1.setQuoteVerified(true);
        r1.setJurisdictionCaveat("Governing law is not specified; liability limits vary widely by jurisdiction.");
        r1.setProvenance("AI_INTERPRETATION");
        riskFindingRepository.save(r1);

        RiskFinding r2 = new RiskFinding();
        r2.setAnalysis(analysis);
        r2.setTitle("Late Payment Penalty");
        r2.setCategory("Financial");
        r2.setLevel("MEDIUM");
        r2.setOriginalClause("Late payments accrue 2% per month interest.");
        r2.setExplanation("High interest rate on late invoices.");
        r2.setWhyItMatters("Compounding charges if invoicing issues occur.");
        r2.setPossibleConsequences("Additional financing costs.");
        r2.setSuggestedQuestions("[\"Can the grace period be extended to 30 days?\"]");
        r2.setSourcePage(3);
        r2.setEvidenceQuote("2% per month interest");
        r2.setQuoteVerified(true);
        r2.setProvenance("AI_INTERPRETATION");
        riskFindingRepository.save(r2);

        // Fetch all risks
        mockMvc.perform(get("/api/documents/" + docId + "/risks")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(2)))
                .andExpect(jsonPath("$[0].title", is("Uncapped Indemnification")))
                .andExpect(jsonPath("$[0].level", is("HIGH")))
                .andExpect(jsonPath("$[0].category", is("Liability")))
                .andExpect(jsonPath("$[0].suggestedQuestions", hasSize(2)))
                .andExpect(jsonPath("$[0].jurisdictionCaveat", containsString("Governing law is not specified")));

        // Filter by level HIGH
        mockMvc.perform(get("/api/documents/" + docId + "/risks")
                        .param("level", "HIGH")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].title", is("Uncapped Indemnification")));

        // Filter by category Financial
        mockMvc.perform(get("/api/documents/" + docId + "/risks")
                        .param("category", "Financial")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].title", is("Late Payment Penalty")));

        // Cross-tenant: User B accessing User A's risks gets 404
        mockMvc.perform(get("/api/documents/" + docId + "/risks")
                        .header("Authorization", "Bearer " + userBToken))
                .andExpect(status().isNotFound());

        // Unauthenticated gets 401
        mockMvc.perform(get("/api/documents/" + docId + "/risks"))
                .andExpect(status().isUnauthorized());
    }

    @Test
    void testGetKeyInformationAndMissingProvisions() throws Exception {
        byte[] pdfContent = "%PDF-1.4 key info test".getBytes();
        MockMultipartFile file = new MockMultipartFile("file", "lease.pdf", "application/pdf", pdfContent);
        MvcResult uploadRes = mockMvc.perform(multipart("/api/documents/upload")
                        .file(file)
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isAccepted())
                .andReturn();
        String uploadJson = uploadRes.getResponse().getContentAsString();
        String docId = objectMapper.readTree(uploadJson).get("id").asText();

        Document doc = documentRepository.findById(UUID.fromString(docId)).orElseThrow();
        DocumentAnalysis analysis = new DocumentAnalysis();
        analysis.setDocument(doc);
        analysis.setTitle("Commercial Lease");
        analysis.setDocumentType("rental_lease");
        analysis.setSummaryShort("Lease summary");
        analysis.setSummaryDetailed("Detailed lease summary");
        analysis.setLlmProvider("gemini");
        analysis.setLlmModel("gemini-1.5-flash");
        analysis = documentAnalysisRepository.save(analysis);

        // Key info
        ExtractedInformation keyInfo = new ExtractedInformation();
        keyInfo.setAnalysis(analysis);
        keyInfo.setContractAmount("$2,500 per month");
        keyInfo.setContractAmountPage(1);
        keyInfo.setPaymentDeadlines("First of each month");
        keyInfo.setPaymentDeadlinesPage(1);
        keyInfo.setPenalties("5% late fee after 5 days");
        keyInfo.setPenaltiesPage(2);
        keyInfo.setStartDate("January 1, 2026");
        keyInfo.setStartDatePage(1);
        keyInfo.setEndDate("December 31, 2026");
        keyInfo.setEndDatePage(1);
        keyInfo.setRenewalDate("Not specified");
        keyInfo.setNoticePeriod("60 days written notice");
        keyInfo.setNoticePeriodPage(3);
        keyInfo.setTerminationConditions("Material breach with 14-day cure period");
        keyInfo.setTerminationConditionsPage(4);
        keyInfo.setObligations("[\"Maintain commercial general liability insurance\",\"Keep premises in good repair\"]");
        keyInfo.setImportantDates("[{\"event\":\"Lease Commencement\",\"date_value\":\"January 1, 2026\",\"source_page\":1}]");
        extractedInformationRepository.save(keyInfo);

        // Missing provisions
        MissingClauseWarning w1 = new MissingClauseWarning();
        w1.setAnalysis(analysis);
        w1.setCategory("Contractual");
        w1.setClauseName("Subleasing Rights");
        w1.setWhyItMatters("Specifies whether tenant can sublet space or assign the lease.");
        w1.setTypicalProvision("Tenant shall not assign or sublet without Landlord's prior written consent.");
        w1.setRiskLevel("MEDIUM");
        w1.setLabel("Possible omission");
        missingClauseWarningRepository.save(w1);

        // 1. Fetch Key Info
        mockMvc.perform(get("/api/documents/" + docId + "/key-info")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.contractAmount", is("$2,500 per month")))
                .andExpect(jsonPath("$.contractAmountPage", is(1)))
                .andExpect(jsonPath("$.startDate", is("January 1, 2026")))
                .andExpect(jsonPath("$.renewalDate", is("Not specified")))
                .andExpect(jsonPath("$.obligations", hasSize(2)))
                .andExpect(jsonPath("$.importantDates", hasSize(1)));

        // 2. Fetch Missing Provisions
        mockMvc.perform(get("/api/documents/" + docId + "/missing")
                        .header("Authorization", "Bearer " + userAToken))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$", hasSize(1)))
                .andExpect(jsonPath("$[0].clauseName", is("Subleasing Rights")))
                .andExpect(jsonPath("$[0].riskLevel", is("MEDIUM")))
                .andExpect(jsonPath("$[0].label", is("Possible omission")));

        // 3. Cross-tenant for Key Info and Missing
        mockMvc.perform(get("/api/documents/" + docId + "/key-info")
                        .header("Authorization", "Bearer " + userBToken))
                .andExpect(status().isNotFound());

        mockMvc.perform(get("/api/documents/" + docId + "/missing")
                        .header("Authorization", "Bearer " + userBToken))
                .andExpect(status().isNotFound());

        // 4. Unauthenticated for Key Info and Missing
        mockMvc.perform(get("/api/documents/" + docId + "/key-info"))
                .andExpect(status().isUnauthorized());

        mockMvc.perform(get("/api/documents/" + docId + "/missing"))
                .andExpect(status().isUnauthorized());
    }
}
