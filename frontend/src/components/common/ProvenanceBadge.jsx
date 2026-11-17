import React from "react";
import { CheckCircle2, AlertTriangle, Sparkles, FileText } from "lucide-react";

/**
 * ProvenanceBadge: Displays grounding metadata for an extracted item or clause.
 * - EXTRACTED: Verifiable direct quote from the source document.
 * - AI_INTERPRETATION: Synthesized inference / analysis by LLM.
 * Also flags unverified quotes if fuzzy match failed against document text.
 */
export default function ProvenanceBadge({
  provenance = "EXTRACTED",
  quoteVerified = true,
  page = null,
  className = "",
}) {
  const isDirect = provenance === "EXTRACTED";

  return (
    <div className={`inline-flex items-center gap-1.5 flex-wrap text-[11px] ${className}`}>
      {/* Provenance pill */}
      {isDirect ? (
        <span
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-medium bg-blue-50 dark:bg-blue-950/50 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900"
          title="Directly grounded in document text"
        >
          <FileText className="w-3 h-3 text-blue-600 dark:text-blue-400" />
          Extracted
        </span>
      ) : (
        <span
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-medium bg-purple-50 dark:bg-purple-950/50 text-purple-700 dark:text-purple-300 border border-purple-200 dark:border-purple-900"
          title="AI synthesis / inference based on surrounding context"
        >
          <Sparkles className="w-3 h-3 text-purple-600 dark:text-purple-400" />
          AI Interpretation
        </span>
      )}

      {/* Page citation */}
      {page !== null && page !== undefined && (
        <span className="inline-flex items-center px-1.5 py-0.5 rounded font-medium bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-400">
          p. {page}
        </span>
      )}

      {/* Quote verification alert (only shown if a direct quote was supplied but failed fuzzy match) */}
      {!quoteVerified && (
        <span
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded font-medium bg-amber-50 dark:bg-amber-950/50 text-amber-800 dark:text-amber-300 border border-amber-300 dark:border-amber-800"
          title="Evidence quote could not be verified against extracted document text"
        >
          <AlertTriangle className="w-3 h-3 text-amber-600 dark:text-amber-400" />
          Unverified Quote
        </span>
      )}

      {quoteVerified && isDirect && (
        <span
          className="inline-flex items-center gap-0.5 px-1.5 py-0.5 rounded text-[10px] font-medium bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-900"
          title="Quote matched document text with >= 90% fidelity"
        >
          <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600 dark:text-emerald-400" />
          Verified
        </span>
      )}
    </div>
  );
}
