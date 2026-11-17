package com.lexilegal.controller;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.dto.request.RegisterRequest;
import com.lexilegal.dto.response.AuthResponse;
import com.lexilegal.entity.*;
import com.lexilegal.repository.*;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;

import java.math.BigDecimal;
import java.util.UUID;

import static org.hamcrest.Matchers.*;
import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest
@AutoConfigureMockMvc
class DashboardAndReportTest {

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private DocumentRepository documentRepository;

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

    private String tokenA;
    private User userA;
    private Document docA;

    @BeforeEach
    void setUp() throws Exception {
        String emailA = "test_phase9_" + UUID.randomUUID().toString().substring(0, 8) + "@lexilegal.ai";
        RegisterRequest reqA = new RegisterRequest(emailA, "Password123!", "Alice Phase9");

        MvcResult resA = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reqA)))
                .andExpect(status().isCreated())
                .andReturn();

        AuthResponse authA = objectMapper.readValue(resA.getResponse().getContentAsString(), AuthResponse.class);
        tokenA = authA.getToken();
        userA = userRepository.findById(authA.getUser().getId()).orElseThrow();

        // Create completed document for User A
        docA = new Document();
        docA.setUser(userA);
        docA.setOriginalFilename("test_commercial_lease.pdf");
        docA.setStoragePath("/tmp/test_commercial_lease.pdf");
        docA.setFileType("PDF");
        docA.setFileSize(45000L);
        docA.setFileHash(UUID.randomUUID().toString().replace("-", ""));
        docA.setPageCount(3);
        docA.setIsScanned(false);
        docA.setStatus("COMPLETED");
        docA = documentRepository.save(docA);

        // Analysis
        DocumentAnalysis analysis = new DocumentAnalysis();
        analysis.setDocument(docA);
        analysis.setTitle("Commercial Lease Agreement");
        analysis.setDocumentType("Lease Agreement");
        analysis.setSummaryShort("A 3-year commercial lease for downtown office space.");
        analysis.setSummaryDetailed("Detailed lease terms including rent, maintenance covenants, and early termination penalties.");
        analysis.setLlmProvider("gemini");
        analysis.setLlmModel("gemini-3.5-flash-lite");
        analysis.setVerificationRate(BigDecimal.valueOf(100.0));
        analysis.setParties("[{\"name\":\"Downtown Holdings LLC\",\"role\":\"Landlord\"},{\"name\":\"Tech Ventures Inc\",\"role\":\"Tenant\"}]");
        analysis = documentAnalysisRepository.save(analysis);

        // Extracted Clause
        ExtractedClause clause = new ExtractedClause();
        clause.setAnalysis(analysis);
        clause.setTitle("Monthly Rent Payment");
        clause.setCategory("Financial");
        clause.setOriginalText("Tenant shall pay rent of $5,000 on the first day of each month.");
        clause.setSimplifiedSimple("You pay $5,000 rent on the 1st of every month.");
        clause.setSimplifiedDetailed("Monthly rent is set at $5,000 due in advance on the 1st.");
        clause.setSimplifiedProfessional("Rent covenant obligates monthly disbursement of $5,000.");
        clause.setImportance("HIGH");
        clause.setSourcePage(1);
        clause.setEvidenceQuote("Tenant shall pay rent of $5,000");
        clause.setQuoteVerified(true);
        clause.setProvenance("EXTRACTED");
        extractedClauseRepository.save(clause);

        // Risk Finding
        RiskFinding risk = new RiskFinding();
        risk.setAnalysis(analysis);
        risk.setLevel("HIGH");
        risk.setCategory("FINANCIAL");
        risk.setTitle("Accelerated Rent on Default");
        risk.setOriginalClause("All remaining rent shall accelerate upon default.");
        risk.setExplanation("Landlord can claim all future rent immediately if default is uncured.");
        risk.setWhyItMatters("Significant financial exposure without mitigation requirement.");
        risk.setPossibleConsequences("Immediate multi-thousand dollar liability.");
        risk.setSourcePage(2);
        risk.setEvidenceQuote("All remaining rent shall accelerate upon default.");
        risk.setQuoteVerified(true);
        risk.setProvenance("AI_INTERPRETATION");
        risk.setSuggestedQuestions("[\"Can we add a landlord duty to mitigate damages?\"]");
        riskFindingRepository.save(risk);

        // Key Information
        ExtractedInformation info = new ExtractedInformation();
        info.setAnalysis(analysis);
        info.setContractAmount("$5,000 / month");
        info.setContractAmountPage(1);
        info.setPaymentDeadlines("1st of each month");
        info.setPaymentDeadlinesPage(1);
        info.setPenalties("5% late charge after 5 days");
        info.setPenaltiesPage(1);
        info.setStartDate("2026-01-01");
        info.setStartDatePage(1);
        info.setEndDate("2028-12-31");
        info.setEndDatePage(1);
        info.setRenewalDate("60 days prior to expiry");
        info.setRenewalDatePage(2);
        info.setNoticePeriod("30 days written notice");
        info.setNoticePeriodPage(2);
        info.setTerminationConditions("Notice upon material breach");
        info.setTerminationConditionsPage(3);
        extractedInformationRepository.save(info);

        // Missing Clause Warning
        MissingClauseWarning missing = new MissingClauseWarning();
        missing.setAnalysis(analysis);
        missing.setCategory("Dispute Resolution");
        missing.setClauseName("Arbitration Clause");
        missing.setWhyItMatters("Lacks dispute escalation mechanism before litigation.");
        missing.setTypicalProvision("Commercial leases typically require mediation prior to filing in court.");
        missing.setRiskLevel("MEDIUM");
        missing.setLabel("Possible omission");
        missingClauseWarningRepository.save(missing);
    }

    @Test
    void testGetDashboardStats_Success() throws Exception {
        mockMvc.perform(get("/api/dashboard/stats")
                        .header("Authorization", "Bearer " + tokenA))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalDocuments", is(1)))
                .andExpect(jsonPath("$.analyzedDocuments", is(1)))
                .andExpect(jsonPath("$.failedDocuments", is(0)))
                .andExpect(jsonPath("$.totalClauses", is(1)))
                .andExpect(jsonPath("$.totalRisks", is(1)))
                .andExpect(jsonPath("$.riskDistributionByLevel.HIGH", is(1)))
                .andExpect(jsonPath("$.riskDistributionByCategory.FINANCIAL", is(1)))
                .andExpect(jsonPath("$.recentDocuments", hasSize(1)))
                .andExpect(jsonPath("$.recentDocuments[0].originalFilename", is("test_commercial_lease.pdf")))
                .andExpect(jsonPath("$.recentAnalyses", hasSize(1)))
                .andExpect(jsonPath("$.recentAnalyses[0].title", is("Commercial Lease Agreement")));
    }

    @Test
    void testGetDashboardStats_MultiTenantIsolation() throws Exception {
        // Register User B
        String emailB = "test_user_b_" + UUID.randomUUID().toString().substring(0, 8) + "@lexilegal.ai";
        RegisterRequest reqB = new RegisterRequest(emailB, "Password123!", "Bob Beta");

        MvcResult resB = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reqB)))
                .andExpect(status().isCreated())
                .andReturn();

        AuthResponse authB = objectMapper.readValue(resB.getResponse().getContentAsString(), AuthResponse.class);

        // User B has 0 documents
        mockMvc.perform(get("/api/dashboard/stats")
                        .header("Authorization", "Bearer " + authB.getToken()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalDocuments", is(0)))
                .andExpect(jsonPath("$.analyzedDocuments", is(0)))
                .andExpect(jsonPath("$.totalClauses", is(0)))
                .andExpect(jsonPath("$.totalRisks", is(0)))
                .andExpect(jsonPath("$.recentDocuments", hasSize(0)));
    }

    @Test
    void testDownloadReportPdf_Success() throws Exception {
        MvcResult result = mockMvc.perform(get("/api/documents/" + docA.getId() + "/report.pdf")
                        .header("Authorization", "Bearer " + tokenA))
                .andExpect(status().isOk())
                .andExpect(header().string("Content-Type", "application/pdf"))
                .andExpect(header().string("Content-Disposition", containsString("lexilegal_report_")))
                .andReturn();

        byte[] pdfBytes = result.getResponse().getContentAsByteArray();
        assertNotNull(pdfBytes);
        assertTrue(pdfBytes.length > 500, "PDF should be non-empty and well-structured");

        // Verify PDF Magic Bytes (%PDF-)
        String header = new String(pdfBytes, 0, 5);
        assertEquals("%PDF-", header, "Generated file must start with valid PDF magic bytes %PDF-");
    }

    @Test
    void testDownloadReportPdf_MultiTenantIsolation_Returns404() throws Exception {
        // Register User B
        String emailB = "test_user_b_" + UUID.randomUUID().toString().substring(0, 8) + "@lexilegal.ai";
        RegisterRequest reqB = new RegisterRequest(emailB, "Password123!", "Bob Beta");

        MvcResult resB = mockMvc.perform(post("/api/auth/register")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(reqB)))
                .andExpect(status().isCreated())
                .andReturn();

        AuthResponse authB = objectMapper.readValue(resB.getResponse().getContentAsString(), AuthResponse.class);

        // User B tries to download User A's report -> strictly 404
        mockMvc.perform(get("/api/documents/" + docA.getId() + "/report.pdf")
                        .header("Authorization", "Bearer " + authB.getToken()))
                .andExpect(status().isNotFound());
    }
}

