import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  BookOpen,
  User,
  Tag,
  AlertTriangle,
  Sparkles,
  HelpCircle,
  ShieldAlert,
  ExternalLink,
  Loader2,
} from "lucide-react";
import ProvenanceBadge from "../common/ProvenanceBadge";
import { reExplainDocumentClause, simplifyLegalText } from "../../services/api";

export default function ClauseCard({
  clause,
  documentId = null,
  globalMode = "simple",
  onViewPage = null,
}) {
  const navigate = useNavigate();
  const [localMode, setLocalMode] = useState(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [copied, setCopied] = useState(false);

  // Deep dive "Explain this" state
  const [showDeepDive, setShowDeepDive] = useState(false);
  const [deepDiveLoading, setDeepDiveLoading] = useState(false);
  const [deepDiveData, setDeepDiveData] = useState(null);
  const [deepDiveError, setDeepDiveError] = useState(null);

  const activeMode = localMode || globalMode;

  const modeToApi = (m) => {
    switch (m) {
      case "detailed":
        return "detailed";
      case "professional":
        return "professional";
      case "simple":
      default:
        return "simple_english";
    }
  };

  const getExplanation = () => {
    switch (activeMode) {
      case "detailed":
        return clause.simplifiedDetailed || clause.simplifiedSimple;
      case "professional":
        return clause.simplifiedProfessional || clause.simplifiedSimple;
      case "simple":
      default:
        return clause.simplifiedSimple;
    }
  };

  const handleCopy = async () => {
    const textToCopy = `Clause: ${clause.title} (${clause.category})\n` +
      `Explanation (${activeMode}):\n${getExplanation()}\n\n` +
      `Original Text (Page ${clause.sourcePage}):\n${clause.originalText}`;
    try {
      await navigator.clipboard.writeText(textToCopy);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy clause text", err);
    }
  };

  const handleExplainThis = async (overrideMode = null) => {
    const targetMode = overrideMode || activeMode;
    const apiMode = modeToApi(targetMode);

    if (!showDeepDive) {
      setShowDeepDive(true);
    }

    setDeepDiveLoading(true);
    setDeepDiveError(null);

    try {
      let data;
      if (documentId && clause.id) {
        data = await reExplainDocumentClause(documentId, clause.id, apiMode);
      } else {
        data = await simplifyLegalText({
          text: clause.originalText,
          mode: apiMode,
          documentContext: `Clause: ${clause.title} (${clause.category})`,
        });
      }
      setDeepDiveData(data);
    } catch (err) {
      console.error("Failed to generate deep dive explanation", err);
      setDeepDiveError(err.response?.data?.detail || "Could not generate detailed explanation.");
    } finally {
      setDeepDiveLoading(false);
    }
  };

  const handleOpenInStudio = () => {
    navigate("/simplify", {
      state: {
        prefillText: clause.originalText,
        prefillContext: `Clause: ${clause.title} (${clause.category})`,
        prefillMode: modeToApi(activeMode),
      },
    });
  };

  const importanceBadge = () => {
    const imp = (clause.importance || "MEDIUM").toUpperCase();
    if (imp === "HIGH") {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-semibold uppercase tracking-wider bg-rose-50 text-rose-700 border border-rose-200 dark:bg-rose-950/40 dark:text-rose-300 dark:border-rose-900">
          High Importance
        </span>
      );
    }
    if (imp === "LOW") {
      return (
        <span className="px-2 py-0.5 rounded text-[11px] font-medium uppercase tracking-wider bg-slate-100 text-slate-600 border border-slate-200 dark:bg-slate-800 dark:text-slate-400 dark:border-slate-700">
          Low Importance
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[11px] font-medium uppercase tracking-wider bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900">
        Medium Importance
      </span>
    );
  };

  return (
    <div className="border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 p-5 shadow-xs space-y-4 hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-3">
        <div className="space-y-1.5 flex-1">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
              <Tag className="w-3 h-3 text-slate-500" />
              {clause.category === "Other" && clause.customLabel
                ? clause.customLabel
                : clause.category}
            </span>

            {clause.sectionReference && (
              <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-blue-50 dark:bg-blue-950/40 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900">
                {clause.sectionReference}
              </span>
            )}

            {importanceBadge()}
          </div>

          <h3 className="text-sm font-semibold text-slate-900 dark:text-white leading-snug">
            {clause.title}
          </h3>
        </div>

        {/* Local Mode Selector & Copy Button */}
        <div className="flex items-center gap-1.5 self-start">
          <div className="inline-flex p-0.5 rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-[11px]">
            <button
              type="button"
              onClick={() => setLocalMode("simple")}
              className={`px-2 py-0.5 rounded font-medium transition-colors ${
                activeMode === "simple"
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
              title="Simple English explanation"
            >
              Simple
            </button>
            <button
              type="button"
              onClick={() => setLocalMode("detailed")}
              className={`px-2 py-0.5 rounded font-medium transition-colors ${
                activeMode === "detailed"
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
              title="Detailed breakdown preserving exceptions"
            >
              Detailed
            </button>
            <button
              type="button"
              onClick={() => setLocalMode("professional")}
              className={`px-2 py-0.5 rounded font-medium transition-colors ${
                activeMode === "professional"
                  ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                  : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
              }`}
              title="Professional commercial summary"
            >
              Professional
            </button>
          </div>

          <button
            type="button"
            onClick={handleCopy}
            className="p-1.5 rounded border border-slate-200 dark:border-slate-800 text-slate-500 hover:text-slate-800 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
            title="Copy explanation and clause text"
          >
            {copied ? (
              <Check className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
            ) : (
              <Copy className="w-3.5 h-3.5" />
            )}
          </button>
        </div>
      </div>

      {/* Primary Explanation Text */}
      <div className="text-xs leading-relaxed text-slate-700 dark:text-slate-300 bg-slate-50/70 dark:bg-slate-800/40 p-3.5 rounded border border-slate-100 dark:border-slate-800">
        <div className="font-medium text-[11px] text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1">
          {activeMode === "simple"
            ? "Plain English Explanation"
            : activeMode === "detailed"
            ? "Detailed Legal Breakdown"
            : "Commercial Analysis"}
        </div>
        <p className="whitespace-pre-line">{getExplanation()}</p>
      </div>

      {/* Metadata & Actions Row */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pt-1 gap-2 text-xs">
        <div className="flex items-center gap-3 flex-wrap text-slate-500 dark:text-slate-400">
          {clause.affectedParty && (
            <span className="flex items-center gap-1 text-[11px]">
              <User className="w-3 h-3 text-slate-400" />
              Party: <strong className="font-medium text-slate-700 dark:text-slate-300">{clause.affectedParty}</strong>
            </span>
          )}

          <ProvenanceBadge
            provenance={clause.provenance || "EXTRACTED"}
            quoteVerified={clause.quoteVerified}
            page={clause.sourcePage}
          />
        </div>

        <div className="flex items-center gap-2">
          {/* "Explain this" Button */}
          <button
            type="button"
            onClick={() => handleExplainThis()}
            disabled={deepDiveLoading}
            className={`inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-semibold rounded border transition-colors ${
              showDeepDive
                ? "bg-blue-50 dark:bg-blue-950/60 text-blue-700 dark:text-blue-300 border-blue-200 dark:border-blue-900"
                : "border-slate-200 dark:border-slate-800 text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-950/30"
            }`}
            title="Deep dive with glossary terms and subtle traps"
          >
            {deepDiveLoading ? (
              <Loader2 className="w-3 h-3 animate-spin" />
            ) : (
              <Sparkles className="w-3 h-3" />
            )}
            {showDeepDive ? "Explaining..." : "Explain this"}
          </button>

          {onViewPage && clause.sourcePage && (
            <button
              type="button"
              onClick={() => onViewPage(clause.sourcePage)}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 rounded transition-colors"
            >
              <BookOpen className="w-3 h-3" />
              Page {clause.sourcePage}
            </button>
          )}

          <button
            type="button"
            onClick={() => setIsExpanded(!isExpanded)}
            className="inline-flex items-center gap-1 px-2.5 py-1 text-[11px] font-medium text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          >
            {isExpanded ? (
              <>
                Hide Original <ChevronUp className="w-3 h-3" />
              </>
            ) : (
              <>
                Original Text <ChevronDown className="w-3 h-3" />
              </>
            )}
          </button>
        </div>
      </div>

      {/* Deep Dive Panel (Explain this section) */}
      {showDeepDive && (
        <div className="pt-3 border-t border-blue-100 dark:border-blue-950/50 space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
              <h4 className="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
                In-Depth Analysis & Legal Terms
              </h4>
            </div>

            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={handleOpenInStudio}
                className="inline-flex items-center gap-1 text-[11px] text-blue-600 dark:text-blue-400 hover:underline"
              >
                Open in Simplify <ExternalLink className="w-3 h-3" />
              </button>
              <button
                type="button"
                onClick={() => setShowDeepDive(false)}
                className="text-xs text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                Close
              </button>
            </div>
          </div>

          {deepDiveLoading && (
            <div className="p-4 rounded bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-800 flex items-center justify-center gap-2 text-xs text-slate-500">
              <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              <span>Analyzing clause and defining legal terms...</span>
            </div>
          )}

          {deepDiveError && (
            <div className="p-3 rounded bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs text-rose-700 dark:text-rose-300">
              {deepDiveError}
            </div>
          )}

          {deepDiveData && !deepDiveLoading && (
            <div className="space-y-3 text-xs">
              {/* Key Terms Defined (Glossary) */}
              {deepDiveData.glossary && deepDiveData.glossary.length > 0 && (
                <div className="p-3 rounded bg-slate-50/80 dark:bg-slate-800/40 border border-slate-200/80 dark:border-slate-800 space-y-2">
                  <div className="flex items-center gap-1 text-slate-700 dark:text-slate-300 font-semibold text-[11px] uppercase tracking-wider">
                    <HelpCircle className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                    Key Legal Terms Explained
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {deepDiveData.glossary.map((item, idx) => (
                      <div
                        key={idx}
                        className="p-2 rounded bg-white dark:bg-slate-900 border border-slate-100 dark:border-slate-800 space-y-0.5"
                      >
                        <span className="font-semibold text-slate-900 dark:text-white text-[11px]">
                          {item.term}
                        </span>
                        <p className="text-[11px] text-slate-600 dark:text-slate-400 leading-normal">
                          {item.definition}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* What Could Be Missed */}
              {deepDiveData.whatCouldBeMissed && deepDiveData.whatCouldBeMissed.length > 0 && (
                <div className="p-3 rounded bg-amber-50/40 dark:bg-amber-950/20 border border-amber-200 dark:border-amber-900/60 space-y-1.5">
                  <div className="flex items-center gap-1 text-amber-800 dark:text-amber-300 font-semibold text-[11px] uppercase tracking-wider">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    What Could Be Missed (Traps & Nuances)
                  </div>
                  <ul className="space-y-1 pl-1">
                    {deepDiveData.whatCouldBeMissed.map((note, idx) => (
                      <li key={idx} className="flex items-start gap-1.5 text-slate-700 dark:text-slate-300 text-[11px]">
                        <span className="text-amber-600 font-bold">•</span>
                        <span>{note}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Original Text Expander */}
      {isExpanded && (
        <div className="pt-3 border-t border-slate-100 dark:border-slate-800 space-y-3">
          <div className="p-3.5 rounded bg-slate-100/70 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 text-xs font-legal leading-relaxed text-slate-800 dark:text-slate-300 select-text">
            <div className="font-sans font-medium text-[11px] text-slate-400 dark:text-slate-500 uppercase tracking-wider mb-1.5 flex items-center justify-between">
              <span>Original Contract Text (Page {clause.sourcePage})</span>
              {clause.sectionReference && <span>{clause.sectionReference}</span>}
            </div>
            <p className="whitespace-pre-line">{clause.originalText}</p>
          </div>

          {clause.evidenceQuote && (
            <div className="p-3 rounded bg-blue-50/60 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/60 text-xs text-blue-900 dark:text-blue-200">
              <span className="font-semibold text-[11px] text-blue-700 dark:text-blue-300 block mb-0.5">
                Grounded Key Quote:
              </span>
              <p className="italic">"{clause.evidenceQuote}"</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
