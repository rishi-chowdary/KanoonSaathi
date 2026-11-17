import React, { useState, useEffect, useMemo } from "react";
import {
  HelpCircle,
  AlertTriangle,
  Info,
  Scale,
  Copy,
  Check,
  ChevronDown,
  ChevronUp,
  FileQuestion,
  Filter,
} from "lucide-react";
import { getDocumentMissingProvisions } from "../../services/api";

const RISK_BADGES = {
  HIGH: "bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-200 border-red-200 dark:border-red-800",
  MEDIUM: "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200 border-amber-200 dark:border-amber-800",
  LOW: "bg-blue-100 text-blue-800 dark:bg-blue-900/60 dark:text-blue-200 border-blue-200 dark:border-blue-800",
  INFORMATIONAL: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700",
};

export default function MissingProvisionsTab({ documentId }) {
  const [warnings, setWarnings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [copiedId, setCopiedId] = useState(null);
  const [expandedExamples, setExpandedExamples] = useState({});

  useEffect(() => {
    async function loadMissing() {
      try {
        setLoading(true);
        setError(null);
        const data = await getDocumentMissingProvisions(documentId);
        setWarnings(data || []);
      } catch (err) {
        console.error("Failed to load missing provisions", err);
        setError("Unable to load missing provisions checklist. Please verify document status.");
      } finally {
        setLoading(false);
      }
    }
    loadMissing();
  }, [documentId]);

  const toggleExample = (id) => {
    setExpandedExamples((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const categories = useMemo(() => {
    const set = new Set(["All"]);
    warnings.forEach((w) => {
      if (w.category) set.add(w.category);
    });
    return Array.from(set);
  }, [warnings]);

  const filteredWarnings = useMemo(() => {
    if (categoryFilter === "All") return warnings;
    return warnings.filter((w) => w.category === categoryFilter);
  }, [warnings, categoryFilter]);

  if (loading) {
    return (
      <div className="py-16 text-center text-xs text-slate-500">
        <FileQuestion className="w-8 h-8 animate-pulse text-blue-600 mx-auto mb-2" />
        Auditing document against standard contract checklists and expected provisions...
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 rounded-lg border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 text-xs text-rose-700 dark:text-rose-300">
        <AlertTriangle className="w-5 h-5 mb-2 text-rose-500" />
        <strong>Error:</strong> {error}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Mandatory Legal Disclaimer Banner */}
      <div className="p-4 rounded-lg border border-blue-200 dark:border-blue-900/60 bg-blue-50/70 dark:bg-blue-950/30 flex items-start gap-3">
        <Scale className="w-5 h-5 text-blue-700 dark:text-blue-400 mt-0.5 flex-shrink-0" />
        <div className="space-y-1 text-xs text-blue-900 dark:text-blue-200">
          <span className="font-semibold block uppercase tracking-wider text-[11px]">
            Statutory Legal Notice & Rule 7 Disclosure
          </span>
          <p className="leading-relaxed">
            LexiLegal AI provides automated structural review. All items identified below are categorized strictly as{" "}
            <strong className="underline decoration-blue-400 font-bold">&ldquo;Possible omission&rdquo;</strong> based on standard commercial norms and document checklists. They do not constitute formal legal counsel or guarantees of contractual deficiency.
          </p>
        </div>
      </div>

      {/* Filter Toolbar */}
      {categories.length > 2 && (
        <div className="flex items-center gap-2 p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs">
          <span className="text-slate-500 font-medium flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          <div className="flex flex-wrap gap-1.5">
            {categories.map((cat) => (
              <button
                key={cat}
                type="button"
                onClick={() => setCategoryFilter(cat)}
                className={`px-2.5 py-1 rounded text-xs transition-colors ${
                  categoryFilter === cat
                    ? "bg-blue-600 text-white font-medium"
                    : "bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700"
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Missing Provisions List */}
      {filteredWarnings.length === 0 ? (
        <div className="p-12 text-center rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs text-slate-500">
          No missing provisions detected for this category. The document conforms to typical standard clauses.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredWarnings.map((warning) => {
            const riskClass = RISK_BADGES[warning.riskLevel] || RISK_BADGES.INFORMATIONAL;
            const isExampleOpen = !!expandedExamples[warning.id];

            return (
              <div
                key={warning.id}
                className="p-5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3.5 shadow-sm hover:border-slate-300 dark:hover:border-slate-700 transition-colors"
              >
                {/* Header: Label, Risk, Category, Title */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 dark:border-slate-800 pb-2.5">
                  <div className="flex items-center gap-2 flex-wrap">
                    {/* Strict "Possible omission" badge */}
                    <span className="px-2 py-0.5 rounded text-[11px] font-semibold tracking-wide bg-indigo-50 dark:bg-indigo-950/50 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-indigo-800 uppercase">
                      {warning.label || "Possible omission"}
                    </span>

                    <span
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold tracking-wide border uppercase ${riskClass}`}
                    >
                      {warning.riskLevel}
                    </span>

                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300">
                      {warning.category}
                    </span>

                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                      {warning.clauseName}
                    </h3>
                  </div>
                </div>

                {/* Why It Matters */}
                <div className="space-y-1">
                  <span className="text-[11px] font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider block">
                    Why It Matters
                  </span>
                  <p className="text-xs text-slate-700 dark:text-slate-300 leading-relaxed font-sans">
                    {warning.whyItMatters}
                  </p>
                </div>

                {/* Typical Commercial Provision Language */}
                {warning.typicalProvision && (
                  <div className="border-t border-slate-100 dark:border-slate-800 pt-2.5">
                    <button
                      type="button"
                      onClick={() => toggleExample(warning.id)}
                      className="flex items-center justify-between w-full text-xs font-medium text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400"
                    >
                      <span className="flex items-center gap-1.5">
                        <Info className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                        View Typical Commercial Provision Example
                      </span>
                      {isExampleOpen ? (
                        <ChevronUp className="w-4 h-4" />
                      ) : (
                        <ChevronDown className="w-4 h-4" />
                      )}
                    </button>

                    {isExampleOpen && (
                      <div className="mt-2 p-3 rounded bg-slate-50 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 font-mono text-[11px] text-slate-800 dark:text-slate-300 leading-relaxed relative group">
                        <span className="text-[10px] font-sans font-bold uppercase text-slate-400 block mb-1">
                          Illustrative Model Language:
                        </span>
                        &ldquo;{warning.typicalProvision}&rdquo;

                        <button
                          type="button"
                          onClick={() => handleCopy(warning.id, warning.typicalProvision)}
                          className="absolute top-2 right-2 p-1 rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 opacity-0 group-hover:opacity-100 transition-opacity"
                          title="Copy example language"
                        >
                          {copiedId === warning.id ? (
                            <Check className="w-3 h-3 text-emerald-600" />
                          ) : (
                            <Copy className="w-3 h-3 text-slate-500" />
                          )}
                        </button>
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

