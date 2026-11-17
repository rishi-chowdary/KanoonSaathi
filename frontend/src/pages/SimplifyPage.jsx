import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import {
  FileText,
  Sparkles,
  Copy,
  Check,
  AlertCircle,
  HelpCircle,
  ShieldAlert,
  RotateCcw,
  BookOpen,
  ArrowRight,
} from "lucide-react";
import { simplifyLegalText } from "../services/api";

const SAMPLE_CLAUSES = [
  {
    name: "Indemnification",
    mode: "simple_english",
    context: "Master Services Agreement",
    text: "The Contractor agrees to defend, indemnify, and hold harmless the Company, its affiliates, directors, officers, and employees against any and all liabilities, losses, damages, claims, and expenses (including reasonable attorney fees) arising from any third-party claim alleging that the Deliverables infringe any copyright, patent, trademark, or trade secret, except to the extent such infringement results from Company specifications or unauthorized modifications.",
  },
  {
    name: "Termination for Convenience",
    mode: "detailed",
    context: "Commercial Vendor Agreement",
    text: "Either party may terminate this Agreement without cause at any time by delivering to the other party at least sixty (60) days advance written notice; provided, however, that Client shall promptly reimburse Contractor for all verified and approved expenses incurred and satisfactory services rendered prior to the effective date of termination.",
  },
  {
    name: "Non-Compete & Non-Solicit",
    mode: "professional",
    context: "Employment & Confidentiality Agreement",
    text: "During employment and for twelve (12) months following separation, Employee shall not directly or indirectly engage in any business competing directly with the Company within a fifty (50) mile radius, nor solicit or hire any person who was a full-time employee of the Company during the six (6) months preceding separation.",
  },
  {
    name: "Force Majeure",
    mode: "simple_english",
    context: "Supply Chain & Procurement Agreement",
    text: "Neither party shall be held liable for failure or delay in fulfilling obligations caused by circumstances beyond reasonable control, including acts of God, war, pandemic, governmental orders, or labor disputes; provided that the affected party delivers written notice within five (5) calendar days of the event and resumes performance promptly once the condition ceases.",
  },
];

export default function SimplifyPage() {
  const location = useLocation();
  const [text, setText] = useState(location.state?.prefillText || "");
  const [mode, setMode] = useState(location.state?.prefillMode || "simple_english");
  const [documentContext, setDocumentContext] = useState(location.state?.prefillContext || "");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("side-by-side");

  useEffect(() => {
    if (location.state?.prefillText) {
      setText(location.state.prefillText);
      if (location.state.prefillMode) setMode(location.state.prefillMode);
      if (location.state.prefillContext) setDocumentContext(location.state.prefillContext);
    }
  }, [location.state]);

  const handleLoadSample = (sample) => {
    setText(sample.text);
    setMode(sample.mode);
    setDocumentContext(sample.context);
    setError(null);
  };

  const handleClear = () => {
    setText("");
    setDocumentContext("");
    setResult(null);
    setError(null);
  };

  const handleSimplify = async (e) => {
    if (e) e.preventDefault();
    if (!text.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const data = await simplifyLegalText({
        text: text.trim(),
        mode,
        documentContext: documentContext.trim() || undefined,
      });
      setResult(data);
    } catch (err) {
      console.error("Simplification error:", err);
      const detail = err.response?.data?.detail || err.response?.data?.message || "Failed to simplify text. Please check server status.";
      setError(detail);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (!result?.explanation) return;
    try {
      await navigator.clipboard.writeText(result.explanation);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Failed to copy explanation", err);
    }
  };

  const charCount = text.length;
  const isOverLimit = charCount > 10000;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header */}
      <div className="border-b border-slate-200 dark:border-slate-800 pb-5">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold font-legal text-slate-900 dark:text-white">
              Simplify Legal Text
            </h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              Paste arbitrary clauses or legal provisions to convert them into plain English with key terms defined and subtle traps highlighted.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-500 dark:text-slate-400 font-medium hidden sm:inline">
              Sample clauses:
            </span>
            <div className="flex items-center gap-1.5 flex-wrap">
              {SAMPLE_CLAUSES.map((s) => (
                <button
                  key={s.name}
                  type="button"
                  onClick={() => handleLoadSample(s)}
                  className="px-2.5 py-1 text-xs font-medium rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:border-slate-400 dark:hover:border-slate-600 transition-colors"
                >
                  {s.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left Column: Input Form (5 cols) */}
        <div className="lg:col-span-5 space-y-4">
          <form onSubmit={handleSimplify} className="border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 p-5 shadow-xs space-y-4">
            {/* Mode Selector */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
                Explanation Style
              </label>
              <div className="grid grid-cols-3 gap-1.5 p-1 rounded-md border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-xs">
                <button
                  type="button"
                  onClick={() => setMode("simple_english")}
                  className={`py-1.5 px-2 rounded font-medium text-center transition-colors ${
                    mode === "simple_english"
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                  }`}
                >
                  Simple English
                </button>
                <button
                  type="button"
                  onClick={() => setMode("detailed")}
                  className={`py-1.5 px-2 rounded font-medium text-center transition-colors ${
                    mode === "detailed"
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                  }`}
                >
                  Detailed
                </button>
                <button
                  type="button"
                  onClick={() => setMode("professional")}
                  className={`py-1.5 px-2 rounded font-medium text-center transition-colors ${
                    mode === "professional"
                      ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                      : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                  }`}
                >
                  Professional
                </button>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-1.5">
                {mode === "simple_english" && "Clear, conversational English eliminating jargon while preserving all conditions."}
                {mode === "detailed" && "Clause-by-clause breakdown of obligations, triggers, and procedural requirements."}
                {mode === "professional" && "Commercial executive summary focused on commercial risk and business impact."}
              </p>
            </div>

            {/* Document Context (Optional) */}
            <div>
              <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-1">
                Document Context <span className="text-slate-400 font-normal lowercase">(optional)</span>
              </label>
              <input
                type="text"
                value={documentContext}
                onChange={(e) => setDocumentContext(e.target.value)}
                placeholder="e.g., Commercial Lease, Vendor Agreement, Employment Offer"
                className="w-full text-xs px-3 py-2 rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-slate-400"
              />
            </div>

            {/* Legal Text Area */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <label className="block text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
                  Original Legal Text
                </label>
                <span className={`text-[11px] font-mono ${isOverLimit ? "text-rose-600 font-bold" : "text-slate-400"}`}>
                  {charCount} / 10,000
                </span>
              </div>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                rows={10}
                placeholder="Paste contract clause or legal paragraph here..."
                required
                className={`w-full text-xs font-mono p-3 rounded border bg-white dark:bg-slate-950 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-1 ${
                  isOverLimit
                    ? "border-rose-400 focus:ring-rose-500"
                    : "border-slate-200 dark:border-slate-800 focus:ring-slate-400"
                }`}
              />
            </div>

            {/* Error Message */}
            {error && (
              <div className="p-3 rounded bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
                <p>{error}</p>
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-2">
              <button
                type="button"
                onClick={handleClear}
                disabled={loading || (!text && !result)}
                className="inline-flex items-center gap-1 px-3 py-1.5 text-xs text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors disabled:opacity-50"
              >
                <RotateCcw className="w-3.5 h-3.5" /> Clear
              </button>

              <button
                type="submit"
                disabled={loading || !text.trim() || isOverLimit}
                className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-semibold rounded bg-slate-900 hover:bg-slate-800 dark:bg-white dark:text-slate-900 dark:hover:bg-slate-100 text-white shadow-xs transition-colors disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <span className="w-3.5 h-3.5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                    Simplifying...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" /> Simplify Text
                  </>
                )}
              </button>
            </div>
          </form>
        </div>

        {/* Right Column: Output / Side-by-Side (7 cols) */}
        <div className="lg:col-span-7 space-y-4">
          {!result && !loading && (
            <div className="border border-dashed border-slate-300 dark:border-slate-800 rounded-lg p-12 text-center bg-white/50 dark:bg-slate-900/40">
              <BookOpen className="w-10 h-10 text-slate-400 mx-auto mb-3" />
              <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
                No text simplified yet
              </h3>
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 max-w-md mx-auto">
                Paste any contract text on the left, select your preferred explanation style, or click one of the sample clauses above to test the simplifier.
              </p>
            </div>
          )}

          {loading && (
            <div className="border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 p-6 shadow-xs space-y-4 animate-pulse">
              <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/4" />
              <div className="space-y-2">
                <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-full" />
                <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-5/6" />
                <div className="h-3 bg-slate-200 dark:bg-slate-800 rounded w-4/6" />
              </div>
              <div className="pt-4 border-t border-slate-100 dark:border-slate-800 space-y-2">
                <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/3" />
                <div className="h-16 bg-slate-100 dark:bg-slate-800/60 rounded" />
              </div>
            </div>
          )}

          {result && !loading && (() => {
            const displayMode = (result.mode || mode || "simple_english").replace("_", " ");
            const isGrounded = result.is_grounded !== false && result.isGrounded !== false;
            const originalText = result.original_text || result.originalText || text;
            const explanation = result.explanation || "";
            const glossary = result.glossary || [];
            const whatCouldBeMissed = result.what_could_be_missed || result.whatCouldBeMissed || [];
            const warnings = result.warnings || [];

            return (
            <div className="space-y-4">
              {/* Output Header with Badges & Copy */}
              <div className="flex items-center justify-between flex-wrap gap-2 pb-1 border-b border-slate-200 dark:border-slate-800">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="px-2 py-0.5 rounded text-[11px] font-medium uppercase tracking-wider bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                    Mode: {displayMode}
                  </span>

                  {isGrounded ? (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-900">
                      <Check className="w-3 h-3" /> Grounded (No Invented Figures)
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-700 border border-amber-200 dark:bg-amber-950/40 dark:text-amber-300 dark:border-amber-900">
                      <AlertCircle className="w-3 h-3" /> Consistency Warning
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2">
                  <div className="inline-flex p-0.5 rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 text-[11px]">
                    <button
                      type="button"
                      onClick={() => setActiveTab("side-by-side")}
                      className={`px-2 py-0.5 rounded font-medium transition-colors ${
                        activeTab === "side-by-side"
                          ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                          : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                      }`}
                    >
                      Side-by-Side
                    </button>
                    <button
                      type="button"
                      onClick={() => setActiveTab("explanation-only")}
                      className={`px-2 py-0.5 rounded font-medium transition-colors ${
                        activeTab === "explanation-only"
                          ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                          : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                      }`}
                    >
                      Explanation Only
                    </button>
                  </div>

                  <button
                    type="button"
                    onClick={handleCopy}
                    className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
                  >
                    {copied ? (
                      <>
                        <Check className="w-3.5 h-3.5 text-emerald-600" /> Copied
                      </>
                    ) : (
                      <>
                        <Copy className="w-3.5 h-3.5" /> Copy
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Consistency Warnings */}
              {warnings.length > 0 && (
                <div className="p-3 rounded bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900 text-xs text-amber-800 dark:text-amber-200 space-y-1">
                  <div className="font-semibold flex items-center gap-1.5">
                    <AlertCircle className="w-3.5 h-3.5" /> Number/Date Consistency Note
                  </div>
                  <ul className="list-disc list-inside space-y-0.5 pl-1 text-[11px]">
                    {warnings.map((w, idx) => (
                      <li key={idx}>{w}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Side-by-Side View */}
              {activeTab === "side-by-side" ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Original Text Box */}
                  <div className="border border-slate-200 dark:border-slate-800 rounded-lg bg-slate-50/70 dark:bg-slate-950 p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                        Original Contract Clause
                      </span>
                    </div>
                    <p className="text-xs font-legal leading-relaxed text-slate-700 dark:text-slate-300 whitespace-pre-line select-text">
                      {originalText}
                    </p>
                  </div>

                  {/* Explanation Box */}
                  <div className="border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 p-4 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[11px] font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wider">
                        Plain Language Explanation
                      </span>
                    </div>
                    <p className="text-xs leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-line select-text">
                      {explanation}
                    </p>
                  </div>
                </div>
              ) : (
                /* Explanation Only */
                <div className="border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 p-5 space-y-2">
                  <span className="text-[11px] font-semibold text-blue-700 dark:text-blue-400 uppercase tracking-wider block">
                    Plain Language Explanation
                  </span>
                  <p className="text-sm leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-line select-text">
                    {explanation}
                  </p>
                </div>
              )}

              {/* Key Terms Explained (Glossary) */}
              {glossary.length > 0 && (
                <div className="border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 p-4 space-y-3">
                  <div className="flex items-center gap-1.5">
                    <HelpCircle className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                    <h3 className="text-xs font-semibold text-slate-900 dark:text-white uppercase tracking-wider">
                      Key Terms Explained
                    </h3>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                    {glossary.map((item, idx) => (
                      <div
                        key={idx}
                        className="p-3 rounded border border-slate-100 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/40 space-y-1"
                      >
                        <span className="inline-block px-2 py-0.5 rounded text-[11px] font-bold text-slate-900 dark:text-white bg-slate-200/80 dark:bg-slate-700">
                          {item.term}
                        </span>
                        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
                          {item.definition}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* What Could Be Missed */}
              {whatCouldBeMissed.length > 0 && (
                <div className="border border-amber-200 dark:border-amber-900/60 rounded-lg bg-amber-50/40 dark:bg-amber-950/20 p-4 space-y-2.5">
                  <div className="flex items-center gap-1.5 text-amber-800 dark:text-amber-300">
                    <ShieldAlert className="w-4 h-4 shrink-0" />
                    <h3 className="text-xs font-semibold uppercase tracking-wider">
                      What Could Be Missed
                    </h3>
                  </div>
                  <ul className="space-y-1.5 pl-1">
                    {whatCouldBeMissed.map((note, idx) => (
                      <li
                        key={idx}
                        className="text-xs text-slate-700 dark:text-slate-300 flex items-start gap-2 leading-relaxed"
                      >
                        <span className="text-amber-600 dark:text-amber-400 font-bold shrink-0 mt-0.5">•</span>
                        <span>{note}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
            );
          })()}
        </div>
      </div>
    </div>
  );
}
