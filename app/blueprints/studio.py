"""Simplification Studio blueprint for Indian statutes, constitutional clauses, and contracts."""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.extensions import csrf
from app.nlp.indian_law import search_indian_statutes
from app.nlp.simplification import (
    get_sorted_glossary_terms,
    simplify_clause,
)

studio_bp = Blueprint("studio", __name__)

SAMPLE_CLAUSES = [
    {
        "name": "BNS Sec. 318 (Cheating / IPC 420)",
        "category": "BNS_SECTION",
        "text": (
            "Section 318. Cheating. (4) Whoever cheats and thereby dishonestly induces the person "
            "deceived to deliver any property to any person, or to make, alter or destroy the whole "
            "or any part of a valuable security, or anything which is signed or sealed, and which is "
            "capable of being converted into a valuable security, shall be punished with imprisonment "
            "of either description for a term which may extend to seven years, and shall also be liable to fine."
        ),
    },
    {
        "name": "BNS Sec. 103 (Murder / IPC 302)",
        "category": "BNS_SECTION",
        "text": (
            "Section 103. Punishment for murder. (1) Whoever commits murder shall be punished with "
            "death or imprisonment for life, and shall also be liable to fine. (2) When a group of "
            "five or more persons acting in concert commits murder on the ground of race, caste or "
            "community, sex, place of birth, language, personal belief or any other similar ground "
            "each member of such group shall be punished with death or with imprisonment for life, "
            "and shall also be liable to fine."
        ),
    },
    {
        "name": "IPC Sec. 406 / BNS 316 (Breach of Trust)",
        "category": "IPC_SECTION",
        "text": (
            "Section 406 of the Indian Penal Code (corresponding to BNS Section 316). Whoever, being "
            "in any manner entrusted with property, or with any dominion over property, dishonestly "
            "misappropriates or converts to his own use that property in violation of any direction of "
            "law or legal contract commits criminal breach of trust and shall be punished with "
            "imprisonment of either description for a term which may extend to three years under IPC "
            "(extended to five years under BNS Section 316), or with fine, or with both."
        ),
    },
    {
        "name": "Constitution Art. 21 (Life & Liberty)",
        "category": "CONSTITUTIONAL_CLAUSE",
        "text": (
            "Article 21. Protection of life and personal liberty. No person shall be deprived of his "
            "life or personal liberty except according to procedure established by law."
        ),
    },
    {
        "name": "Constitution Art. 19(1)(a) & 19(2)",
        "category": "CONSTITUTIONAL_CLAUSE",
        "text": (
            "Article 19. (1) All citizens shall have the right (a) to freedom of speech and expression. "
            "(2) Nothing in sub-clause (a) of clause (1) shall affect the operation of any existing law, "
            "or prevent the State from making any law, in so far as such law imposes reasonable restrictions "
            "on the exercise of the right conferred by the said sub-clause in the interests of the "
            "sovereignty and integrity of India, the security of the State, public order, decency or "
            "morality or in relation to contempt of court, defamation or incitement to an offence."
        ),
    },
    {
        "name": "Indian Leave & License Indemnity",
        "category": "INDEMNITY",
        "text": (
            "The Licensee shall indemnify, defend, and hold harmless the Licensor from and against "
            "any and all claims, liabilities, damages, losses, and costs arising out of the Licensee's "
            "occupancy of the Licensed Premises in Bengaluru, provided that the Licensor gives written "
            "notice of such claim within thirty (30) days."
        ),
    },
]


@studio_bp.route("/studio", methods=["GET"])
def studio_index():
    """Render the interactive Simplification Studio and Indian Statute Lookup page."""
    return render_template(
        "studio/index.html",
        sample_clauses=SAMPLE_CLAUSES,
        statutes=search_indian_statutes(),
    )


@studio_bp.route("/api/simplify", methods=["POST"])
@csrf.exempt
def api_simplify():
    """Analyze and simplify an Indian statute section, constitutional clause, or contract clause."""
    payload = request.get_json(silent=True) or {}
    text = payload.get("text", "").strip()

    if not text:
        return (
            jsonify(
                {
                    "error": "Field 'text' is required and cannot be empty.",
                    "status": 400,
                }
            ),
            400,
        )

    mode = payload.get("mode", "simple_english").lower()
    category = payload.get("category", "")
    affected_party = payload.get("affected_party", "") or payload.get(
        "affectedParty", ""
    )

    simplified = simplify_clause(
        original_text=text,
        category=category,
        affected_party=affected_party,
    )

    if mode == "detailed":
        selected_explanation = simplified["detailed"]
    elif mode == "professional":
        selected_explanation = simplified["professional"]
    else:
        mode = "simple_english"
        selected_explanation = simplified["simple_english"]

    warning_points = [t["explanation"] for t in simplified["traps_and_nuances"]]

    return (
        jsonify(
            {
                "mode": mode,
                "explanation": selected_explanation,
                "simpleEnglish": simplified["simple_english"],
                "detailed": simplified["detailed"],
                "professional": simplified["professional"],
                "readabilityOriginal": simplified["readability_original"],
                "readabilitySimple": simplified["readability_simple"],
                "readabilityDetailed": simplified["readability_detailed"],
                "glossary": simplified["glossary_terms"],
                "warningPoints": warning_points,
                "traps": simplified["traps_and_nuances"],
                "statuteReferences": simplified["statute_references"],
                "preservationVerified": simplified["preservation_verified"],
            }
        ),
        200,
    )


@studio_bp.route("/api/glossary", methods=["GET"])
def api_glossary():
    """Return all terms in the legal glossary."""
    terms_raw = get_sorted_glossary_terms()
    terms_sorted = sorted(terms_raw, key=lambda x: x[0].lower())

    results = [
        {
            "term": term,
            "plainReplacement": plain,
            "definition": definition,
            "category": category,
        }
        for term, plain, definition, category in terms_sorted
    ]

    return jsonify({"count": len(results), "terms": results}), 200


@studio_bp.route("/api/statutes", methods=["GET"])
def api_statutes():
    """Search offline BNS 2023 <-> IPC 1860 sections and Constitution of India articles."""
    query = request.args.get("q", "").strip()
    statute_type = request.args.get("type", "all").strip()
    entries = search_indian_statutes(query=query, statute_type=statute_type)
    return jsonify({"count": len(entries), "statutes": entries}), 200
