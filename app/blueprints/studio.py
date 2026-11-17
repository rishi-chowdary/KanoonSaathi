"""LexiLegal AI — Simplification Studio Blueprint.

Provides:
- Web interface at /studio for interactive clause analysis and simplification
- REST API at POST /api/simplify for programmatic and client-side simplification
- REST API at GET /api/glossary returning the 150+ legal terms dictionary
"""

from __future__ import annotations

from flask import Blueprint, jsonify, render_template, request

from app.extensions import csrf
from app.nlp.simplifier import (
    get_sorted_glossary_terms,
    simplify_clause,
)

studio_bp = Blueprint("studio", __name__)

SAMPLE_CLAUSES = [
    {
        "name": "Indemnity & Defense",
        "category": "INDEMNITY",
        "text": (
            "The Tenant shall indemnify, defend, and hold harmless the Landlord, its agents, "
            "and contractors from and against any and all claims, liabilities, damages, losses, "
            "and costs (including reasonable attorneys' fees) resulting from the Tenant's use, "
            "occupancy, or conduct on the Leased Premises, or from any breach by the Tenant in "
            "the performance of any covenant herein, provided that the Landlord gives prompt written "
            "notice of such claim within thirty (30) days."
        ),
    },
    {
        "name": "Non-Compete Covenant",
        "category": "NON_COMPETE",
        "text": (
            "During the Employment Term and for a period of one (1) year following termination "
            "of employment, the Employee shall not, directly or indirectly, engage in, perform services "
            "for, or contribute knowledge to any business that competes with the Company within the territory."
        ),
    },
    {
        "name": "Confidentiality & Non-Disclosure",
        "category": "CONFIDENTIALITY",
        "text": (
            "The Receiving Party agrees that it shall not disclose, reproduce, summarize, or distribute "
            "any Confidential Information to any third party without the express prior written consent "
            "of the Disclosing Party, and shall use such information solely for the Purpose."
        ),
    },
    {
        "name": "Termination for Default",
        "category": "TERMINATION",
        "text": (
            "Either party may terminate this Agreement immediately upon written notice to the other "
            "party in the event that the other party breaches any material term or condition of this "
            "Agreement and fails to cure such breach within thirty (30) calendar days after receipt "
            "of written notice specifying the default."
        ),
    },
    {
        "name": "Severability",
        "category": "SEVERABILITY",
        "text": (
            "In the event that any provision of this Agreement is determined by a court of competent "
            "jurisdiction to be illegal, invalid, or otherwise unenforceable, such provision shall be "
            "deemed severed and deleted, and the remaining provisions of this Agreement shall continue "
            "in full force and effect."
        ),
    },
]


@studio_bp.route("/studio", methods=["GET"])
def studio_index():
    """Render the interactive Simplification Studio page."""
    return render_template(
        "studio/index.html",
        sample_clauses=SAMPLE_CLAUSES,
    )


@studio_bp.route("/api/simplify", methods=["POST"])
@csrf.exempt
def api_simplify():
    """Analyze and simplify arbitrary legal text.

    Request Body (JSON):
    - text: str (required)
    - mode: 'simple_english' | 'detailed' | 'professional' (default: 'simple_english')
    - category: str (optional)
    - affected_party: str (optional)

    Returns JSON with 3 modes, before/after Flesch readability, glossary terms, and traps.
    """
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

    results = []
    for term, plain, definition, category in terms_sorted:
        results.append(
            {
                "term": term,
                "plainReplacement": plain,
                "definition": definition,
                "category": category,
            }
        )

    return (
        jsonify(
            {
                "count": len(results),
                "terms": results,
            }
        ),
        200,
    )
