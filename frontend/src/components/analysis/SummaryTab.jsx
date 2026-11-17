import React, { useState, useEffect } from "react";
import api from "../../services/api";
import ProvenanceBadge from "../common/ProvenanceBadge";
import {
  Users,
  ShieldCheck,
  FileCheck2,
  DollarSign,
  RotateCw,
  Sparkles,
  AlertCircle,
  Quote,
  CheckCircle2,
  Info,
} from "lucide-react";

export default function SummaryTab({ documentId, documentStatus, onStatusChange }) {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reanalyzing, setReanalyzing] = useState(false);
  const [summaryMode, setSummaryMode] = useState("short"); // "short" | "detailed"
  const [error, setError] = useState(null);

  useEffect(() => {
    let timer = null;
    let isMounted = true;

    async function fetchAnalysis() {
      if (!documentId) return;

      try {
        const resp = await api.get(`/documents/${documentId}/analysis`);
        if (isMounted) {
          setAnalysis(resp.data);
          setError(null);
          setLoading(false);
        }
      } catch (err) {
        if (!isMounted) return;
        if (err.response?.status === 404) {
          // Analysis not ready yet
          setAnalysis(null);
          // If document is in progress, poll
          if (documentStatus === "ANALYZING" || documentStatus === "EXTRACTED" || documentStatus === "EXTRACTING") {
            timer = setTimeout(fetchAnalysis, 2500);
          } else {
            setLoading(false);
          }
        } else {
          setError(err.response?.data?.message || "Failed to load document analysis.");
          setLoading(false);
        }
      }
    }

    fetchAnalysis();

    return () => {
      isMounted = false;
      if (timer) clearTimeout(timer);
    };
  }, [documentId, documentStatus]);

  const handleReanalyze = async () => {
    try {
      setReanalyzing(true);
      setError(null);
      await api.post(`/documents/${documentId}/reanalyze`);
      if (onStatusChange) {
        onStatusChange("ANALYZING");
      }
      setLoading(true);
      setAnalysis(null);
      // Wait briefly then poll
      setTimeout(async () => {
        try {
          const resp = await api.get(`/documents/${documentId}/analysis`);
          setAnalysis(resp.data);
        } catch (_) {
          // Will be picked up by polling
        } finally {
          setReanalyzing(false);
        }
      }, 3000);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to trigger reanalysis.");
      setReanalyzing(false);
    }
  };

  // 1. Loading Skeleton during analysis or initial fetch
  if (loading || (documentStatus === "ANALYZING" && !analysis)) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-4">
          <div className="flex items-center justify-between">
            <div className="h-5 w-48 bg-slate-200 dark:bg-slate-800 rounded"></div>
            <div className="h-6 w-24 bg-slate-200 dark:bg-slate-800 rounded"></div>
          </div>
          <div className="h-4 w-3/4 bg-slate-200 dark:bg-slate-800 rounded"></div>
          <div className="h-16 w-full bg-slate-100 dark:bg-slate-800/60 rounded"></div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="p-5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 h-40"></div>
          <div className="p-5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 h-40"></div>
        </div>

        <div className="text-center py-6 text-xs text-slate-500 flex items-center justify-center gap-2">
          <RotateCw className="w-4 h-4 animate-spin text-blue-600 dark:text-blue-400" />
          <span>Generating structured contract summary &amp; verifying evidence quotes...</span>
        </div>
      </div>
    );
  }

  // 2. Failure State
  if (error || (!analysis && documentStatus === "FAILED")) {
    return (
      <div className="p-6 rounded-lg border border-rose-200 dark:border-rose-900/60 bg-rose-50 dark:bg-rose-950/30 space-y-4">
        <div className="flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-rose-600 dark:text-rose-400 mt-0.5 shrink-0" />
          <div>
            <h3 className="text-sm font-semibold text-rose-900 dark:text-rose-200">
              Analysis Failed or Unavailable
            </h3>
            <p className="text-xs text-rose-700 dark:text-rose-300 mt-1">
              {error || "The structured analysis could not be completed for this document."}
            </p>
          </div>
        </div>
        <div className="pt-2">
          <button
            type="button"
            onClick={handleReanalyze}
            disabled={reanalyzing}
            className="inline-flex items-center gap-1.5 px-3.5 py-1.5 rounded-md text-xs font-medium bg-rose-600 hover:bg-rose-700 text-white disabled:opacity-50 transition-colors"
          >
            <RotateCw className={`w-3.5 h-3.5 ${reanalyzing ? "animate-spin" : ""}`} />
            {reanalyzing ? "Reanalyzing..." : "Retry Analysis"}
          </button>
        </div>
      </div>
    );
  }

  // 3. Extracted but Analysis Not Started Yet
  if (!analysis) {
    return (
      <div className="p-8 text-center rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
        <FileCheck2 className="w-8 h-8 text-slate-400 mx-auto" />
        <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
          Ready for Analysis
        </h3>
        <p className="text-xs text-slate-500 max-w-md mx-auto">
          Document text has been extracted. Click below to run structured summary extraction with evidence quote verification.
        </p>
        <button
          type="button"
          onClick={handleReanalyze}
          disabled={reanalyzing}
          className="inline-flex items-center gap-1.5 px-4 py-2 rounded-md text-xs font-semibold bg-blue-600 hover:bg-blue-700 text-white shadow-sm disabled:opacity-50 transition-colors"
        >
          <Sparkles className={`w-3.5 h-3.5 ${reanalyzing ? "animate-spin" : ""}`} />
          {reanalyzing ? "Analyzing Document..." : "Run Summary Analysis"}
        </button>
      </div>
    );
  }

  // 4. Render Analysis Results
  const parseList = (val) => {
    if (Array.isArray(val)) return val;
    if (typeof val === "string") {
      try {
        const parsed = JSON.parse(val);
        return Array.isArray(parsed) ? parsed : [];
      } catch (_) {
        return [];
      }
    }
    return [];
  };

  const parties = parseList(analysis.parties);
  const mainConditions = parseList(analysis.mainConditions);
  const obligations = parseList(analysis.obligations || analysis.obligationsSummary);
  const financialTerms = parseList(analysis.financialTerms || analysis.financialTermsSummary);

  const rawRate = Number(analysis.verificationRate) || 0;
  const verificationPercent = rawRate <= 1.0 ? Math.round(rawRate * 100) : Math.min(100, Math.round(rawRate));

  return (
    <div className="space-y-6">
      {/* Header Overview Card */}
      <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100 dark:border-slate-800">
          <div>
            <div className="flex items-center gap-2 flex-wrap">
              <h2 className="text-base font-bold text-slate-900 dark:text-white">
                {analysis.title || "Legal Document Analysis"}
              </h2>
              {analysis.documentType && (
                <span className="px-2.5 py-0.5 rounded text-[11px] font-semibold bg-blue-50 dark:bg-blue-950 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900">
                  {analysis.documentType}
                </span>
              )}
            </div>
            {analysis.purpose && analysis.purpose !== "Not specified" && (
              <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 italic">
                Purpose: {analysis.purpose}
              </p>
            )}
          </div>

          <div className="flex items-center gap-2 flex-wrap">
            {/* Grounding Score */}
            <div
              className={`inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium border ${
                verificationPercent >= 80
                  ? "bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-300 border-emerald-200 dark:border-emerald-900"
                  : "bg-amber-50 dark:bg-amber-950/40 text-amber-800 dark:text-amber-300 border-amber-200 dark:border-amber-900"
              }`}
              title="Percentage of evidence quotes that strictly matched extracted document text"
            >
              <CheckCircle2 className="w-3.5 h-3.5" />
              <span>{verificationPercent}% Grounded</span>
            </div>

            {/* Model & Provider */}
            <span className="text-[11px] text-slate-400 bg-slate-100 dark:bg-slate-800 px-2 py-1 rounded">
              {analysis.llmModel || analysis.modelUsed || "llm"} &bull; {analysis.llmProvider || "v1"}
            </span>

            {/* Reanalyze Action */}
            <button
              type="button"
              onClick={handleReanalyze}
              disabled={reanalyzing}
              title="Re-run analysis pipeline"
              className="p-1.5 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors disabled:opacity-40"
            >
              <RotateCw className={`w-3.5 h-3.5 ${reanalyzing ? "animate-spin" : ""}`} />
            </button>
          </div>
        </div>

        {/* Executive vs Detailed Summary Section */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500">
              Contract Summary
            </h3>
            <div className="inline-flex rounded-md border border-slate-200 dark:border-slate-800 p-0.5 bg-slate-50 dark:bg-slate-950 text-xs">
              <button
                type="button"
                onClick={() => setSummaryMode("short")}
                className={`px-3 py-1 rounded font-medium transition-colors ${
                  summaryMode === "short"
                    ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm"
                    : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                }`}
              >
                Executive
              </button>
              <button
                type="button"
                onClick={() => setSummaryMode("detailed")}
                className={`px-3 py-1 rounded font-medium transition-colors ${
                  summaryMode === "detailed"
                    ? "bg-white dark:bg-slate-800 text-slate-900 dark:text-white shadow-sm"
                    : "text-slate-500 hover:text-slate-800 dark:hover:text-slate-200"
                }`}
              >
                Comprehensive
              </button>
            </div>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 dark:bg-slate-800/50 border border-slate-200 dark:border-slate-800 font-legal text-sm leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap select-text">
            {summaryMode === "short"
              ? analysis.shortSummary || "No executive summary available."
              : analysis.detailedSummary || analysis.shortSummary || "No comprehensive summary available."}
          </div>
        </div>
      </div>

      {/* Parties Involved */}
      <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <Users className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Identified Parties ({parties.length})
          </h3>
        </div>

        {parties.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No contracting parties identified.</p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {parties.map((p, idx) => (
              <div
                key={idx}
                className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/60 dark:bg-slate-800/40 space-y-2.5"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h4 className="text-xs font-bold text-slate-900 dark:text-white">
                      {p.name}
                    </h4>
                    <span className="text-[11px] font-medium text-blue-600 dark:text-blue-400">
                      {p.role || "Party"}
                    </span>
                  </div>
                  <ProvenanceBadge
                    provenance={p.provenance || "EXTRACTED"}
                    quoteVerified={p.quoteVerified ?? true}
                    page={p.sourcePage}
                  />
                </div>

                {p.evidenceQuote && p.evidenceQuote !== "Not specified" && (
                  <div className="text-[11px] text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-900 p-2.5 rounded border border-slate-200 dark:border-slate-800 font-mono italic">
                    <Quote className="w-3 h-3 inline mr-1 text-slate-400" />
                    &ldquo;{p.evidenceQuote}&rdquo;
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Main Conditions */}
      <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Main Conditions &amp; Pre-requisites ({mainConditions.length})
          </h3>
        </div>

        {mainConditions.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No specific conditions recorded.</p>
        ) : (
          <div className="space-y-3">
            {mainConditions.map((cond, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                  <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                    {cond.text}
                  </p>
                  <ProvenanceBadge
                    provenance={cond.provenance || "EXTRACTED"}
                    quoteVerified={cond.quoteVerified ?? true}
                    page={cond.sourcePage}
                    className="shrink-0"
                  />
                </div>

                {cond.evidenceQuote && cond.evidenceQuote !== "Not specified" && (
                  <div className="text-[11px] text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-900 p-2 rounded border border-slate-200 dark:border-slate-800 font-mono italic">
                    &ldquo;{cond.evidenceQuote}&rdquo;
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Contractual Obligations */}
      <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <FileCheck2 className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Contractual Obligations ({obligations.length})
          </h3>
        </div>

        {obligations.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No obligations recorded.</p>
        ) : (
          <div className="space-y-3">
            {obligations.map((ob, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                  <div className="space-y-1">
                    {ob.party && ob.party !== "Not specified" && (
                      <span className="text-[10px] font-semibold uppercase tracking-wider text-emerald-700 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/60 px-1.5 py-0.5 rounded border border-emerald-200 dark:border-emerald-900 inline-block">
                        {ob.party}
                      </span>
                    )}
                    <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                      {ob.text}
                    </p>
                  </div>
                  <ProvenanceBadge
                    provenance={ob.provenance || "EXTRACTED"}
                    quoteVerified={ob.quoteVerified ?? true}
                    page={ob.sourcePage}
                    className="shrink-0"
                  />
                </div>

                {ob.evidenceQuote && ob.evidenceQuote !== "Not specified" && (
                  <div className="text-[11px] text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-900 p-2 rounded border border-slate-200 dark:border-slate-800 font-mono italic">
                    &ldquo;{ob.evidenceQuote}&rdquo;
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Financial Terms */}
      <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm space-y-4">
        <div className="flex items-center gap-2">
          <DollarSign className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          <h3 className="text-sm font-bold text-slate-900 dark:text-white">
            Financial Terms &amp; Compensation ({financialTerms.length})
          </h3>
        </div>

        {financialTerms.length === 0 ? (
          <p className="text-xs text-slate-400 italic">No financial commitments or compensation terms specified.</p>
        ) : (
          <div className="space-y-3">
            {financialTerms.map((fin, idx) => (
              <div
                key={idx}
                className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-800/30 space-y-2"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                  <p className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-medium">
                    {fin.text}
                  </p>
                  <ProvenanceBadge
                    provenance={fin.provenance || "EXTRACTED"}
                    quoteVerified={fin.quoteVerified ?? true}
                    page={fin.sourcePage}
                    className="shrink-0"
                  />
                </div>

                {fin.evidenceQuote && fin.evidenceQuote !== "Not specified" && (
                  <div className="text-[11px] text-slate-600 dark:text-slate-400 bg-white dark:bg-slate-900 p-2 rounded border border-slate-200 dark:border-slate-800 font-mono italic">
                    &ldquo;{fin.evidenceQuote}&rdquo;
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
