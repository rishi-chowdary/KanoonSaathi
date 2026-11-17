#!/usr/bin/env python3
"""Generate Indian legal sample contracts and Indian statute PDFs (BNS, IPC, Constitution)."""

from __future__ import annotations

from pathlib import Path

from docx import Document as DocxDocument
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples" / "contracts"

FONT_CANDIDATES = [
    "/usr/share/fonts/google-carlito-fonts/Carlito-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]
BOLD_CANDIDATES = [
    "/usr/share/fonts/google-carlito-fonts/Carlito-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/liberation-sans-fonts/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def _register_fonts() -> tuple[str, str]:
    reg = next((p for p in FONT_CANDIDATES if Path(p).exists()), None)
    bold = next((p for p in BOLD_CANDIDATES if Path(p).exists()), None)
    if reg:
        pdfmetrics.registerFont(TTFont("IndiaSans", reg))
        if bold:
            pdfmetrics.registerFont(TTFont("IndiaSans-Bold", bold))
            return "IndiaSans", "IndiaSans-Bold"
        return "IndiaSans", "IndiaSans"
    return "Helvetica", "Helvetica-Bold"


def _write_pdf(
    filename: str, title: str, pages_sections: list[list[tuple[str, str]]]
) -> None:
    font_reg, font_bold = _register_fonts()
    out_path = SAMPLES_DIR / filename
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=0.8 * inch,
        rightMargin=0.8 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName=font_bold,
        fontSize=14,
        leading=18,
        spaceAfter=10,
    )
    head_style = ParagraphStyle(
        "SecHead",
        parent=styles["Heading2"],
        fontName=font_bold,
        fontSize=11,
        leading=14,
        spaceBefore=8,
        spaceAfter=4,
    )
    body_style = ParagraphStyle(
        "SecBody",
        parent=styles["Normal"],
        fontName=font_reg,
        fontSize=10,
        leading=14,
        spaceAfter=8,
    )

    story = [Paragraph(title, title_style), Spacer(1, 4)]
    for page_idx, items in enumerate(pages_sections):
        if page_idx > 0:
            story.append(PageBreak())
        for heading, body in items:
            if heading:
                story.append(Paragraph(heading, head_style))
            story.append(Paragraph(body, body_style))

    doc.build(story)
    print(f"Generated {out_path}")


def generate_clean_nda() -> None:
    pages = [
        [
            (
                "",
                (
                    "This Mutual Non-Disclosure Agreement (the 'Agreement') is entered into as of January 15, 2026, "
                    "between Nakshatra Tech Solutions Private Limited, a company incorporated in Bengaluru, Karnataka "
                    "('Disclosing Party'), and Deccan Cloud Systems Private Limited, a company incorporated in Hyderabad, "
                    "Telangana ('Receiving Party'), governed by the Indian Contract Act, 1872."
                ),
            ),
            (
                "Section 1. Definitions",
                (
                    '"Confidential Information" includes all technical, business, and financial information disclosed by '
                    "Disclosing Party to Receiving Party, whether in written, electronic, or oral form, relating to "
                    "software architecture, client lists, pricing, and product roadmaps."
                ),
            ),
            (
                "Section 2. Non-Disclosure Obligations",
                (
                    "Receiving Party shall hold and maintain the Confidential Information in strictest confidence for the "
                    "sole and exclusive benefit of Disclosing Party. Receiving Party shall carefully restrict access to "
                    "Confidential Information to employees, contractors, and third parties as is reasonably required and "
                    "shall not, without prior written approval of Disclosing Party, use or disclose such information."
                ),
            ),
        ],
        [
            (
                "Section 3. Term and Termination",
                (
                    "This Agreement shall remain in effect for a term of three (3) years from the Effective Date. "
                    "Either party may terminate discussions upon thirty (30) days prior written notice to the other party."
                ),
            ),
            (
                "Section 4. Governing Law and Jurisdiction",
                (
                    "This Agreement shall be governed by and construed in accordance with the laws of India, "
                    "including the Indian Contract Act, 1872. The courts situated at Bengaluru, Karnataka shall have "
                    "exclusive jurisdiction over any dispute arising out of this Agreement."
                ),
            ),
        ],
    ]
    _write_pdf("clean_nda.pdf", "MUTUAL NON-DISCLOSURE AGREEMENT", pages)


def generate_rental_agreement() -> None:
    pages = [
        [
            (
                "",
                (
                    "This Residential Lease and Leave and License Agreement ('Lease Agreement') is made on August 1, 2026, "
                    "at Bengaluru, Karnataka, between Rajeshwar Rao ('Landlord') and Ananya Sharma ('Tenant') for the "
                    "residential apartment located at Indiranagar, Bengaluru, Karnataka 560038."
                ),
            ),
            (
                "Section 1. Premises and Term",
                (
                    "Landlord hereby leases the residential premises at Indiranagar, Bengaluru to Tenant for residential "
                    "occupation. This lease shall commence on August 1, 2026, and continue for a fixed term of twelve (12) "
                    "months, expiring on July 31, 2027."
                ),
            ),
            (
                "Section 2. Monthly Rent and Payment Terms",
                (
                    "Tenant agrees to pay Landlord a monthly rent of ₹28,000.00, payable in advance on or before the "
                    "first (1st) day of each calendar month via UPI or NEFT bank transfer. Payments received more than "
                    "five (5) days after the due date shall incur a late fee of ₹1,500.00."
                ),
            ),
            (
                "Section 3. Security Deposit",
                (
                    "Upon execution of this agreement, Tenant shall deposit with Landlord the sum of ₹1,50,000.00 as a "
                    "security deposit. Landlord may deduct therefrom unpaid rent, utility dues, or repair costs beyond "
                    "normal wear and tear at the end of the tenancy."
                ),
            ),
            (
                "Section 4. Use of Premises and Assignment",
                (
                    "The premises shall be used strictly for private residential purposes. Tenant shall not assign this "
                    "lease, sublet the premises, or permit any commercial sub-tenancy without the prior written consent "
                    "of Landlord."
                ),
            ),
        ],
        [
            (
                "Section 5. Maintenance and Alterations",
                (
                    "Landlord shall maintain electrical, plumbing, water supply, and structural fixtures in habitable "
                    "condition. Tenant shall keep the interior clean and shall not make structural alterations without "
                    "prior written permission."
                ),
            ),
            (
                "Section 6. Termination and Default",
                (
                    "If Tenant fails to pay rent or breaches any material term and fails to cure such default within "
                    "fourteen (14) days after receiving written notice, Landlord may terminate this lease and commence "
                    "eviction proceedings in accordance with applicable Karnataka tenancy law."
                ),
            ),
            (
                "Section 7. Governing Law",
                (
                    "This Lease Agreement shall be governed by and construed in accordance with the laws of the State "
                    "of Karnataka and the Transfer of Property Act, 1882, subject to the exclusive jurisdiction of the "
                    "courts in Bengaluru, Karnataka."
                ),
            ),
        ],
    ]
    _write_pdf(
        "rental_agreement.pdf",
        "RESIDENTIAL LEASE AGREEMENT (BENGALURU, INDIA)",
        pages,
    )


def generate_employment_agreement() -> None:
    pages = [
        [
            (
                "",
                (
                    "This Executive Employment Agreement is entered into effective March 1, 2026, at Hyderabad, Telangana, "
                    "by and between Vayu Analytics Private Limited ('Company') and Vikramaditya Reddy ('Employee')."
                ),
            ),
            (
                "Section 1. Position and Scope of Duties",
                (
                    "Company hereby agrees to employ Employee as Chief Technology Officer at its Hyderabad office. "
                    "Employee shall report to the Board of Directors and devote full working time and professional effort "
                    "to the engineering operations of Company."
                ),
            ),
            (
                "Section 2. Base Compensation and Benefits",
                (
                    "Company shall pay Employee an annual base salary of ₹18,00,000.00, payable in monthly installments "
                    "after statutory deductions including Provident Fund (EPF) and TDS under the Income Tax Act, 1961."
                ),
            ),
            (
                "Section 3. Confidentiality and Trade Secrets",
                (
                    "Employee acknowledges access to proprietary algorithms, source code, and customer data, and agrees "
                    "to hold all such confidential information in strict secrecy during and after employment."
                ),
            ),
            (
                "Section 4. Non-Compete and Non-Solicitation",
                (
                    "For a period of twelve (12) months following termination of employment, Employee shall not directly "
                    "or indirectly engage in or assist any business that directly competes with Company in India or solicit "
                    "Company's clients or employees."
                ),
            ),
        ],
        [
            (
                "Section 5. Intellectual Property Assignment",
                (
                    "Employee hereby irrevocably assigns to Company all right, title, and interest in and to any and all "
                    "inventions, software, patents, and copyrightable works conceived or developed during employment in "
                    "accordance with the Copyright Act, 1957."
                ),
            ),
            (
                "Section 6. Termination Provisions",
                (
                    "Either party may terminate Employee employment at any time without cause upon thirty (30) days prior "
                    "written notice or salary in lieu of notice. Company may terminate immediately for proven misconduct."
                ),
            ),
            (
                "Section 7. Governing Law and Dispute Resolution",
                (
                    "This Agreement shall be governed by the laws of India, including the Indian Contract Act, 1872. "
                    "Any dispute shall be resolved by arbitration under the Arbitration and Conciliation Act, 1996, "
                    "with the seat of arbitration at Hyderabad, Telangana."
                ),
            ),
        ],
    ]
    _write_pdf(
        "employment_agreement.pdf",
        "EXECUTIVE EMPLOYMENT AGREEMENT (HYDERABAD, INDIA)",
        pages,
    )


def generate_one_sided_agreement() -> None:
    pages = [
        [
            (
                "",
                (
                    "This Master Services Agreement ('Agreement') is executed on November 1, 2026, at Mumbai, Maharashtra, "
                    "between Apex Enterprise Systems Private Limited ('Vendor') and Surya Retail Ventures Limited ('Customer')."
                ),
            ),
            (
                "Section 1. Term and Automatic Renewal",
                (
                    "This Agreement commences on November 1, 2026, for an initial period of one (1) year and shall "
                    "automatically renew for successive terms of three (3) years each unless Customer delivers written "
                    "notice of non-renewal at least one hundred eighty (180) days prior to expiration exclusively via "
                    "certified mail to Vendor's Mumbai headquarters."
                ),
            ),
            (
                "Section 2. Fees, Invoicing, and Compounding Late Charges",
                (
                    "All invoices are due immediately upon receipt. If Customer fails to remit payment within three (3) "
                    "calendar days of the invoice date, late interest shall accrue at 2.5% per month, compounded daily on "
                    "the outstanding balance, alongside a mandatory ₹50,000.00 administrative fee per delinquent notice."
                ),
            ),
            (
                "Section 3. Uncapped Indemnification",
                (
                    "Customer shall indemnify, defend, and hold harmless Vendor, its directors, and affiliates from and "
                    "against any and all claims, liabilities, damages, penalties, and attorney fees without any limitation "
                    "or financial cap arising from Customer's use of the services."
                ),
            ),
        ],
        [
            (
                "Section 4. Disproportionate Limitation of Liability",
                (
                    "Vendor disclaims all warranties of merchantability, fitness, or uptime. In no event shall Vendor's "
                    "total aggregate liability under this Agreement exceed the sum of one thousand rupees (₹1,000.00)."
                ),
            ),
            (
                "Section 5. Unilateral Modification of Terms and Fees",
                (
                    "Vendor reserves the right to modify the service fees, service scope, and these terms at any time in "
                    "its sole discretion without prior notice and without requiring Customer's consent."
                ),
            ),
            (
                "Section 6. Unilateral Termination and Fee Acceleration",
                (
                    "Vendor may terminate this Agreement immediately at will without cause or notice. Customer shall have "
                    "no right to terminate for convenience; upon early termination by Customer, all future fees for the "
                    "remainder of the term shall immediately become due and payable as liquidated damages."
                ),
            ),
            (
                "Section 7. Governing Law and Venue",
                (
                    "This Agreement is governed by the laws of India, and Customer submits irrevocably to the exclusive "
                    "jurisdiction of the courts in Mumbai, Maharashtra."
                ),
            ),
        ],
    ]
    _write_pdf(
        "one_sided_agreement.pdf",
        "MASTER SERVICES AGREEMENT (MUMBAI, INDIA)",
        pages,
    )


def generate_service_agreement_docx() -> None:
    doc = DocxDocument()
    doc.add_heading("MASTER SERVICES AGREEMENT (PUNE, INDIA)", level=1)
    doc.add_paragraph(
        "This Master Services Agreement is entered into on April 10, 2026, at Pune, Maharashtra, "
        "between Sahyadri Digital Labs Private Limited ('Service Provider') and Kaveri Logistics Limited ('Client')."
    )
    sections = [
        (
            "Section 1. Scope of Services",
            (
                "Service Provider shall design, develop, and maintain cloud analytics modules for Client's supply chain "
                "operations in India as detailed in mutually signed Statements of Work."
            ),
        ),
        (
            "Section 2. Professional Fees and GST",
            (
                "Client shall pay a total fee of ₹4,50,000.00 plus applicable GST within thirty (30) days of receiving "
                "a valid tax invoice from Service Provider."
            ),
        ),
        (
            "Section 3. Confidentiality and Data Protection",
            (
                "Both parties shall protect each other's confidential data and comply with the Digital Personal Data "
                "Protection Act, 2023 when processing personal records."
            ),
        ),
        (
            "Section 4. Governing Law and Arbitration",
            (
                "This Agreement is governed by the laws of India. Disputes shall be referred to a sole arbitrator under "
                "the Arbitration and Conciliation Act, 1996 at Pune, Maharashtra."
            ),
        ),
    ]
    for title, body in sections:
        doc.add_heading(title, level=2)
        doc.add_paragraph(body)

    out_path = SAMPLES_DIR / "service_agreement.docx"
    doc.save(str(out_path))
    print(f"Generated {out_path}")


def generate_promissory_note_txt() -> None:
    text = """DEMAND PROMISSORY NOTE (NEGOTIABLE INSTRUMENTS ACT, 1881)

Place: Chennai, Tamil Nadu
Date: May 1, 2026
Principal Amount: ₹5,00,000.00 (Rupees Five Lakhs Only)

Section 1. Promise to Pay
On demand, I, Karthik Subramanian, residing at Adyar, Chennai, Tamil Nadu ('Borrower'), unconditionally promise to pay to Meenakshi Sundaram ('Lender'), or order, the principal sum of ₹5,00,000.00 together with simple interest at the rate of 9% per annum from the date of execution until full repayment, with a final maturity date of May 1, 2027.

Section 2. Prepayment
Borrower may prepay the principal amount in whole or in part at any time without any prepayment penalty upon fifteen (15) days prior written notice.

Section 3. Default and Governing Law
If payment is not made within fifteen (15) days of written demand, an additional 2% per annum late charge shall apply. This Promissory Note is governed by the Negotiable Instruments Act, 1881 and subject to the courts in Chennai, Tamil Nadu.
"""
    out_path = SAMPLES_DIR / "promissory_note.txt"
    out_path.write_text(text.strip() + "\n", encoding="utf-8")
    print(f"Generated {out_path}")


def generate_bns_pdf() -> None:
    pages = [
        [
            (
                "",
                "THE BHARATIYA NYAYA SANHITA, 2023 (No. 45 of 2023) — Selected Statutory Sections for Plain-Language Review.",
            ),
            (
                "Section 103. Punishment for murder",
                (
                    "(1) Whoever commits murder shall be punished with death or imprisonment for life, and shall also be "
                    "liable to fine. (2) When a group of five or more persons acting in concert commits murder on the ground "
                    "of race, caste or community, sex, place of birth, language, personal belief or any other similar ground "
                    "each member of such group shall be punished with death or with imprisonment for life, and shall also be "
                    "liable to fine."
                ),
            ),
            (
                "Section 105. Punishment for culpable homicide not amounting to murder",
                (
                    "Whoever commits culpable homicide not amounting to murder, shall be punished with imprisonment for life, "
                    "or imprisonment of either description for a term which shall not be less than five years but which may "
                    "extend to ten years, and shall also be liable to fine, if the act by which the death is caused is done "
                    "with the intention of causing death, or of causing such bodily injury as is likely to cause death."
                ),
            ),
            (
                "Section 115. Voluntarily causing hurt",
                (
                    "(2) Whoever, except in the case provided for by sub-section (1) of section 122, voluntarily causes hurt, "
                    "shall be punished with imprisonment of either description for a term which may extend to one year, or "
                    "with fine which may extend to ten thousand rupees, or with both."
                ),
            ),
            (
                "Section 152. Act endangering sovereignty, unity and integrity of India",
                (
                    "Whoever, purposely or knowingly, by words, either spoken or written, or by signs, or by visible "
                    "representation, or by electronic communication, excites or attempts to excite secession or armed "
                    "rebellion or subversive activities shall be punished with imprisonment for life or with imprisonment "
                    "which may extend to seven years, and shall also be liable to fine. Explanation.—Comments expressing "
                    "disapprobation of the measures of the Government with a view to obtain their alteration by lawful means "
                    "do not constitute an offence under this section."
                ),
            ),
        ],
        [
            (
                "Section 303. Theft",
                (
                    "(1) Whoever, intending to take dishonestly any movable property out of the possession of any person "
                    "without that person's consent, moves that property in order to such taking, is said to commit theft. "
                    "(2) Whoever commits theft shall be punished with imprisonment of either description for a term which "
                    "may extend to three years, or with fine, or with both: Provided that in cases of theft where the value "
                    "of the stolen property is less than five thousand rupees, and a person is convicted for the first time, "
                    "he shall upon return of the value of property or restoration of the stolen property, be punished with "
                    "community service."
                ),
            ),
            (
                "Section 316. Criminal breach of trust",
                (
                    "(1) Whoever, being in any manner entrusted with property, or with any dominion over property, "
                    "dishonestly misappropriates or converts to his own use that property in violation of any direction of "
                    "law or legal contract commits criminal breach of trust. (2) Whoever commits criminal breach of trust "
                    "shall be punished with imprisonment of either description for a term which may extend to five years, "
                    "or with fine, or with both."
                ),
            ),
            (
                "Section 318. Cheating",
                (
                    "(1) Whoever, by deceiving any person, fraudulently or dishonestly induces the person so deceived to "
                    "deliver any property to any person is said to cheat. (4) Whoever cheats and thereby dishonestly induces "
                    "the person deceived to deliver any property to any person, or to make, alter or destroy the whole or "
                    "any part of a valuable security, shall be punished with imprisonment of either description for a term "
                    "which may extend to seven years, and shall also be liable to fine."
                ),
            ),
            (
                "Section 351. Criminal intimidation",
                (
                    "(1) Whoever threatens another by any means, with any injury to his person, reputation or property, with "
                    "intent to cause alarm to that person, commits criminal intimidation. (2) Whoever commits criminal "
                    "intimidation shall be punished with imprisonment of either description for a term which may extend to "
                    "two years, or with fine, or with both."
                ),
            ),
            (
                "Section 356. Defamation",
                (
                    "(1) Whoever, by words either spoken or intended to be read, or by signs or by visible representations, "
                    "makes or publishes any imputation concerning any person intending to harm the reputation of such person "
                    "is said to defame that person. (2) Whoever defames another shall be punished with simple imprisonment "
                    "for a term which may extend to two years, or with fine, or with both, or with community service."
                ),
            ),
        ],
    ]
    _write_pdf(
        "bns_selected_sections.pdf",
        "BHARATIYA NYAYA SANHITA (BNS), 2023 — SELECTED SECTIONS",
        pages,
    )


def generate_ipc_pdf() -> None:
    pages = [
        [
            (
                "",
                "THE INDIAN PENAL CODE, 1860 (Act No. 45 of 1860) — Historical Reference Sections (Replaced by BNS 2023).",
            ),
            (
                "Section 302. Punishment for murder",
                (
                    "Whoever commits murder shall be punished with death, or imprisonment for life, and shall also be "
                    "liable to fine."
                ),
            ),
            (
                "Section 304. Punishment for culpable homicide not amounting to murder",
                (
                    "Whoever commits culpable homicide not amounting to murder shall be punished with imprisonment for life, "
                    "or imprisonment of either description for a term which may extend to ten years, and shall also be "
                    "liable to fine."
                ),
            ),
            (
                "Section 323. Punishment for voluntarily causing hurt",
                (
                    "Whoever, except in the case provided for by section 334, voluntarily causes hurt, shall be punished "
                    "with imprisonment of either description for a term which may extend to one year, or with fine which "
                    "may extend to one thousand rupees, or with both."
                ),
            ),
            (
                "Section 379. Punishment for theft",
                (
                    "Whoever commits theft shall be punished with imprisonment of either description for a term which may "
                    "extend to three years, or with fine, or with both."
                ),
            ),
        ],
        [
            (
                "Section 406. Punishment for criminal breach of trust",
                (
                    "Whoever commits criminal breach of trust shall be punished with imprisonment of either description for "
                    "a term which may extend to three years, or with fine, or with both."
                ),
            ),
            (
                "Section 420. Cheating and dishonestly inducing delivery of property",
                (
                    "Whoever cheats and thereby dishonestly induces the person deceived to deliver any property to any "
                    "person, or to make, alter or destroy the whole or any part of a valuable security, shall be punished "
                    "with imprisonment of either description for a term which may extend to seven years, and shall also be "
                    "liable to fine."
                ),
            ),
            (
                "Section 500. Punishment for defamation",
                (
                    "Whoever defames another shall be punished with simple imprisonment for a term which may extend to two "
                    "years, or with fine, or with both."
                ),
            ),
            (
                "Section 506. Punishment for criminal intimidation",
                (
                    "Whoever commits the offence of criminal intimidation shall be punished with imprisonment of either "
                    "description for a term which may extend to two years, or with fine, or with both; and if the threat be "
                    "to cause death or grievous hurt, with imprisonment for a term which may extend to seven years."
                ),
            ),
        ],
    ]
    _write_pdf(
        "ipc_selected_sections.pdf",
        "INDIAN PENAL CODE (IPC), 1860 — SELECTED SECTIONS",
        pages,
    )


def generate_constitution_pdf() -> None:
    pages = [
        [
            (
                "",
                "THE CONSTITUTION OF INDIA — PART III: FUNDAMENTAL RIGHTS (Selected Constitutional Articles).",
            ),
            (
                "Article 14. Equality before law",
                (
                    "The State shall not deny to any person equality before the law or the equal protection of the laws "
                    "within the territory of India."
                ),
            ),
            (
                "Article 15. Prohibition of discrimination on grounds of religion, race, caste, sex or place of birth",
                (
                    "(1) The State shall not discriminate against any citizen on grounds only of religion, race, caste, sex, "
                    "place of birth or any of them. (3) Nothing in this article shall prevent the State from making any "
                    "special provision for women and children."
                ),
            ),
            (
                "Article 19. Protection of certain rights regarding freedom of speech, etc.",
                (
                    "(1) All citizens shall have the right (a) to freedom of speech and expression; (b) to assemble "
                    "peaceably and without arms; (c) to form associations or unions; (d) to move freely throughout the "
                    "territory of India; (e) to reside and settle in any part of the territory of India; and (g) to practise "
                    "any profession, or to carry on any occupation, trade or business. (2) Nothing in sub-clause (a) of "
                    "clause (1) shall affect the operation of any existing law, or prevent the State from making any law, in "
                    "so far as such law imposes reasonable restrictions on the exercise of the right conferred by the said "
                    "sub-clause in the interests of the sovereignty and integrity of India, the security of the State, "
                    "public order, decency or morality or in relation to contempt of court, defamation or incitement to an offence."
                ),
            ),
            (
                "Article 20. Protection in respect of conviction for offences",
                (
                    "(1) No person shall be convicted of any offence except for violation of a law in force at the time of "
                    "the commission of the act charged as an offence. (2) No person shall be prosecuted and punished for the "
                    "same offence more than once. (3) No person accused of any offence shall be compelled to be a witness "
                    "against himself."
                ),
            ),
        ],
        [
            (
                "Article 21. Protection of life and personal liberty",
                (
                    "No person shall be deprived of his life or personal liberty except according to procedure established "
                    "by law."
                ),
            ),
            (
                "Article 21A. Right to education",
                (
                    "The State shall provide free and compulsory education to all children of the age of six to fourteen "
                    "years in such manner as the State may, by law, determine."
                ),
            ),
            (
                "Article 22. Protection against arrest and detention in certain cases",
                (
                    "(1) No person who is arrested shall be detained in custody without being informed, as soon as may be, "
                    "of the grounds for such arrest nor shall he be denied the right to consult, and to be defended by, a "
                    "legal practitioner of his choice. (2) Every person who is arrested and detained in custody shall be "
                    "produced before the nearest magistrate within a period of twenty-four hours of such arrest excluding "
                    "the time necessary for the journey from the place of arrest to the court of the magistrate."
                ),
            ),
            (
                "Article 32. Remedies for enforcement of rights conferred by this Part",
                (
                    "(1) The right to move the Supreme Court by appropriate proceedings for the enforcement of the rights "
                    "conferred by this Part is guaranteed. (2) The Supreme Court shall have power to issue directions or "
                    "orders or writs, including writs in the nature of habeas corpus, mandamus, prohibition, quo warranto "
                    "and certiorari, whichever may be appropriate, for the enforcement of any of the rights conferred by this Part."
                ),
            ),
        ],
    ]
    _write_pdf(
        "constitution_fundamental_rights.pdf",
        "CONSTITUTION OF INDIA — PART III: FUNDAMENTAL RIGHTS",
        pages,
    )


def main() -> None:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    generate_clean_nda()
    generate_rental_agreement()
    generate_employment_agreement()
    generate_one_sided_agreement()
    generate_service_agreement_docx()
    generate_promissory_note_txt()
    generate_bns_pdf()
    generate_ipc_pdf()
    generate_constitution_pdf()


if __name__ == "__main__":
    main()
