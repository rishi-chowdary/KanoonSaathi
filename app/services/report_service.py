"""ReportLab PDF generator for the 10-section contract analysis report."""

from __future__ import annotations

import io
import logging
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

logger = logging.getLogger("lexilegal.report_service")

# -----------------------------------------------------------------------------
# Color Palette & Semantic Tokens
# -----------------------------------------------------------------------------
COLOR_PRIMARY = colors.HexColor("#0B1B3D")  # Deep Navy
COLOR_SECONDARY = colors.HexColor("#2C5282")  # Slate Blue
COLOR_ACCENT = colors.HexColor("#D69E2E")  # Gold Accent
COLOR_TEXT_MAIN = colors.HexColor("#1A202C")  # Dark Slate
COLOR_TEXT_MUTED = colors.HexColor("#64748B")  # Muted Slate
COLOR_BORDER = colors.HexColor("#E2E8F0")  # Light Border
COLOR_BG_ALT = colors.HexColor("#F8FAFC")  # Subtle Background
COLOR_WHITE = colors.HexColor("#FFFFFF")

# Risk Semantic Colors
COLOR_RISK_HIGH = colors.HexColor("#B91C1C")
COLOR_RISK_HIGH_BG = colors.HexColor("#FEF2F2")
COLOR_RISK_MED = colors.HexColor("#B45309")
COLOR_RISK_MED_BG = colors.HexColor("#FFFBEB")
COLOR_RISK_LOW = colors.HexColor("#15803D")
COLOR_RISK_LOW_BG = colors.HexColor("#F0FDF4")
COLOR_PROVENANCE = colors.HexColor("#0E7490")  # Cyan/Teal for provenance badges

# -----------------------------------------------------------------------------
# TrueType Font Setup (₹, §, curly quotes, bullets)
# -----------------------------------------------------------------------------
_FONT_INITIALIZED = False
_REGULAR_FONT = "Helvetica"
_BOLD_FONT = "Helvetica-Bold"
_ITALIC_FONT = "Helvetica-Oblique"


def init_truetype_fonts() -> tuple[str, str, str]:
    """Register system TrueType fonts supporting Unicode currency symbols and typography."""
    global _FONT_INITIALIZED, _REGULAR_FONT, _BOLD_FONT, _ITALIC_FONT
    if _FONT_INITIALIZED:
        return _REGULAR_FONT, _BOLD_FONT, _ITALIC_FONT

    font_pairs = [
        (
            "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf",
            "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Bold.ttf",
            "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Italic.ttf",
        ),
        (
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
        ),
        (
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        ),
        (
            "/usr/share/fonts/google-noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/google-noto/NotoSans-Bold.ttf",
            "/usr/share/fonts/google-noto/NotoSans-Italic.ttf",
        ),
    ]

    for reg, bold, italic in font_pairs:
        if Path(reg).exists() and Path(bold).exists():
            try:
                pdfmetrics.registerFont(TTFont("LegalSans", reg))
                pdfmetrics.registerFont(TTFont("LegalSans-Bold", bold))
                if Path(italic).exists():
                    pdfmetrics.registerFont(TTFont("LegalSans-Italic", italic))
                    _ITALIC_FONT = "LegalSans-Italic"
                else:
                    _ITALIC_FONT = "LegalSans"
                _REGULAR_FONT = "LegalSans"
                _BOLD_FONT = "LegalSans-Bold"
                _FONT_INITIALIZED = True
                logger.info("Registered TrueType font pair: %s", reg)
                return _REGULAR_FONT, _BOLD_FONT, _ITALIC_FONT
            except Exception as e:  # noqa: BLE001
                logger.warning("Failed to register font %s: %s", reg, e)

    _FONT_INITIALIZED = True
    return _REGULAR_FONT, _BOLD_FONT, _ITALIC_FONT


# -----------------------------------------------------------------------------
# NumberedCanvas for Running Headers & Footers (Page X of Y)
# -----------------------------------------------------------------------------
class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas calculating total page count for running headers and footers."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._saved_page_states: list[dict[str, Any]] = []

    def showPage(self) -> None:
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self) -> None:
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_decorations(self, total_pages: int) -> None:
        self.saveState()
        reg_font, _, _ = init_truetype_fonts()
        self.setFont(reg_font, 8)
        self.setFillColor(COLOR_TEXT_MUTED)

        # Header (Pages > 1)
        if self._pageNumber > 1:
            self.drawString(36, 804, "LexiLegal AI — Contract Analysis Report")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(36, 798, 559, 798)

        # Footer (All pages)
        self.drawString(
            36,
            26,
            "CONFIDENTIAL — Prepared by LexiLegal AI Natural Language Processing",
        )
        page_str = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(559, 26, page_str)
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(36, 36, 559, 36)

        self.restoreState()


# -----------------------------------------------------------------------------
# Report Generation Builder
# -----------------------------------------------------------------------------
def generate_pdf_report(document: Any, analysis: Any) -> bytes:
    """Build a 10-section PDF report for an analyzed contract."""
    reg_font, bold_font, italic_font = init_truetype_fonts()

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46,
    )

    # Custom typography styles
    style_title = ParagraphStyle(
        "ReportTitle",
        fontName=bold_font,
        fontSize=18,
        leading=22,
        textColor=COLOR_PRIMARY,
        spaceAfter=4,
    )
    style_subtitle = ParagraphStyle(
        "ReportSubtitle",
        fontName=reg_font,
        fontSize=9.5,
        leading=13,
        textColor=COLOR_TEXT_MUTED,
        spaceAfter=12,
    )
    style_sec_heading = ParagraphStyle(
        "SectionHeading",
        fontName=bold_font,
        fontSize=12,
        leading=16,
        textColor=COLOR_PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True,
    )
    style_sec_sub = ParagraphStyle(
        "SectionSub",
        fontName=reg_font,
        fontSize=8.5,
        leading=11,
        textColor=COLOR_TEXT_MUTED,
        spaceAfter=8,
        keepWithNext=True,
    )
    style_body = ParagraphStyle(
        "BodyTextCustom",
        fontName=reg_font,
        fontSize=9,
        leading=13,
        textColor=COLOR_TEXT_MAIN,
        spaceAfter=4,
    )
    style_body_bold = ParagraphStyle(
        "BodyBoldCustom",
        fontName=bold_font,
        fontSize=9,
        leading=13,
        textColor=COLOR_TEXT_MAIN,
    )
    style_quote = ParagraphStyle(
        "QuoteCustom",
        fontName=italic_font,
        fontSize=8.5,
        leading=12,
        textColor=COLOR_TEXT_MAIN,
        leftIndent=10,
        rightIndent=10,
    )
    style_badge = ParagraphStyle(
        "BadgeCustom",
        fontName=bold_font,
        fontSize=7.5,
        leading=9,
        textColor=COLOR_PROVENANCE,
    )
    style_small = ParagraphStyle(
        "SmallCustom",
        fontName=reg_font,
        fontSize=8,
        leading=10,
        textColor=COLOR_TEXT_MUTED,
    )

    story: list[Any] = []

    # -------------------------------------------------------------------------
    # Section 1: Cover / Overview
    # -------------------------------------------------------------------------
    badge_p = Paragraph(
        "<b>LEXILEGAL AI</b> &bull; CONTRACT ANALYSIS REPORT",
        style_badge,
    )
    story.append(badge_p)
    story.append(Spacer(1, 4))

    doc_title = document.original_filename or "Legal Contract"
    story.append(Paragraph(doc_title, style_title))

    created_str = (
        document.created_at.strftime("%B %d, %Y at %H:%M UTC")
        if document.created_at
        else "N/A"
    )
    story.append(
        Paragraph(
            f"Extracted and analyzed on {created_str} &bull; Document Format: {document.file_type}",
            style_subtitle,
        )
    )

    # Overview metadata table
    key_info = getattr(analysis, "key_info", None) if analysis else None
    clauses = list(analysis.clauses) if analysis and analysis.clauses else []
    risks = list(analysis.risks) if analysis and analysis.risks else []
    warnings = (
        list(analysis.missing_warnings)
        if analysis and analysis.missing_warnings
        else []
    )

    parties_str = (
        ", ".join([str(p) for p in analysis.parties])
        if analysis and analysis.parties
        else "Not explicitly identified"
    )
    verif_rate = (
        f"{float(analysis.verification_rate or 0.0):.1f}%" if analysis else "0.0%"
    )

    overview_data = [
        [
            Paragraph("<b>Contract Type:</b>", style_body),
            Paragraph(
                (analysis.document_type if analysis else "Agreement") or "Agreement",
                style_body,
            ),
            Paragraph("<b>Quote Verification:</b>", style_body),
            Paragraph(f"<b>{verif_rate}</b> (Extractive)", style_body_bold),
        ],
        [
            Paragraph("<b>Identified Parties:</b>", style_body),
            Paragraph(parties_str, style_body),
            Paragraph("<b>Document Scope:</b>", style_body),
            Paragraph(
                f"{document.page_count} pages &bull; {len(clauses)} clauses", style_body
            ),
        ],
        [
            Paragraph("<b>Risk Findings:</b>", style_body),
            Paragraph(f"{len(risks)} detected issues", style_body),
            Paragraph("<b>Omission Checks:</b>", style_body),
            Paragraph(f"{len(warnings)} potential omissions", style_body),
        ],
    ]

    t_overview = Table(overview_data, colWidths=[105, 175, 105, 138])
    t_overview.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG_ALT),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_overview)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 2: Executive Summary
    # -------------------------------------------------------------------------
    story.append(Paragraph("1. Executive Summary", style_sec_heading))
    story.append(
        Paragraph(
            "Synthesized using extractive SBERT TextRank centrality and clause importance aggregation.",
            style_sec_sub,
        )
    )

    if analysis and analysis.purpose:
        story.append(
            Paragraph(f"<b>Document Purpose:</b> {analysis.purpose}", style_body)
        )
        story.append(Spacer(1, 4))

    summary_text = (
        analysis.summary_short if analysis else ""
    ) or "No summary available."
    summary_box_data = [
        [
            Paragraph(
                f"<b>Key Takeaways:</b> {summary_text}",
                style_body,
            )
        ]
    ]
    t_summary = Table(summary_box_data, colWidths=[523])
    t_summary.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG_ALT),
                ("BOX", (0, 0), (-1, -1), 1, COLOR_SECONDARY),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_summary)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 3: Important Clauses Table
    # -------------------------------------------------------------------------
    story.append(Paragraph("2. Important Contractual Provisions", style_sec_heading))
    story.append(
        Paragraph(
            "Ranked by legal importance score with exact page and character offset tracking.",
            style_sec_sub,
        )
    )

    if clauses:
        clause_rows = [
            [
                Paragraph("<b>Category / Ref</b>", style_body_bold),
                Paragraph("<b>Importance</b>", style_body_bold),
                Paragraph("<b>Page</b>", style_body_bold),
                Paragraph("<b>Verified Source Quote</b>", style_body_bold),
            ]
        ]
        # Include top 8 most important clauses
        imp_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
        sorted_clauses = sorted(
            clauses,
            key=lambda c: imp_order.get(getattr(c, "importance", "LOW"), 0),
            reverse=True,
        )[:8]

        for cl in sorted_clauses:
            cat_name = cl.category or "General"
            sec_ref = f" &bull; {cl.section_reference}" if cl.section_reference else ""
            cat_p = Paragraph(f"<b>{cat_name}</b>{sec_ref}", style_body)

            imp_color = (
                COLOR_RISK_HIGH
                if cl.importance == "HIGH"
                else (COLOR_RISK_MED if cl.importance == "MEDIUM" else COLOR_SECONDARY)
            )
            imp_style = ParagraphStyle(
                "ImpStyle",
                parent=style_body_bold,
                textColor=imp_color,
            )
            imp_p = Paragraph(cl.importance or "LOW", imp_style)
            page_p = Paragraph(f"p. {cl.source_page}", style_body)

            raw_quote = cl.evidence_quote or cl.original_text or ""
            quote_snip = raw_quote[:140] + ("..." if len(raw_quote) > 140 else "")
            quote_p = Paragraph(
                f"&ldquo;{quote_snip}&rdquo;<br/><font color='#0E7490'>[EXTRACTED &bull; Page {cl.source_page}]</font>",
                style_small,
            )

            clause_rows.append([cat_p, imp_p, page_p, quote_p])

        t_clauses = Table(clause_rows, colWidths=[130, 75, 45, 273])
        t_clauses.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_BG_ALT),
                    ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t_clauses)
    else:
        story.append(
            Paragraph("No discrete contractual provisions segmented.", style_body)
        )
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 4: Plain-Language Explanations (3 Modes)
    # -------------------------------------------------------------------------
    story.append(Paragraph("3. Plain-Language Explanations", style_sec_heading))
    story.append(
        Paragraph(
            "Rule-based simplification with Flesch Reading Ease optimization and negation preservation.",
            style_sec_sub,
        )
    )

    top_clauses_for_expl = [
        c
        for c in clauses
        if getattr(c, "simplified_simple", None)
        or getattr(c, "simplified_detailed", None)
        or getattr(c, "simplified_professional", None)
    ][:3]
    if top_clauses_for_expl:
        for idx, cl in enumerate(top_clauses_for_expl, 1):
            expl_box: list[Any] = []
            expl_box.append(
                Paragraph(
                    f"<b>Clause {idx}: {cl.category}</b> (Page {cl.source_page})",
                    style_body_bold,
                )
            )

            orig_snip = (cl.original_text or "")[:120] + (
                "..." if len(cl.original_text or "") > 120 else ""
            )
            expl_box.append(
                Paragraph(f"<i>Original: &ldquo;{orig_snip}&rdquo;</i>", style_quote)
            )

            if cl.simplified_simple:
                expl_box.append(
                    Paragraph(
                        f"<b>Simple English:</b> {cl.simplified_simple}", style_body
                    )
                )
            if cl.simplified_detailed:
                expl_box.append(
                    Paragraph(
                        f"<b>Context & Implications:</b> {cl.simplified_detailed}",
                        style_body,
                    )
                )
            if cl.simplified_professional:
                expl_box.append(
                    Paragraph(
                        f"<b>Structured Breakdown:</b> {cl.simplified_professional}",
                        style_body,
                    )
                )

            t_expl = Table(
                [[expl_box]],
                colWidths=[523],
            )
            t_expl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG_ALT),
                        ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(KeepTogether([t_expl, Spacer(1, 6)]))
    else:
        story.append(
            Paragraph("No simplifications available for this document.", style_body)
        )
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------------------
    # Section 5: Risk Analysis (Color Coded)
    # -------------------------------------------------------------------------
    story.append(Paragraph("4. Contract Risk Assessment", style_sec_heading))
    story.append(
        Paragraph(
            "Pattern-matched against predatory legal terms with verifiable source quotes.",
            style_sec_sub,
        )
    )

    if risks:
        for r in risks[:6]:
            sev = r.level or "MEDIUM"
            border_c = (
                COLOR_RISK_HIGH
                if sev == "HIGH"
                else (COLOR_RISK_MED if sev == "MEDIUM" else COLOR_RISK_LOW)
            )
            bg_c = (
                COLOR_RISK_HIGH_BG
                if sev == "HIGH"
                else (COLOR_RISK_MED_BG if sev == "MEDIUM" else COLOR_RISK_LOW_BG)
            )

            r_title_style = ParagraphStyle(
                "RiskTitleStyle",
                parent=style_body_bold,
                textColor=border_c,
            )

            risk_content = [
                Paragraph(f"[{sev} RISK] {r.title} &bull; {r.category}", r_title_style),
                Paragraph(
                    f"<b>Why it matters:</b> {r.why_it_matters or r.explanation}",
                    style_body,
                ),
            ]
            if r.possible_consequences:
                risk_content.append(
                    Paragraph(
                        f"<b>Consequences:</b> {r.possible_consequences}", style_body
                    )
                )
            if r.evidence_quote:
                quote_s = r.evidence_quote[:130] + (
                    "..." if len(r.evidence_quote) > 130 else ""
                )
                risk_content.append(
                    Paragraph(
                        f"<i>Evidence (p. {r.source_page}): &ldquo;{quote_s}&rdquo;</i>",
                        style_quote,
                    )
                )

            t_risk = Table([[risk_content]], colWidths=[523])
            t_risk.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, -1), bg_c),
                        ("BOX", (0, 0), (-1, -1), 1, border_c),
                        ("LEFTPADDING", (0, 0), (-1, -1), 8),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                        ("TOPPADDING", (0, 0), (-1, -1), 6),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                    ]
                )
            )
            story.append(KeepTogether([t_risk, Spacer(1, 6)]))
    else:
        # Graceful empty state
        story.append(
            Paragraph(
                "No elevated contractual, legal, or financial risks detected in this agreement.",
                style_body,
            )
        )
    story.append(Spacer(1, 6))

    # -------------------------------------------------------------------------
    # Section 6: Financial Terms
    # -------------------------------------------------------------------------
    story.append(Paragraph("5. Financial Terms & Payment Structure", style_sec_heading))
    story.append(
        Paragraph(
            "Extracted financial commitments with currency symbols and deadline schedules.",
            style_sec_sub,
        )
    )

    amount_val = (
        getattr(key_info, "contract_amount", "Not specified") or "Not specified"
    )
    amount_p = getattr(key_info, "contract_amount_page", 1) or 1
    deadlines_val = (
        getattr(key_info, "payment_deadlines", "Not specified") or "Not specified"
    )
    penalties_val = getattr(key_info, "penalties", "Not specified") or "Not specified"

    fin_data = [
        [
            Paragraph("<b>Contract / Payment Amount:</b>", style_body),
            Paragraph(
                f"{amount_val} <font color='#64748B'>(Page {amount_p})</font>",
                style_body,
            ),
        ],
        [
            Paragraph("<b>Payment Deadlines:</b>", style_body),
            Paragraph(deadlines_val, style_body),
        ],
        [
            Paragraph("<b>Penalties & Late Terms:</b>", style_body),
            Paragraph(penalties_val, style_body),
        ],
    ]

    t_fin = Table(fin_data, colWidths=[180, 343])
    t_fin.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG_ALT),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_fin)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 7: Important Dates & Deadlines
    # -------------------------------------------------------------------------
    story.append(Paragraph("6. Critical Dates & Timelines", style_sec_heading))
    story.append(
        Paragraph(
            "Effective dates, expiration milestones, and required notice intervals.",
            style_sec_sub,
        )
    )

    start_date_val = getattr(key_info, "start_date", "Not specified") or "Not specified"
    end_date_val = getattr(key_info, "end_date", "Not specified") or "Not specified"
    renewal_val = getattr(key_info, "renewal_date", "Not specified") or "Not specified"
    notice_val = getattr(key_info, "notice_period", "Not specified") or "Not specified"

    dates_data = [
        [
            Paragraph("<b>Effective / Start Date:</b>", style_body),
            Paragraph(start_date_val, style_body),
            Paragraph("<b>Expiration / End Date:</b>", style_body),
            Paragraph(end_date_val, style_body),
        ],
        [
            Paragraph("<b>Renewal Terms:</b>", style_body),
            Paragraph(renewal_val, style_body),
            Paragraph("<b>Termination Notice:</b>", style_body),
            Paragraph(notice_val, style_body),
        ],
    ]

    t_dates = Table(dates_data, colWidths=[130, 131, 130, 132])
    t_dates.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), COLOR_BG_ALT),
                ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(t_dates)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 8: Missing Provisions (Possible Omissions)
    # -------------------------------------------------------------------------
    story.append(Paragraph("7. Standard Provisions Checklist", style_sec_heading))
    story.append(
        Paragraph(
            "Expected protective covenants for this agreement type flagged under Rule 7 non-definitive guidelines.",
            style_sec_sub,
        )
    )

    if warnings:
        warn_rows = [
            [
                Paragraph("<b>Provision Name</b>", style_body_bold),
                Paragraph("<b>Status</b>", style_body_bold),
                Paragraph("<b>Guidance & Consideration</b>", style_body_bold),
            ]
        ]
        for w in warnings[:5]:
            warn_rows.append(
                [
                    Paragraph(w.clause_name or "Standard Clause", style_body),
                    Paragraph(
                        "<font color='#B45309'><b>Possible omission</b></font>",
                        style_body,
                    ),
                    Paragraph(
                        w.why_it_matters
                        or w.typical_provision
                        or "Consider standard protective covenant.",
                        style_small,
                    ),
                ]
            )

        t_warn = Table(warn_rows, colWidths=[140, 110, 273])
        t_warn.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), COLOR_BG_ALT),
                    ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
                    ("TOPPADDING", (0, 0), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(t_warn)
    else:
        story.append(
            Paragraph(
                "All standard contractual provisions for this agreement type appear to be addressed.",
                style_body,
            )
        )
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 9: Suggested Questions to Ask
    # -------------------------------------------------------------------------
    story.append(
        Paragraph("8. Actionable Questions for Legal Counsel", style_sec_heading)
    )
    story.append(
        Paragraph(
            "Recommended negotiating points and clarifying questions based on detected terms.",
            style_sec_sub,
        )
    )

    sample_questions = [
        "Are the late payment interest fees consistent with local statutory maximums?",
        "Can the termination notice requirement be made strictly bilateral?",
        "Is there an opportunity to place an aggregate dollar cap on indemnification obligations?",
        "Are all carve-outs for publicly available information clearly recognized?",
    ]
    # Augment with risk-specific questions if available
    for r in risks:
        sqs = r.suggested_questions or []
        for q in sqs:
            if q and q not in sample_questions:
                sample_questions.append(q)

    q_data = []
    for q in sample_questions[:4]:
        q_data.append(
            [
                Paragraph("&bull;", style_body_bold),
                Paragraph(q, style_body),
            ]
        )

    t_q = Table(q_data, colWidths=[20, 503])
    t_q.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    story.append(t_q)
    story.append(Spacer(1, 10))

    # -------------------------------------------------------------------------
    # Section 10: Legal Disclaimer & Jurisdiction Notice
    # -------------------------------------------------------------------------
    story.append(
        Paragraph("9. Regulatory Notice & Legal Disclaimer", style_sec_heading)
    )

    disclaimer_text = (
        "<b>LEGAL DISCLAIMER:</b> LexiLegal AI provides automated natural language processing "
        "analysis for document simplification and informational reference only. It does not constitute "
        "formal legal advice, attorney-client privileged communication, or an authoritative legal determination. "
        "Natural language models may not identify every contractual ambiguity or local jurisdiction requirement. "
        "Users are strongly advised to review all legal documents with a qualified legal professional before signing."
    )
    story.append(Paragraph(disclaimer_text, style_small))
    story.append(Spacer(1, 4))

    hash_val = document.file_hash or "N/A"
    story.append(
        Paragraph(
            f"<b>Integrity Verification:</b> SHA-256 Digest: <font name='{reg_font}'>{hash_val}</font>",
            style_small,
        )
    )
    story.append(Spacer(1, 6))

    # Build document
    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()
