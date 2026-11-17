package com.lexilegal.service;

import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.lexilegal.entity.DocumentAnalysis;
import com.lexilegal.entity.ExtractedClause;
import com.lexilegal.entity.ExtractedInformation;
import com.lexilegal.entity.MissingClauseWarning;
import com.lexilegal.entity.RiskFinding;
import com.lexilegal.exception.ResourceNotFoundException;
import com.lexilegal.repository.DocumentAnalysisRepository;
import com.lexilegal.repository.DocumentRepository;
import com.lexilegal.repository.ExtractedClauseRepository;
import com.lexilegal.repository.ExtractedInformationRepository;
import com.lexilegal.repository.MissingClauseWarningRepository;
import com.lexilegal.repository.RiskFindingRepository;
import com.lowagie.text.Chunk;
import com.lowagie.text.DocumentException;
import com.lowagie.text.Element;
import com.lowagie.text.Font;
import com.lowagie.text.FontFactory;
import com.lowagie.text.PageSize;
import com.lowagie.text.Paragraph;
import com.lowagie.text.Phrase;
import com.lowagie.text.Rectangle;
import com.lowagie.text.pdf.BaseFont;
import com.lowagie.text.pdf.ColumnText;
import com.lowagie.text.pdf.PdfContentByte;
import com.lowagie.text.pdf.PdfPCell;
import com.lowagie.text.pdf.PdfPTable;
import com.lowagie.text.pdf.PdfPageEventHelper;
import com.lowagie.text.pdf.PdfWriter;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.awt.Color;
import java.io.ByteArrayOutputStream;
import java.math.BigDecimal;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.List;

@Service
@Transactional(readOnly = true)
public class ReportPdfService {

    private final DocumentRepository documentRepository;
    private final DocumentAnalysisRepository documentAnalysisRepository;
    private final ExtractedClauseRepository extractedClauseRepository;
    private final RiskFindingRepository riskFindingRepository;
    private final ExtractedInformationRepository extractedInformationRepository;
    private final MissingClauseWarningRepository missingClauseWarningRepository;
    private final ObjectMapper objectMapper;

    // Palette tokens
    private static final Color COLOR_PRIMARY = new Color(15, 23, 42);       // Navy #0F172A
    private static final Color COLOR_ACCENT = new Color(37, 99, 235);       // Blue #2563EB
    private static final Color COLOR_TEXT_MAIN = new Color(30, 41, 59);     // Slate 800 #1E293B
    private static final Color COLOR_TEXT_MUTED = new Color(100, 116, 139); // Slate 500 #64748B
    private static final Color COLOR_BORDER = new Color(226, 232, 240);     // Slate 200 #E2E8F0
    private static final Color COLOR_BG_LIGHT = new Color(248, 250, 252);   // Slate 50 #F8FAFC
    private static final Color COLOR_BG_ALT = new Color(241, 245, 249);     // Slate 100 #F1F5F9

    // Semantic risk colors
    private static final Color COLOR_RISK_HIGH = new Color(220, 38, 38);
    private static final Color COLOR_RISK_HIGH_BG = new Color(254, 242, 242);
    private static final Color COLOR_RISK_MED = new Color(217, 119, 6);
    private static final Color COLOR_RISK_MED_BG = new Color(254, 243, 199);
    private static final Color COLOR_RISK_LOW = new Color(22, 163, 74);
    private static final Color COLOR_RISK_LOW_BG = new Color(240, 253, 244);
    private static final Color COLOR_RISK_INFO = new Color(37, 99, 235);
    private static final Color COLOR_RISK_INFO_BG = new Color(239, 246, 255);

    // Unicode TrueType Fonts with Helvetica fallback
    private static BaseFont baseFont;
    private static BaseFont baseFontBold;
    private static BaseFont baseFontItalic;

    static {
        try {
            String notoPath = "/usr/share/fonts/google-noto-vf/NotoSans[wght].ttf";
            String notoItalicPath = "/usr/share/fonts/google-noto-vf/NotoSans-Italic[wght].ttf";
            if (new java.io.File(notoPath).exists()) {
                baseFont = BaseFont.createFont(notoPath, BaseFont.IDENTITY_H, BaseFont.EMBEDDED);
                baseFontBold = baseFont;
                baseFontItalic = new java.io.File(notoItalicPath).exists()
                        ? BaseFont.createFont(notoItalicPath, BaseFont.IDENTITY_H, BaseFont.EMBEDDED)
                        : baseFont;
            } else {
                baseFont = BaseFont.createFont(BaseFont.HELVETICA, BaseFont.WINANSI, BaseFont.NOT_EMBEDDED);
                baseFontBold = BaseFont.createFont(BaseFont.HELVETICA_BOLD, BaseFont.WINANSI, BaseFont.NOT_EMBEDDED);
                baseFontItalic = BaseFont.createFont(BaseFont.HELVETICA_OBLIQUE, BaseFont.WINANSI, BaseFont.NOT_EMBEDDED);
            }
        } catch (Exception e) {
            try {
                baseFont = BaseFont.createFont(BaseFont.HELVETICA, BaseFont.WINANSI, BaseFont.NOT_EMBEDDED);
                baseFontBold = BaseFont.createFont(BaseFont.HELVETICA_BOLD, BaseFont.WINANSI, BaseFont.NOT_EMBEDDED);
                baseFontItalic = BaseFont.createFont(BaseFont.HELVETICA_OBLIQUE, BaseFont.WINANSI, BaseFont.NOT_EMBEDDED);
            } catch (Exception ignored) {}
        }
    }

    public static Font font(float size, int style, Color color) {
        BaseFont bf = (style == Font.BOLD) ? baseFontBold : (style == Font.ITALIC ? baseFontItalic : baseFont);
        return new Font(bf, size, style, color);
    }

    // Fonts
    private static final Font FONT_TITLE = font(20, Font.BOLD, COLOR_PRIMARY);
    private static final Font FONT_SUBTITLE = font(10, Font.NORMAL, COLOR_TEXT_MUTED);
    private static final Font FONT_H1 = font(13, Font.BOLD, COLOR_PRIMARY);
    private static final Font FONT_H2 = font(10.5f, Font.BOLD, COLOR_TEXT_MAIN);
    private static final Font FONT_BODY = font(9.5f, Font.NORMAL, COLOR_TEXT_MAIN);
    private static final Font FONT_BODY_BOLD = font(9.5f, Font.BOLD, COLOR_TEXT_MAIN);
    private static final Font FONT_SMALL = font(8.5f, Font.NORMAL, COLOR_TEXT_MUTED);
    private static final Font FONT_SMALL_BOLD = font(8.5f, Font.BOLD, COLOR_TEXT_MAIN);
    private static final Font FONT_PROVENANCE_EXT = font(8f, Font.BOLD, new Color(14, 116, 144));
    private static final Font FONT_PROVENANCE_AI = font(8f, Font.BOLD, new Color(109, 40, 217));

    public ReportPdfService(DocumentRepository documentRepository,
                            DocumentAnalysisRepository documentAnalysisRepository,
                            ExtractedClauseRepository extractedClauseRepository,
                            RiskFindingRepository riskFindingRepository,
                            ExtractedInformationRepository extractedInformationRepository,
                            MissingClauseWarningRepository missingClauseWarningRepository,
                            ObjectMapper objectMapper) {
        this.documentRepository = documentRepository;
        this.documentAnalysisRepository = documentAnalysisRepository;
        this.extractedClauseRepository = extractedClauseRepository;
        this.riskFindingRepository = riskFindingRepository;
        this.extractedInformationRepository = extractedInformationRepository;
        this.missingClauseWarningRepository = missingClauseWarningRepository;
        this.objectMapper = objectMapper;
    }

    public byte[] generatePdfReport(UUID userId, UUID documentId) {
        com.lexilegal.entity.Document document = documentRepository.findByIdAndUserId(documentId, userId)
                .orElseThrow(() -> new ResourceNotFoundException("Document not found"));

        if (!"COMPLETED".equalsIgnoreCase(document.getStatus())) {
            throw new IllegalStateException("Analysis for this document is not completed yet (current status: " + document.getStatus() + ")");
        }

        DocumentAnalysis analysis = documentAnalysisRepository.findByDocumentId(documentId)
                .orElseThrow(() -> new ResourceNotFoundException("Document analysis not found"));

        List<ExtractedClause> clauses = extractedClauseRepository.findByAnalysisId(analysis.getId());
        List<RiskFinding> risks = riskFindingRepository.findByAnalysisId(analysis.getId());
        ExtractedInformation keyInfo = extractedInformationRepository.findByAnalysisId(analysis.getId()).orElse(null);
        List<MissingClauseWarning> missingClauses = missingClauseWarningRepository.findByAnalysisId(analysis.getId());

        ByteArrayOutputStream baos = new ByteArrayOutputStream();
        com.lowagie.text.Document pdfDoc = new com.lowagie.text.Document(PageSize.A4, 36, 36, 46, 42);

        try {
            PdfWriter writer = PdfWriter.getInstance(pdfDoc, baos);
            writer.setPageEvent(new HeaderFooterPageEvent());
            pdfDoc.open();

            // 1. Cover / Overview Section
            addOverviewSection(pdfDoc, document, analysis, keyInfo, clauses.size(), risks.size());

            // 2. Executive Summary
            addExecutiveSummarySection(pdfDoc, analysis);

            // 3. Important Clauses Table
            addClausesTableSection(pdfDoc, clauses);

            // 4. Plain-Language Explanations
            addPlainLanguageSection(pdfDoc, clauses);

            // 5. Risk Analysis
            addRiskAnalysisSection(pdfDoc, risks);

            // 6. Financial Terms
            addFinancialTermsSection(pdfDoc, keyInfo, analysis);

            // 7. Important Dates & Deadlines
            addImportantDatesSection(pdfDoc, keyInfo);

            // 8. Missing / Ambiguous Provisions
            addMissingProvisionsSection(pdfDoc, missingClauses);

            // 9. Suggested Questions to Ask
            addQuestionsToAskSection(pdfDoc, risks, missingClauses);

            // 10. Legal Disclaimer & Notice
            addDisclaimerSection(pdfDoc);

            pdfDoc.close();
            return baos.toByteArray();
        } catch (DocumentException e) {
            throw new RuntimeException("Failed to generate PDF report: " + e.getMessage(), e);
        }
    }

    // -------------------------------------------------------------
    // Section 1: Cover / Overview
    // -------------------------------------------------------------
    private void addOverviewSection(com.lowagie.text.Document doc,
                                    com.lexilegal.entity.Document document,
                                    DocumentAnalysis analysis,
                                    ExtractedInformation keyInfo,
                                    int totalClauses,
                                    int totalRisks) throws DocumentException {
        // Top header banner
        PdfPTable headerTable = new PdfPTable(2);
        headerTable.setWidthPercentage(100);
        headerTable.setWidths(new float[]{70, 30});

        PdfPCell leftCell = new PdfPCell();
        leftCell.setBorder(Rectangle.NO_BORDER);
        leftCell.addElement(new Paragraph("LEXILEGAL AI", font(10, Font.BOLD, COLOR_ACCENT)));
        leftCell.addElement(new Paragraph(analysis.getTitle() != null ? analysis.getTitle() : document.getOriginalFilename(), FONT_TITLE));
        leftCell.addElement(new Paragraph("Comprehensive Contract Review & Risk Intelligence Dossier", FONT_SUBTITLE));
        headerTable.addCell(leftCell);

        PdfPCell rightCell = new PdfPCell();
        rightCell.setBorder(Rectangle.NO_BORDER);
        rightCell.setHorizontalAlignment(Element.ALIGN_RIGHT);
        Paragraph meta = new Paragraph();
        meta.setAlignment(Element.ALIGN_RIGHT);
        meta.add(new Chunk("Report Date: " + DateTimeFormatter.ISO_LOCAL_DATE.format(java.time.LocalDate.now()) + "\n", FONT_SMALL));
        meta.add(new Chunk("Original File: " + document.getOriginalFilename() + "\n", FONT_SMALL));
        meta.add(new Chunk("Format: " + document.getFileType() + " (" + (document.getPageCount() != null ? document.getPageCount() : 1) + " pages)\n", FONT_SMALL));
        meta.add(new Chunk("Verification Rate: " + (analysis.getVerificationRate() != null ? analysis.getVerificationRate() : BigDecimal.ZERO) + "%\n", FONT_SMALL_BOLD));
        rightCell.addElement(meta);
        headerTable.addCell(rightCell);

        doc.add(headerTable);
        doc.add(createDivider());

        Paragraph sec1 = new Paragraph("1. Document Overview & Metadata", FONT_H2);
        sec1.setSpacingBefore(2f);
        sec1.setSpacingAfter(4f);
        doc.add(sec1);

        // Overview Key Metadata Grid
        PdfPTable gridTable = new PdfPTable(4);
        gridTable.setWidthPercentage(100);
        gridTable.setWidths(new float[]{25, 25, 25, 25});
        gridTable.setSpacingBefore(8f);
        gridTable.setSpacingAfter(10f);

        addStatCard(gridTable, "Document Type", analysis.getDocumentType() != null ? analysis.getDocumentType() : "Contract");
        addStatCard(gridTable, "Source Pages", String.valueOf(document.getPageCount() != null ? document.getPageCount() : 1));
        addStatCard(gridTable, "Identified Clauses", String.valueOf(totalClauses));
        addStatCard(gridTable, "Risk Findings", String.valueOf(totalRisks));

        doc.add(gridTable);

        // Parties Overview
        List<Map<String, Object>> parties = parseJsonList(analysis.getParties());
        if (!parties.isEmpty()) {
            Paragraph partiesHead = new Paragraph("Identified Parties [EXTRACTED]", FONT_H2);
            doc.add(partiesHead);

            PdfPTable partiesTable = new PdfPTable(2);
            partiesTable.setWidthPercentage(100);
            partiesTable.setWidths(new float[]{40, 60});
            partiesTable.setSpacingBefore(4f);
            partiesTable.setSpacingAfter(8f);

            for (Map<String, Object> p : parties) {
                String name = Objects.toString(p.get("name"), "Unknown");
                String role = Objects.toString(p.get("role"), "Party");

                PdfPCell nameCell = new PdfPCell(new Phrase(name, FONT_BODY_BOLD));
                nameCell.setBackgroundColor(COLOR_BG_LIGHT);
                nameCell.setBorderColor(COLOR_BORDER);
                nameCell.setPadding(5f);

                PdfPCell roleCell = new PdfPCell(new Phrase(role, FONT_BODY));
                roleCell.setBorderColor(COLOR_BORDER);
                roleCell.setPadding(5f);

                partiesTable.addCell(nameCell);
                partiesTable.addCell(roleCell);
            }
            doc.add(partiesTable);
        }
    }

    // -------------------------------------------------------------
    // Section 2: Executive Summary
    // -------------------------------------------------------------
    private void addExecutiveSummarySection(com.lowagie.text.Document doc, DocumentAnalysis analysis) throws DocumentException {
        doc.add(createSectionHeading("2. Executive Summary"));

        // Concise Summary Box
        PdfPTable box = new PdfPTable(1);
        box.setWidthPercentage(100);
        box.setSpacingBefore(4f);
        box.setSpacingAfter(6f);

        PdfPCell boxCell = new PdfPCell();
        boxCell.setBackgroundColor(COLOR_BG_LIGHT);
        boxCell.setBorderColor(COLOR_BORDER);
        boxCell.setPadding(8f);

        Paragraph label = new Paragraph("CONCISE SUMMARY [AI_INTERPRETATION]", FONT_PROVENANCE_AI);
        boxCell.addElement(label);

        Paragraph shortText = new Paragraph(analysis.getSummaryShort() != null ? analysis.getSummaryShort() : "No summary available.", FONT_BODY);
        shortText.setSpacingBefore(3f);
        boxCell.addElement(shortText);

        box.addCell(boxCell);
        doc.add(box);

        // Detailed Summary
        Paragraph detHead = new Paragraph("Detailed Overview:", FONT_H2);
        detHead.setSpacingBefore(4f);
        detHead.setSpacingAfter(2f);
        doc.add(detHead);

        Paragraph detText = new Paragraph(analysis.getSummaryDetailed() != null ? analysis.getSummaryDetailed() : "", FONT_BODY);
        detText.setSpacingAfter(8f);
        doc.add(detText);
    }

    // -------------------------------------------------------------
    // Section 3: Important Clauses Table
    // -------------------------------------------------------------
    private void addClausesTableSection(com.lowagie.text.Document doc, List<ExtractedClause> clauses) throws DocumentException {
        doc.add(createSectionHeading("3. Important Clauses"));

        if (clauses.isEmpty()) {
            doc.add(new Paragraph("No clauses extracted from this document.", FONT_BODY));
            return;
        }

        PdfPTable table = new PdfPTable(4);
        table.setWidthPercentage(100);
        table.setWidths(new float[]{28, 14, 14, 44});
        table.setSpacingBefore(6f);
        table.setSpacingAfter(8f);

        // Table Header
        addTableHeaderCell(table, "Clause & Category");
        addTableHeaderCell(table, "Importance");
        addTableHeaderCell(table, "Citation");
        addTableHeaderCell(table, "Original Evidence Quote [EXTRACTED]");

        for (ExtractedClause c : clauses) {
            // Title & Category
            PdfPCell c1 = new PdfPCell();
            c1.setBorderColor(COLOR_BORDER);
            c1.setPadding(5f);
            c1.addElement(new Paragraph(c.getTitle(), FONT_BODY_BOLD));
            c1.addElement(new Paragraph(c.getCategory() + (c.getCustomLabel() != null ? " (" + c.getCustomLabel() + ")" : ""), FONT_SMALL));
            table.addCell(c1);

            // Importance
            PdfPCell c2 = new PdfPCell();
            c2.setBorderColor(COLOR_BORDER);
            c2.setPadding(5f);
            c2.addElement(createImportanceBadge(c.getImportance()));
            table.addCell(c2);

            // Citation
            PdfPCell c3 = new PdfPCell();
            c3.setBorderColor(COLOR_BORDER);
            c3.setPadding(5f);
            String ref = "Page " + c.getSourcePage();
            if (c.getSectionReference() != null && !c.getSectionReference().isBlank()) {
                ref += "\n" + c.getSectionReference();
            }
            c3.addElement(new Paragraph(ref, FONT_SMALL_BOLD));
            table.addCell(c3);

            // Evidence quote
            PdfPCell c4 = new PdfPCell();
            c4.setBorderColor(COLOR_BORDER);
            c4.setPadding(5f);
            String quote = c.getEvidenceQuote() != null ? c.getEvidenceQuote() : c.getOriginalText();
            if (quote.length() > 300) {
                quote = quote.substring(0, 300) + "...";
            }
            c4.addElement(new Paragraph("\"" + quote + "\"", font(8.5f, Font.ITALIC, COLOR_TEXT_MAIN)));
            table.addCell(c4);
        }

        doc.add(table);
    }

    // -------------------------------------------------------------
    // Section 4: Plain-Language Explanations (3 Modes)
    // -------------------------------------------------------------
    private void addPlainLanguageSection(com.lowagie.text.Document doc, List<ExtractedClause> clauses) throws DocumentException {
        doc.add(createSectionHeading("4. Plain-Language Clause Explanations"));
        Paragraph intro = new Paragraph(
                "Each clause is provided in three explanatory tiers: Simple English (layperson), Detailed (business operations), and Professional (legal summary).",
                FONT_SMALL
        );
        intro.setSpacingAfter(6f);
        doc.add(intro);

        if (clauses.isEmpty()) {
            doc.add(new Paragraph("No clauses available for explanation.", FONT_BODY));
            return;
        }

        for (ExtractedClause c : clauses) {
            PdfPTable card = new PdfPTable(1);
            card.setWidthPercentage(100);
            card.setSpacingBefore(4f);
            card.setSpacingAfter(6f);

            PdfPCell cell = new PdfPCell();
            cell.setBorderColor(COLOR_BORDER);
            cell.setBackgroundColor(COLOR_BG_LIGHT);
            cell.setPadding(7f);

            // Heading row
            Paragraph h = new Paragraph();
            h.add(new Chunk(c.getTitle() + " ", FONT_H2));
            h.add(new Chunk("(Page " + c.getSourcePage() + ") ", FONT_SMALL));
            h.add(new Chunk("[AI_INTERPRETATION]", FONT_PROVENANCE_AI));
            cell.addElement(h);

            // Simple
            Paragraph pSimple = new Paragraph();
            pSimple.setSpacingBefore(3f);
            pSimple.add(new Chunk("• Simple English: ", FONT_BODY_BOLD));
            pSimple.add(new Chunk(c.getSimplifiedSimple() != null ? c.getSimplifiedSimple() : "N/A", FONT_BODY));
            cell.addElement(pSimple);

            // Detailed
            Paragraph pDetailed = new Paragraph();
            pDetailed.setSpacingBefore(2f);
            pDetailed.add(new Chunk("• Detailed Breakdown: ", FONT_BODY_BOLD));
            pDetailed.add(new Chunk(c.getSimplifiedDetailed() != null ? c.getSimplifiedDetailed() : "N/A", FONT_BODY));
            cell.addElement(pDetailed);

            // Professional
            Paragraph pProf = new Paragraph();
            pProf.setSpacingBefore(2f);
            pProf.add(new Chunk("• Professional Summary: ", FONT_BODY_BOLD));
            pProf.add(new Chunk(c.getSimplifiedProfessional() != null ? c.getSimplifiedProfessional() : "N/A", FONT_BODY));
            cell.addElement(pProf);

            card.addCell(cell);
            doc.add(card);
        }
    }

    // -------------------------------------------------------------
    // Section 5: Risk Analysis (Color Coded)
    // -------------------------------------------------------------
    private void addRiskAnalysisSection(com.lowagie.text.Document doc, List<RiskFinding> risks) throws DocumentException {
        doc.add(createSectionHeading("5. Risk Analysis & Exposure Findings"));

        if (risks.isEmpty()) {
            doc.add(new Paragraph("No specific risks identified in this agreement.", FONT_BODY));
            return;
        }

        for (RiskFinding r : risks) {
            Color levelColor = getRiskLevelColor(r.getLevel());
            Color levelBg = getRiskLevelBg(r.getLevel());

            PdfPTable card = new PdfPTable(1);
            card.setWidthPercentage(100);
            card.setSpacingBefore(4f);
            card.setSpacingAfter(6f);

            PdfPCell cell = new PdfPCell();
            cell.setBorderColor(levelColor);
            cell.setBorderWidth(1.2f);
            cell.setBackgroundColor(levelBg);
            cell.setPadding(7f);

            // Header line
            Paragraph h = new Paragraph();
            h.add(new Chunk("[" + r.getLevel().toUpperCase() + "] ", font(9.5f, Font.BOLD, levelColor)));
            h.add(new Chunk(r.getTitle() + " ", FONT_H2));
            h.add(new Chunk("(" + r.getCategory() + " • Page " + r.getSourcePage() + ") ", FONT_SMALL));
            h.add(new Chunk("[AI_INTERPRETATION]", FONT_PROVENANCE_AI));
            cell.addElement(h);

            // Explanation
            Paragraph pExp = new Paragraph();
            pExp.setSpacingBefore(3f);
            pExp.add(new Chunk("Explanation: ", FONT_BODY_BOLD));
            pExp.add(new Chunk(r.getExplanation(), FONT_BODY));
            cell.addElement(pExp);

            // Why it matters & Consequences
            Paragraph pWhy = new Paragraph();
            pWhy.setSpacingBefore(2f);
            pWhy.add(new Chunk("Why It Matters: ", FONT_BODY_BOLD));
            pWhy.add(new Chunk(r.getWhyItMatters() + " ", FONT_BODY));
            pWhy.add(new Chunk("Consequences: ", FONT_BODY_BOLD));
            pWhy.add(new Chunk(r.getPossibleConsequences(), FONT_BODY));
            cell.addElement(pWhy);

            // Evidence quote
            if (r.getEvidenceQuote() != null && !r.getEvidenceQuote().isBlank()) {
                Paragraph pQuote = new Paragraph();
                pQuote.setSpacingBefore(3f);
                pQuote.add(new Chunk("Evidence Quote [EXTRACTED]: ", FONT_PROVENANCE_EXT));
                pQuote.add(new Chunk("\"" + r.getEvidenceQuote() + "\"", font(8.5f, Font.ITALIC, COLOR_TEXT_MAIN)));
                cell.addElement(pQuote);
            }

            // Jurisdiction caveat
            if (r.getJurisdictionCaveat() != null && !r.getJurisdictionCaveat().isBlank()) {
                Paragraph pCav = new Paragraph("Note: " + r.getJurisdictionCaveat(), font(8f, Font.ITALIC, COLOR_TEXT_MUTED));
                pCav.setSpacingBefore(2f);
                cell.addElement(pCav);
            }

            card.addCell(cell);
            doc.add(card);
        }
    }

    // -------------------------------------------------------------
    // Section 6: Financial Terms
    // -------------------------------------------------------------
    private void addFinancialTermsSection(com.lowagie.text.Document doc, ExtractedInformation info, DocumentAnalysis analysis) throws DocumentException {
        doc.add(createSectionHeading("6. Financial Terms & Payment Schedule"));

        PdfPTable table = new PdfPTable(3);
        table.setWidthPercentage(100);
        table.setWidths(new float[]{30, 55, 15});
        table.setSpacingBefore(5f);
        table.setSpacingAfter(8f);

        addTableHeaderCell(table, "Financial Element");
        addTableHeaderCell(table, "Terms & Provisions [EXTRACTED]");
        addTableHeaderCell(table, "Source Page");

        addFinancialRow(table, "Contract Amount", info != null ? info.getContractAmount() : "Not specified", info != null ? info.getContractAmountPage() : null);
        addFinancialRow(table, "Payment Deadlines", info != null ? info.getPaymentDeadlines() : "Not specified", info != null ? info.getPaymentDeadlinesPage() : null);
        addFinancialRow(table, "Late Fees & Penalties", info != null ? info.getPenalties() : "Not specified", info != null ? info.getPenaltiesPage() : null);

        doc.add(table);
    }

    private void addFinancialRow(PdfPTable table, String element, String value, Integer page) {
        PdfPCell c1 = new PdfPCell(new Phrase(element, FONT_BODY_BOLD));
        c1.setBorderColor(COLOR_BORDER);
        c1.setBackgroundColor(COLOR_BG_LIGHT);
        c1.setPadding(5f);

        PdfPCell c2 = new PdfPCell(new Phrase(value != null ? value : "Not specified", FONT_BODY));
        c2.setBorderColor(COLOR_BORDER);
        c2.setPadding(5f);

        PdfPCell c3 = new PdfPCell(new Phrase(page != null ? "Page " + page : "N/A", FONT_SMALL_BOLD));
        c3.setBorderColor(COLOR_BORDER);
        c3.setPadding(5f);

        table.addCell(c1);
        table.addCell(c2);
        table.addCell(c3);
    }

    // -------------------------------------------------------------
    // Section 7: Important Dates & Deadlines
    // -------------------------------------------------------------
    private void addImportantDatesSection(com.lowagie.text.Document doc, ExtractedInformation info) throws DocumentException {
        doc.add(createSectionHeading("7. Important Dates & Milestones"));

        PdfPTable table = new PdfPTable(3);
        table.setWidthPercentage(100);
        table.setWidths(new float[]{30, 55, 15});
        table.setSpacingBefore(5f);
        table.setSpacingAfter(8f);

        addTableHeaderCell(table, "Milestone Event");
        addTableHeaderCell(table, "Scheduled Date / Period [EXTRACTED]");
        addTableHeaderCell(table, "Source Page");

        addFinancialRow(table, "Start / Effective Date", info != null ? info.getStartDate() : "Not specified", info != null ? info.getStartDatePage() : null);
        addFinancialRow(table, "End / Expiration Date", info != null ? info.getEndDate() : "Not specified", info != null ? info.getEndDatePage() : null);
        addFinancialRow(table, "Renewal Notice Deadline", info != null ? info.getRenewalDate() : "Not specified", info != null ? info.getRenewalDatePage() : null);
        addFinancialRow(table, "Notice Period", info != null ? info.getNoticePeriod() : "Not specified", info != null ? info.getNoticePeriodPage() : null);
        addFinancialRow(table, "Termination Conditions", info != null ? info.getTerminationConditions() : "Not specified", info != null ? info.getTerminationConditionsPage() : null);

        doc.add(table);
    }

    // -------------------------------------------------------------
    // Section 8: Missing Provisions (Possible Omissions)
    // -------------------------------------------------------------
    private void addMissingProvisionsSection(com.lowagie.text.Document doc, List<MissingClauseWarning> warnings) throws DocumentException {
        doc.add(createSectionHeading("8. Missing & Ambiguous Provisions"));

        if (warnings.isEmpty()) {
            doc.add(new Paragraph("No significant contractual omissions were identified for this document type.", FONT_BODY));
            return;
        }

        Paragraph note = new Paragraph(
                "Notice: Items below are marked as 'Possible omission' based on standard industry contracts. Absence does not automatically imply a defect.",
                font(8.5f, Font.ITALIC, COLOR_TEXT_MUTED)
        );
        note.setSpacingAfter(5f);
        doc.add(note);

        for (MissingClauseWarning w : warnings) {
            PdfPTable card = new PdfPTable(1);
            card.setWidthPercentage(100);
            card.setSpacingBefore(4f);
            card.setSpacingAfter(5f);

            PdfPCell cell = new PdfPCell();
            cell.setBorderColor(COLOR_BORDER);
            cell.setBackgroundColor(COLOR_BG_LIGHT);
            cell.setPadding(6f);

            Paragraph h = new Paragraph();
            h.add(new Chunk("[Possible omission] ", font(9f, Font.BOLD, COLOR_RISK_MED)));
            h.add(new Chunk(w.getClauseName() + " ", FONT_H2));
            h.add(new Chunk("(" + w.getCategory() + " • Risk: " + w.getRiskLevel() + ")", FONT_SMALL));
            cell.addElement(h);

            Paragraph pWhy = new Paragraph();
            pWhy.setSpacingBefore(2f);
            pWhy.add(new Chunk("Why It Matters: ", FONT_BODY_BOLD));
            pWhy.add(new Chunk(w.getWhyItMatters(), FONT_BODY));
            cell.addElement(pWhy);

            Paragraph pTyp = new Paragraph();
            pTyp.setSpacingBefore(2f);
            pTyp.add(new Chunk("Typical Industry Provision: ", FONT_BODY_BOLD));
            pTyp.add(new Chunk(w.getTypicalProvision(), FONT_BODY));
            cell.addElement(pTyp);

            card.addCell(cell);
            doc.add(card);
        }
    }

    // -------------------------------------------------------------
    // Section 9: Suggested Questions to Ask
    // -------------------------------------------------------------
    private void addQuestionsToAskSection(com.lowagie.text.Document doc,
                                         List<RiskFinding> risks,
                                         List<MissingClauseWarning> missing) throws DocumentException {
        doc.add(createSectionHeading("9. Suggested Questions to Ask"));

        Set<String> questions = new LinkedHashSet<>();

        for (RiskFinding r : risks) {
            List<String> qs = parseJsonStringList(r.getSuggestedQuestions());
            questions.addAll(qs);
        }

        if (questions.isEmpty()) {
            questions.add("Are there any unwritten side letters, exhibits, or schedules referenced in the agreement?");
            questions.add("Does this contract supersede all prior oral or written agreements between the parties?");
            questions.add("What specific remedies or cure periods apply in the event of an unforeseen operational delay?");
        }

        PdfPTable box = new PdfPTable(1);
        box.setWidthPercentage(100);
        box.setSpacingBefore(4f);
        box.setSpacingAfter(8f);

        PdfPCell cell = new PdfPCell();
        cell.setBorderColor(COLOR_BORDER);
        cell.setBackgroundColor(COLOR_BG_LIGHT);
        cell.setPadding(8f);

        for (String q : questions) {
            Paragraph qPara = new Paragraph();
            qPara.setSpacingBefore(3f);
            qPara.add(new Chunk("? ", font(10f, Font.BOLD, COLOR_ACCENT)));
            qPara.add(new Chunk(q, FONT_BODY));
            cell.addElement(qPara);
        }

        box.addCell(cell);
        doc.add(box);
    }

    // -------------------------------------------------------------
    // Section 10: Legal Disclaimer & Jurisdiction Notice
    // -------------------------------------------------------------
    private void addDisclaimerSection(com.lowagie.text.Document doc) throws DocumentException {
        doc.add(createSectionHeading("10. Legal Notice & Disclaimer"));

        PdfPTable box = new PdfPTable(1);
        box.setWidthPercentage(100);
        box.setSpacingBefore(6f);
        box.setSpacingAfter(10f);

        PdfPCell cell = new PdfPCell();
        cell.setBorderColor(COLOR_PRIMARY);
        cell.setBorderWidth(1.2f);
        cell.setBackgroundColor(COLOR_BG_ALT);
        cell.setPadding(10f);

        Paragraph disTitle = new Paragraph("NOT FORMAL LEGAL COUNSEL — AUTOMATED INFORMATIONAL AID", font(10, Font.BOLD, COLOR_PRIMARY));
        cell.addElement(disTitle);

        Paragraph disBody = new Paragraph(
                "This document analysis report is generated by LexiLegal AI for informational and educational purposes only. " +
                "LexiLegal AI is an automated software tool and is NOT an attorney, law firm, or substitute for qualified legal counsel. " +
                "This report does not establish an attorney-client relationship, nor does it guarantee the legality, enforceability, or validity of any clause under local, state, or federal laws. " +
                "Legal outcomes depend on governing jurisdiction, factual circumstances, and applicable statutory frameworks. " +
                "Before signing, executing, modifying, or relying on any contract terms analyzed in this report, you must consult with a licensed attorney admitted to practice in the relevant jurisdiction.",
                font(8.5f, Font.NORMAL, COLOR_TEXT_MAIN)
        );
        disBody.setSpacingBefore(4f);
        cell.addElement(disBody);

        box.addCell(cell);
        doc.add(box);
    }

    // -------------------------------------------------------------
    // Helper Methods & Formatters
    // -------------------------------------------------------------
    private Paragraph createSectionHeading(String title) {
        Paragraph p = new Paragraph(title, FONT_H1);
        p.setSpacingBefore(12f);
        p.setSpacingAfter(4f);
        p.setKeepTogether(true);
        return p;
    }

    private Paragraph createDivider() {
        Paragraph p = new Paragraph();
        p.setSpacingBefore(4f);
        p.setSpacingAfter(6f);
        PdfPTable line = new PdfPTable(1);
        line.setWidthPercentage(100);
        PdfPCell cell = new PdfPCell();
        cell.setBorder(Rectangle.BOTTOM);
        cell.setBorderColor(COLOR_BORDER);
        cell.setFixedHeight(2f);
        line.addCell(cell);
        p.add(line);
        return p;
    }

    private void addStatCard(PdfPTable table, String label, String value) {
        PdfPCell cell = new PdfPCell();
        cell.setBackgroundColor(COLOR_BG_LIGHT);
        cell.setBorderColor(COLOR_BORDER);
        cell.setPadding(6f);
        cell.addElement(new Paragraph(label, FONT_SMALL));
        cell.addElement(new Paragraph(value, FONT_BODY_BOLD));
        table.addCell(cell);
    }

    private void addTableHeaderCell(PdfPTable table, String text) {
        PdfPCell cell = new PdfPCell(new Phrase(text, FONT_SMALL_BOLD));
        cell.setBackgroundColor(COLOR_BG_ALT);
        cell.setBorderColor(COLOR_BORDER);
        cell.setPadding(5f);
        table.addCell(cell);
    }

    private Paragraph createImportanceBadge(String importance) {
        String imp = importance != null ? importance.toUpperCase() : "MEDIUM";
        Color c = switch (imp) {
            case "HIGH" -> COLOR_RISK_HIGH;
            case "LOW" -> COLOR_RISK_LOW;
            default -> COLOR_RISK_MED;
        };
        return new Paragraph(imp, font(8.5f, Font.BOLD, c));
    }

    private Color getRiskLevelColor(String level) {
        if (level == null) return COLOR_RISK_INFO;
        return switch (level.toUpperCase()) {
            case "HIGH" -> COLOR_RISK_HIGH;
            case "MEDIUM" -> COLOR_RISK_MED;
            case "LOW" -> COLOR_RISK_LOW;
            default -> COLOR_RISK_INFO;
        };
    }

    private Color getRiskLevelBg(String level) {
        if (level == null) return COLOR_RISK_INFO_BG;
        return switch (level.toUpperCase()) {
            case "HIGH" -> COLOR_RISK_HIGH_BG;
            case "MEDIUM" -> COLOR_RISK_MED_BG;
            case "LOW" -> COLOR_RISK_LOW_BG;
            default -> COLOR_RISK_INFO_BG;
        };
    }

    private List<Map<String, Object>> parseJsonList(String json) {
        if (json == null || json.isBlank() || "[]".equals(json.trim())) {
            return Collections.emptyList();
        }
        try {
            return objectMapper.readValue(json, new TypeReference<List<Map<String, Object>>>() {});
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    private List<String> parseJsonStringList(String json) {
        if (json == null || json.isBlank() || "[]".equals(json.trim())) {
            return Collections.emptyList();
        }
        try {
            return objectMapper.readValue(json, new TypeReference<List<String>>() {});
        } catch (Exception e) {
            return Collections.emptyList();
        }
    }

    // Page Event for Running Header and Footer
    private static class HeaderFooterPageEvent extends PdfPageEventHelper {
        @Override
        public void onEndPage(PdfWriter writer, com.lowagie.text.Document document) {
            PdfContentByte cb = writer.getDirectContent();

            // Running header on page > 1
            if (writer.getPageNumber() > 1) {
                ColumnText.showTextAligned(
                        cb, Element.ALIGN_LEFT,
                        new Phrase("LexiLegal AI • Contract Analysis Report", font(8, Font.NORMAL, COLOR_TEXT_MUTED)),
                        document.left(), document.top() + 10, 0
                );
            }

            // Running footer on all pages
            ColumnText.showTextAligned(
                    cb, Element.ALIGN_LEFT,
                    new Phrase("CONFIDENTIAL • INFORMATIONAL ONLY • NOT LEGAL ADVICE", font(7.5f, Font.NORMAL, COLOR_TEXT_MUTED)),
                    document.left(), document.bottom() - 15, 0
            );

            ColumnText.showTextAligned(
                    cb, Element.ALIGN_RIGHT,
                    new Phrase("Page " + writer.getPageNumber(), font(8, Font.NORMAL, COLOR_TEXT_MUTED)),
                    document.right(), document.bottom() - 15, 0
            );
        }
    }
}
