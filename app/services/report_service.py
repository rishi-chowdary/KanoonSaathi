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

logger = logging.getLogger("kanoonsaathi.report_service")

COLOR_PRIMARY = colors.HexColor("#0B1B3D")
COLOR_SECONDARY = colors.HexColor("#2C5282")
COLOR_ACCENT = colors.HexColor("#D69E2E")
COLOR_TEXT_MAIN = colors.HexColor("#1A202C")
COLOR_TEXT_MUTED = colors.HexColor("#64748B")
COLOR_BORDER = colors.HexColor("#E2E8F0")
COLOR_BG_ALT = colors.HexColor("#F8FAFC")

COLOR_RISK_HIGH = colors.HexColor("#B91C1C")
COLOR_RISK_HIGH_BG = colors.HexColor("#FEF2F2")
COLOR_RISK_MED = colors.HexColor("#B45309")
COLOR_RISK_MED_BG = colors.HexColor("#FFFBEB")
COLOR_RISK_LOW = colors.HexColor("#15803D")
COLOR_RISK_LOW_BG = colors.HexColor("#F0FDF4")
COLOR_PROVENANCE = colors.HexColor("#0E7490")

_FONT_INITIALIZED = False
_REGULAR_FONT = "Helvetica"
_BOLD_FONT = "Helvetica-Bold"
_ITALIC_FONT = "Helvetica-Oblique"

_FONT_CANDIDATES = [
    (
        "/usr/share/fonts/google-carlito-fonts/Carlito-Regular.ttf",
        "/usr/share/fonts/google-carlito-fonts/Carlito-Bold.ttf",
        "/usr/share/fonts/google-carlito-fonts/Carlito-Italic.ttf",
    ),
    (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
    ),
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


def init_truetype_fonts() -> tuple[str, str, str]:
    """Register a system TrueType font family so ₹, §, and curly quotes render cleanly."""
    global _FONT_INITIALIZED, _REGULAR_FONT, _BOLD_FONT, _ITALIC_FONT
    if _FONT_INITIALIZED:
        return _REGULAR_FONT, _BOLD_FONT, _ITALIC_FONT

    for reg, bold, italic in _FONT_CANDIDATES:
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
                logger.info("registered truetype font: %s", reg)
                return _REGULAR_FONT, _BOLD_FONT, _ITALIC_FONT
            except Exception as exc:  # noqa: BLE001
                logger.warning("could not register font %s: %s", reg, exc)

    _FONT_INITIALIZED = True
    return _REGULAR_FONT, _BOLD_FONT, _ITALIC_FONT


class NumberedCanvas(canvas.Canvas):
    """Two-pass canvas that prints running headers and 'Page X of Y' footers."""

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

        if self._pageNumber > 1:
            self.drawString(36, 804, "KanoonSaathi — Contract Analysis Report")
            self.setStrokeColor(COLOR_BORDER)
            self.setLineWidth(0.5)
            self.line(36, 798, 559, 798)

        self.drawString(
            36,
            26,
            "CONFIDENTIAL — Prepared by KanoonSaathi Natural Language Processing",
        )
        self.drawRightString(559, 26, f"Page {self._pageNumber} of {total_pages}")
        self.setStrokeColor(COLOR_BORDER)
        self.setLineWidth(0.5)
        self.line(36, 36, 559, 36)
        self.restoreState()


def _build_styles(
    reg_font: str, bold_font: str, italic_font: str
) -> dict[str, ParagraphStyle]:
    return {
        "title": ParagraphStyle(
            "ReportTitle",
            fontName=bold_font,
            fontSize=18,
            leading=22,
            textColor=COLOR_PRIMARY,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "ReportSubtitle",
            fontName=reg_font,
            fontSize=9.5,
            leading=13,
            textColor=COLOR_TEXT_MUTED,
            spaceAfter=12,
        ),
        "sec_heading": ParagraphStyle(
            "SectionHeading",
            fontName=bold_font,
            fontSize=12,
            leading=16,
            textColor=COLOR_PRIMARY,
            spaceBefore=14,
            spaceAfter=6,
            keepWithNext=True,
        ),
        "sec_sub": ParagraphStyle(
            "SectionSub",
            fontName=reg_font,
            fontSize=8.5,
            leading=11,
            textColor=COLOR_TEXT_MUTED,
            spaceAfter=8,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "BodyTextCustom",
            fontName=reg_font,
            fontSize=9,
            leading=13,
            textColor=COLOR_TEXT_MAIN,
            spaceAfter=4,
        ),
        "body_bold": ParagraphStyle(
            "BodyBoldCustom",
            fontName=bold_font,
            fontSize=9,
            leading=13,
            textColor=COLOR_TEXT_MAIN,
        ),
        "quote": ParagraphStyle(
            "QuoteCustom",
            fontName=italic_font,
            fontSize=8.5,
            leading=12,
            textColor=COLOR_TEXT_MAIN,
            leftIndent=10,
            rightIndent=10,
        ),
        "badge": ParagraphStyle(
            "BadgeCustom",
            fontName=bold_font,
            fontSize=7.5,
            leading=9,
            textColor=COLOR_PROVENANCE,
        ),
        "small": ParagraphStyle(
            "SmallCustom",
            fontName=reg_font,
            fontSize=8,
            leading=10,
            textColor=COLOR_TEXT_MUTED,
        ),
    }


def _grid_table_style(
    header_only_bg: bool = False, pad_v: int = 5, pad_h: int = 8
) -> TableStyle:
    bg_end = (-1, 0) if header_only_bg else (-1, -1)
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), bg_end, COLOR_BG_ALT),
            ("BOX", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, COLOR_BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), pad_v),
            ("BOTTOMPADDING", (0, 0), (-1, -1), pad_v),
            ("LEFTPADDING", (0, 0), (-1, -1), pad_h),
            ("RIGHTPADDING", (0, 0), (-1, -1), pad_h),
        ]
    )


def _box_table_style(
    bg_color: Any = COLOR_BG_ALT,
    border_color: Any = COLOR_BORDER,
    border_width: float = 0.5,
) -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, -1), bg_color),
            ("BOX", (0, 0), (-1, -1), border_width, border_color),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]
    )


def _add_cover_section(
    story: list[Any],
    styles: dict[str, ParagraphStyle],
    document: Any,
    analysis: Any,
    clauses: list[Any],
    risks: list[Any],
    warnings: list[Any],
) -> None:
    story.append(
        Paragraph(
            "<b>KANOONSAATHI</b> &bull; CONTRACT ANALYSIS REPORT", styles["badge"]
        )
    )
    story.append(Spacer(1, 4))
    story.append(
        Paragraph(document.original_filename or "Legal Contract", styles["title"])
    )

    created_str = (
        document.created_at.strftime("%B %d, %Y at %H:%M UTC")
        if document.created_at
        else "N/A"
    )
    story.append(
        Paragraph(
            f"Extracted and analyzed on {created_str} &bull; Document Format: {document.file_type}",
            styles["subtitle"],
        )
    )

    parties_str = (
        ", ".join(str(p) for p in analysis.parties)
        if analysis and analysis.parties
        else "Not explicitly identified"
    )
    verif_rate = (
        f"{float(analysis.verification_rate or 0.0):.1f}%" if analysis else "0.0%"
    )
    doc_type = (analysis.document_type if analysis else "Agreement") or "Agreement"

    rows = [
        [
            Paragraph("<b>Contract Type:</b>", styles["body"]),
            Paragraph(doc_type, styles["body"]),
            Paragraph("<b>Source Match:</b>", styles["body"]),
            Paragraph(f"<b>{verif_rate}</b> (Extractive)", styles["body_bold"]),
        ],
        [
            Paragraph("<b>Identified Parties:</b>", styles["body"]),
            Paragraph(parties_str, styles["body"]),
            Paragraph("<b>Document Scope:</b>", styles["body"]),
            Paragraph(
                f"{document.page_count} pages &bull; {len(clauses)} clauses",
                styles["body"],
            ),
        ],
        [
            Paragraph("<b>Risk Findings:</b>", styles["body"]),
            Paragraph(f"{len(risks)} detected issues", styles["body"]),
            Paragraph("<b>Omission Checks:</b>", styles["body"]),
            Paragraph(f"{len(warnings)} possible omissions", styles["body"]),
        ],
    ]
    tbl = Table(rows, colWidths=[105, 175, 105, 138])
    tbl.setStyle(_grid_table_style())
    story.extend([tbl, Spacer(1, 10)])


def _add_summary_section(
    story: list[Any], styles: dict[str, ParagraphStyle], analysis: Any
) -> None:
    story.append(Paragraph("1. Executive Summary", styles["sec_heading"]))
    story.append(
        Paragraph(
            "Built from extractive SBERT TextRank sentences and key clause obligations.",
            styles["sec_sub"],
        )
    )
    if analysis and analysis.purpose:
        story.append(
            Paragraph(f"<b>Document Purpose:</b> {analysis.purpose}", styles["body"])
        )
        story.append(Spacer(1, 4))

    summary_text = (
        analysis.summary_short if analysis else ""
    ) or "No summary available."
    tbl = Table(
        [[Paragraph(f"<b>Key Takeaways:</b> {summary_text}", styles["body"])]],
        colWidths=[523],
    )
    tbl.setStyle(_box_table_style(COLOR_BG_ALT, COLOR_SECONDARY, border_width=1))
    story.extend([tbl, Spacer(1, 10)])


def _add_clauses_section(
    story: list[Any], styles: dict[str, ParagraphStyle], clauses: list[Any]
) -> None:
    story.append(
        Paragraph("2. Important Contractual Provisions", styles["sec_heading"])
    )
    story.append(
        Paragraph(
            "Ranked by importance score with page and character offset tracking.",
            styles["sec_sub"],
        )
    )
    if not clauses:
        story.append(
            Paragraph("No discrete contractual provisions segmented.", styles["body"])
        )
        story.append(Spacer(1, 10))
        return

    rows = [
        [
            Paragraph("<b>Category / Ref</b>", styles["body_bold"]),
            Paragraph("<b>Importance</b>", styles["body_bold"]),
            Paragraph("<b>Page</b>", styles["body_bold"]),
            Paragraph("<b>Source Quote</b>", styles["body_bold"]),
        ]
    ]
    imp_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}
    top_clauses = sorted(
        clauses,
        key=lambda c: imp_order.get(getattr(c, "importance", "LOW"), 0),
        reverse=True,
    )[:8]

    for cl in top_clauses:
        sec_ref = f" &bull; {cl.section_reference}" if cl.section_reference else ""
        imp_color = (
            COLOR_RISK_HIGH
            if cl.importance == "HIGH"
            else (COLOR_RISK_MED if cl.importance == "MEDIUM" else COLOR_SECONDARY)
        )
        imp_style = ParagraphStyle(
            "ImpStyle", parent=styles["body_bold"], textColor=imp_color
        )
        raw_quote = cl.evidence_quote or cl.original_text or ""
        quote_snip = raw_quote[:140] + ("..." if len(raw_quote) > 140 else "")
        rows.append(
            [
                Paragraph(
                    f"<b>{cl.category or 'General'}</b>{sec_ref}", styles["body"]
                ),
                Paragraph(cl.importance or "LOW", imp_style),
                Paragraph(f"p. {cl.source_page}", styles["body"]),
                Paragraph(
                    f"&ldquo;{quote_snip}&rdquo;<br/>"
                    f"<font color='#0E7490'>[From the document &bull; Page {cl.source_page}]</font>",
                    styles["small"],
                ),
            ]
        )

    tbl = Table(rows, colWidths=[130, 75, 45, 273])
    tbl.setStyle(_grid_table_style(header_only_bg=True, pad_v=4, pad_h=6))
    story.extend([tbl, Spacer(1, 10)])


def _add_explanations_section(
    story: list[Any], styles: dict[str, ParagraphStyle], clauses: list[Any]
) -> None:
    story.append(Paragraph("3. Plain-Language Explanations", styles["sec_heading"]))
    story.append(
        Paragraph(
            "Rule-based simplifications in three modes (simple, detailed, professional).",
            styles["sec_sub"],
        )
    )
    selected = [
        c
        for c in clauses
        if getattr(c, "simplified_simple", None)
        or getattr(c, "simplified_detailed", None)
        or getattr(c, "simplified_professional", None)
    ][:3]

    if not selected:
        story.append(
            Paragraph("No simplifications available for this document.", styles["body"])
        )
        story.append(Spacer(1, 6))
        return

    for idx, cl in enumerate(selected, 1):
        orig_snip = (cl.original_text or "")[:120] + (
            "..." if len(cl.original_text or "") > 120 else ""
        )
        box_items: list[Any] = [
            Paragraph(
                f"<b>Clause {idx}: {cl.category}</b> (Page {cl.source_page})",
                styles["body_bold"],
            ),
            Paragraph(f"<i>Original: &ldquo;{orig_snip}&rdquo;</i>", styles["quote"]),
        ]
        if cl.simplified_simple:
            box_items.append(
                Paragraph(
                    f"<b>Simple English:</b> {cl.simplified_simple}", styles["body"]
                )
            )
        if cl.simplified_detailed:
            box_items.append(
                Paragraph(
                    f"<b>Context & Implications:</b> {cl.simplified_detailed}",
                    styles["body"],
                )
            )
        if cl.simplified_professional:
            box_items.append(
                Paragraph(
                    f"<b>Structured Breakdown:</b> {cl.simplified_professional}",
                    styles["body"],
                )
            )
        tbl = Table([[box_items]], colWidths=[523])
        tbl.setStyle(_box_table_style())
        story.append(KeepTogether([tbl, Spacer(1, 6)]))
    story.append(Spacer(1, 6))


def _add_risks_section(
    story: list[Any], styles: dict[str, ParagraphStyle], risks: list[Any]
) -> None:
    story.append(Paragraph("4. Contract Risk Assessment", styles["sec_heading"]))
    story.append(
        Paragraph(
            "Rule and similarity matches against risky clause patterns with source quotes.",
            styles["sec_sub"],
        )
    )
    if not risks:
        story.append(
            Paragraph(
                "No elevated contractual, legal, or financial risks detected in this agreement.",
                styles["body"],
            )
        )
        story.append(Spacer(1, 6))
        return

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
        title_style = ParagraphStyle(
            "RiskTitleStyle", parent=styles["body_bold"], textColor=border_c
        )
        items: list[Any] = [
            Paragraph(f"[{sev} RISK] {r.title} &bull; {r.category}", title_style),
            Paragraph(
                f"<b>Why it matters:</b> {r.why_it_matters or r.explanation}",
                styles["body"],
            ),
        ]
        if r.possible_consequences:
            items.append(
                Paragraph(
                    f"<b>Consequences:</b> {r.possible_consequences}", styles["body"]
                )
            )
        if r.evidence_quote:
            quote_s = r.evidence_quote[:130] + (
                "..." if len(r.evidence_quote) > 130 else ""
            )
            items.append(
                Paragraph(
                    f"<i>Evidence (p. {r.source_page}): &ldquo;{quote_s}&rdquo;</i>",
                    styles["quote"],
                )
            )
        tbl = Table([[items]], colWidths=[523])
        tbl.setStyle(_box_table_style(bg_c, border_c, border_width=1))
        story.append(KeepTogether([tbl, Spacer(1, 6)]))
    story.append(Spacer(1, 6))


def _add_financials_and_dates(
    story: list[Any], styles: dict[str, ParagraphStyle], key_info: Any
) -> None:
    story.append(
        Paragraph("5. Financial Terms & Payment Structure", styles["sec_heading"])
    )
    story.append(
        Paragraph(
            "Extracted financial amounts, due dates, and late-payment charges.",
            styles["sec_sub"],
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

    fin_tbl = Table(
        [
            [
                Paragraph("<b>Contract / Payment Amount:</b>", styles["body"]),
                Paragraph(
                    f"{amount_val} <font color='#64748B'>(Page {amount_p})</font>",
                    styles["body"],
                ),
            ],
            [
                Paragraph("<b>Payment Deadlines:</b>", styles["body"]),
                Paragraph(deadlines_val, styles["body"]),
            ],
            [
                Paragraph("<b>Penalties & Late Terms:</b>", styles["body"]),
                Paragraph(penalties_val, styles["body"]),
            ],
        ],
        colWidths=[180, 343],
    )
    fin_tbl.setStyle(_grid_table_style())
    story.extend([fin_tbl, Spacer(1, 10)])

    story.append(Paragraph("6. Critical Dates & Timelines", styles["sec_heading"]))
    story.append(
        Paragraph(
            "Effective dates, expiration dates, renewal terms, and notice periods.",
            styles["sec_sub"],
        )
    )
    start_val = getattr(key_info, "start_date", "Not specified") or "Not specified"
    end_val = getattr(key_info, "end_date", "Not specified") or "Not specified"
    renewal_val = getattr(key_info, "renewal_date", "Not specified") or "Not specified"
    notice_val = getattr(key_info, "notice_period", "Not specified") or "Not specified"

    dates_tbl = Table(
        [
            [
                Paragraph("<b>Effective / Start Date:</b>", styles["body"]),
                Paragraph(start_val, styles["body"]),
                Paragraph("<b>Expiration / End Date:</b>", styles["body"]),
                Paragraph(end_val, styles["body"]),
            ],
            [
                Paragraph("<b>Renewal Terms:</b>", styles["body"]),
                Paragraph(renewal_val, styles["body"]),
                Paragraph("<b>Termination Notice:</b>", styles["body"]),
                Paragraph(notice_val, styles["body"]),
            ],
        ],
        colWidths=[130, 131, 130, 132],
    )
    dates_tbl.setStyle(_grid_table_style())
    story.extend([dates_tbl, Spacer(1, 10)])


def _add_missing_and_questions(
    story: list[Any],
    styles: dict[str, ParagraphStyle],
    warnings: list[Any],
    risks: list[Any],
) -> None:
    story.append(Paragraph("7. Standard Provisions Checklist", styles["sec_heading"]))
    story.append(
        Paragraph(
            "Expected provisions for this contract type, labeled as possible omissions.",
            styles["sec_sub"],
        )
    )
    if warnings:
        rows = [
            [
                Paragraph("<b>Provision Name</b>", styles["body_bold"]),
                Paragraph("<b>Status</b>", styles["body_bold"]),
                Paragraph("<b>Guidance & Consideration</b>", styles["body_bold"]),
            ]
        ]
        for w in warnings[:5]:
            rows.append(
                [
                    Paragraph(w.clause_name or "Standard Clause", styles["body"]),
                    Paragraph(
                        "<font color='#B45309'><b>Possible omission</b></font>",
                        styles["body"],
                    ),
                    Paragraph(
                        w.why_it_matters
                        or w.typical_provision
                        or "Consider standard protective covenant.",
                        styles["small"],
                    ),
                ]
            )
        tbl = Table(rows, colWidths=[140, 110, 273])
        tbl.setStyle(_grid_table_style(header_only_bg=True, pad_v=4, pad_h=6))
        story.append(tbl)
    else:
        story.append(
            Paragraph(
                "All standard contractual provisions for this agreement type appear to be addressed.",
                styles["body"],
            )
        )
    story.append(Spacer(1, 10))

    story.append(
        Paragraph("8. Actionable Questions for Legal Counsel", styles["sec_heading"])
    )
    story.append(
        Paragraph(
            "Suggested clarifying questions based on detected clauses and risks.",
            styles["sec_sub"],
        )
    )
    questions = [
        "Are the late payment interest fees consistent with local statutory maximums?",
        "Can the termination notice requirement be made bilateral?",
        "Is there an opportunity to place an aggregate dollar cap on indemnification?",
        "Are carve-outs for publicly available information clearly stated?",
    ]
    for r in risks:
        for q in r.suggested_questions or []:
            if q and q not in questions:
                questions.append(q)

    q_tbl = Table(
        [
            [Paragraph("&bull;", styles["body_bold"]), Paragraph(q, styles["body"])]
            for q in questions[:4]
        ],
        colWidths=[20, 503],
    )
    q_tbl.setStyle(
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
    story.extend([q_tbl, Spacer(1, 10)])


def _add_disclaimer_section(
    story: list[Any], styles: dict[str, ParagraphStyle], document: Any, reg_font: str
) -> None:
    story.append(
        Paragraph("9. Regulatory Notice & Legal Disclaimer", styles["sec_heading"])
    )
    disclaimer_text = (
        "<b>LEGAL DISCLAIMER:</b> KanoonSaathi provides automated natural language processing "
        "analysis for document simplification and informational reference only. It does not constitute "
        "legal advice or a legal determination. Automated tools may miss ambiguity or local statutory "
        "requirements. Review important documents with a qualified legal professional before signing."
    )
    story.append(Paragraph(disclaimer_text, styles["small"]))
    story.append(Spacer(1, 4))
    hash_val = document.file_hash or "N/A"
    story.append(
        Paragraph(
            f"<b>File Digest (SHA-256):</b> <font name='{reg_font}'>{hash_val}</font>",
            styles["small"],
        )
    )
    story.append(Spacer(1, 6))


def generate_pdf_report(document: Any, analysis: Any) -> bytes:
    """Build a 10-section PDF report for an analyzed contract."""
    reg_font, bold_font, italic_font = init_truetype_fonts()
    styles = _build_styles(reg_font, bold_font, italic_font)

    key_info = getattr(analysis, "key_info", None) if analysis else None
    clauses = list(analysis.clauses) if analysis and analysis.clauses else []
    risks = list(analysis.risks) if analysis and analysis.risks else []
    warnings = (
        list(analysis.missing_warnings)
        if analysis and analysis.missing_warnings
        else []
    )

    story: list[Any] = []
    _add_cover_section(story, styles, document, analysis, clauses, risks, warnings)
    _add_summary_section(story, styles, analysis)
    _add_clauses_section(story, styles, clauses)
    _add_explanations_section(story, styles, clauses)
    _add_risks_section(story, styles, risks)
    _add_financials_and_dates(story, styles, key_info)
    _add_missing_and_questions(story, styles, warnings, risks)
    _add_disclaimer_section(story, styles, document, reg_font)

    buf = io.BytesIO()
    pdf_doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=46,
        bottomMargin=46,
    )
    pdf_doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()
