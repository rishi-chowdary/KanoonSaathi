import React, { useState, useEffect, useMemo } from "react";
import {
  ShieldAlert,
  AlertTriangle,
  Info,
  CheckCircle2,
  ChevronDown,
  ChevronUp,
  HelpCircle,
  Scale,
  Copy,
  Check,
  Filter,
  FileText,
  RotateCcw,
  Sparkles,
} from "lucide-react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Cell,
} from "recharts";
import { getDocumentRisks } from "../../services/api";

const LEVEL_COLORS = {
  HIGH: {
    bg: "bg-red-50 dark:bg-red-950/30",
    border: "border-red-200 dark:border-red-900",
    badge: "bg-red-100 text-red-800 dark:bg-red-900/60 dark:text-red-200 border-red-200 dark:border-red-800",
    barColor: "#ef4444",
  },
  MEDIUM: {
    bg: "bg-amber-50 dark:bg-amber-950/30",
    border: "border-amber-200 dark:border-amber-900",
    badge: "bg-amber-100 text-amber-800 dark:bg-amber-900/60 dark:text-amber-200 border-amber-200 dark:border-amber-800",
    barColor: "#f59e0b",
  },
  LOW: {
    bg: "bg-blue-50 dark:bg-blue-950/30",
    border: "border-blue-200 dark:border-blue-900",
    badge: "bg-blue-100 text-blue-800 dark:bg-blue-900/60 dark:text-blue-200 border-blue-200 dark:border-blue-800",
    barColor: "#3b82f6",
  },
  INFORMATIONAL: {
    bg: "bg-slate-50 dark:bg-slate-900/40",
    border: "border-slate-200 dark:border-slate-800",
    badge: "bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700",
    barColor: "#64748b",
  },
};

const CATEGORIES = ["All", "Financial", "Legal", "Privacy", "Contractual", "Employment", "Liability"];
const LEVELS = ["ALL", "HIGH", "MEDIUM", "LOW", "INFORMATIONAL"];

export default function RisksTab({ documentId, onSelectPage = null }) {
  const [risks, setRisks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [levelFilter, setLevelFilter] = useState("ALL");

  // Expanded items
  const [expandedCards, setExpandedCards] = useState({});
  const [copiedId, setCopiedId] = useState(null);

  useEffect(() => {
    async function loadRisks() {
      try {
        setLoading(true);
        setError(null);
        const data = await getDocumentRisks(documentId);
        setRisks(data || []);
      } catch (err) {
        console.error("Failed to load risks", err);
        setError("Unable to load risk findings. Please verify analysis has completed.");
      } finally {
        setLoading(false);
      }
    }
    loadRisks();
  }, [documentId]);

  const toggleExpand = (id) => {
    setExpandedCards((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  const handleCopy = (id, text) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Filtered risks
  const filteredRisks = useMemo(() => {
    return risks.filter((r) => {
      const matchCat = categoryFilter === "All" || (r.category && r.category.toLowerCase() === categoryFilter.toLowerCase());
      const matchLevel = levelFilter === "ALL" || (r.level && r.level.toUpperCase() === levelFilter.toUpperCase());
      return matchCat && matchLevel;
    });
  }, [risks, categoryFilter, levelFilter]);

  // Chart data
  const chartData = useMemo(() => {
    const counts = { HIGH: 0, MEDIUM: 0, LOW: 0, INFORMATIONAL: 0 };
    risks.forEach((r) => {
      const lvl = (r.level || "INFORMATIONAL").toUpperCase();
      if (counts[lvl] !== undefined) counts[lvl]++;
    });
    return [
      { name: "High", level: "HIGH", count: counts.HIGH, fill: LEVEL_COLORS.HIGH.barColor },
      { name: "Medium", level: "MEDIUM", count: counts.MEDIUM, fill: LEVEL_COLORS.MEDIUM.barColor },
      { name: "Low", level: "LOW", count: counts.LOW, fill: LEVEL_COLORS.LOW.barColor },
      { name: "Info", level: "INFORMATIONAL", count: counts.INFORMATIONAL, fill: LEVEL_COLORS.INFORMATIONAL.barColor },
    ];
  }, [risks]);

  // Check if any finding has a jurisdiction caveat
  const globalJurisdictionCaveat = useMemo(() => {
    const item = risks.find((r) => r.jurisdictionCaveat);
    return item ? item.jurisdictionCaveat : null;
  }, [risks]);

  if (loading) {
    return (
      <div className="py-16 text-center text-xs text-slate-500">
        <ShieldAlert className="w-8 h-8 animate-pulse text-blue-600 mx-auto mb-2" />
        Evaluating risk findings and liability exposures...
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
      {/* Jurisdiction Caveat Alert */}
      {globalJurisdictionCaveat && (
        <div className="p-3.5 rounded-lg border border-amber-200 dark:border-amber-900/60 bg-amber-50 dark:bg-amber-950/30 flex items-start gap-3">
          <Scale className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 flex-shrink-0" />
          <div className="text-xs text-amber-800 dark:text-amber-300 leading-relaxed">
            <span className="font-semibold">Jurisdiction Caveat: </span>
            {globalJurisdictionCaveat}
          </div>
        </div>
      )}

      {/* Distribution Overview + Summary Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Metric Overview */}
        <div className="lg:col-span-1 p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
          <h3 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider">
            Risk Profile Distribution
          </h3>
          <div className="grid grid-cols-2 gap-2 text-center">
            <div className="p-2.5 rounded bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-900">
              <span className="text-lg font-bold text-red-600 dark:text-red-400">
                {chartData[0].count}
              </span>
              <p className="text-[11px] text-red-700 dark:text-red-300">High Risks</p>
            </div>
            <div className="p-2.5 rounded bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-900">
              <span className="text-lg font-bold text-amber-600 dark:text-amber-400">
                {chartData[1].count}
              </span>
              <p className="text-[11px] text-amber-700 dark:text-amber-300">Medium Risks</p>
            </div>
            <div className="p-2.5 rounded bg-blue-50 dark:bg-blue-950/30 border border-blue-200 dark:border-blue-900">
              <span className="text-lg font-bold text-blue-600 dark:text-blue-400">
                {chartData[2].count}
              </span>
              <p className="text-[11px] text-blue-700 dark:text-blue-300">Low Risks</p>
            </div>
            <div className="p-2.5 rounded bg-slate-50 dark:bg-slate-800/40 border border-slate-200 dark:border-slate-700">
              <span className="text-lg font-bold text-slate-600 dark:text-slate-300">
                {chartData[3].count}
              </span>
              <p className="text-[11px] text-slate-500">Informational</p>
            </div>
          </div>
          <p className="text-[11px] text-slate-500 italic">
            Total of {risks.length} evaluated risk items across {CATEGORIES.length - 1} legal categories.
          </p>
        </div>

        {/* Recharts Bar Chart */}
        <div className="lg:col-span-2 p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 flex flex-col justify-between">
          <h3 className="text-xs font-semibold text-slate-700 dark:text-slate-300 uppercase tracking-wider mb-2">
            Severity Frequency Breakdown
          </h3>
          <div className="h-32 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 5, right: 10, left: -25, bottom: 0 }}>
                <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="#94a3b8" />
                <YAxis allowDecimals={false} tick={{ fontSize: 11 }} stroke="#94a3b8" />
                <Tooltip
                  formatter={(value) => [`${value} finding(s)`, "Count"]}
                  contentStyle={{
                    backgroundColor: "#1e293b",
                    borderColor: "#334155",
                    fontSize: "12px",
                    color: "#f8fafc",
                    borderRadius: "6px",
                  }}
                />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {chartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <div className="text-[11px] text-slate-400 text-right mt-1">
            Rule 7 Post-Filter Active &bull; Objective Risk Assessment
          </div>
        </div>
      </div>

      {/* Filter Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 text-xs">
        {/* Category Pills */}
        <div className="flex flex-wrap items-center gap-1.5">
          <span className="text-slate-500 font-medium mr-1 flex items-center gap-1">
            <Filter className="w-3.5 h-3.5" /> Category:
          </span>
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              type="button"
              onClick={() => setCategoryFilter(cat)}
              className={`px-2.5 py-1 rounded text-xs transition-colors ${
                categoryFilter === cat
                  ? "bg-blue-600 text-white font-medium shadow-sm"
                  : "bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Level Pills */}
        <div className="flex items-center gap-1.5">
          <span className="text-slate-500 font-medium mr-1">Level:</span>
          {LEVELS.map((lvl) => (
            <button
              key={lvl}
              type="button"
              onClick={() => setLevelFilter(lvl)}
              className={`px-2 py-0.5 rounded text-[11px] font-medium transition-colors ${
                levelFilter === lvl
                  ? "bg-slate-800 dark:bg-slate-200 text-white dark:text-slate-900"
                  : "bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:bg-slate-100"
              }`}
            >
              {lvl}
            </button>
          ))}
        </div>
      </div>

      {/* Risk Cards List */}
      {filteredRisks.length === 0 ? (
        <div className="p-12 text-center rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs text-slate-500">
          No risk findings match the selected filters.
        </div>
      ) : (
        <div className="space-y-4">
          {filteredRisks.map((risk) => {
            const colors = LEVEL_COLORS[risk.level] || LEVEL_COLORS.INFORMATIONAL;
            const isExpanded = !!expandedCards[risk.id];
            const questions = risk.suggestedQuestions || [];

            return (
              <div
                key={risk.id}
                className={`rounded-lg border transition-all ${colors.border} ${colors.bg} p-5 space-y-3.5 shadow-sm`}
              >
                {/* Header: Title, Category, Level, Provenance */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span
                      className={`px-2 py-0.5 rounded text-[11px] font-semibold tracking-wide border uppercase ${colors.badge}`}
                    >
                      {risk.level}
                    </span>
                    <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-slate-700 dark:text-slate-300">
                      {risk.category}
                    </span>
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                      {risk.title}
                    </h3>
                  </div>

                  <div className="flex items-center gap-2 text-xs">
                    {risk.quoteVerified ? (
                      <span className="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-700 dark:text-emerald-400">
                        <CheckCircle2 className="w-3.5 h-3.5" /> Quote Verified
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-[11px] text-amber-700 dark:text-amber-400">
                        <AlertTriangle className="w-3.5 h-3.5" /> Unverified Quote
                      </span>
                    )}

                    <span className="text-slate-400">&bull;</span>
                    <button
                      type="button"
                      onClick={() => onSelectPage && onSelectPage(risk.sourcePage)}
                      className="text-[11px] text-blue-600 dark:text-blue-400 hover:underline inline-flex items-center gap-1"
                    >
                      <FileText className="w-3 h-3" /> Page {risk.sourcePage}
                    </button>
                  </div>
                </div>

                {/* Explanation */}
                <div className="text-xs text-slate-800 dark:text-slate-200 leading-relaxed font-sans">
                  {risk.explanation}
                </div>

                {/* Impact Details Grid: Why it Matters & Possible Consequences */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1 text-xs">
                  <div className="p-3 rounded bg-white/70 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 space-y-1">
                    <span className="font-semibold text-slate-800 dark:text-slate-200 block text-[11px] uppercase tracking-wide">
                      Why It Matters
                    </span>
                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                      {risk.whyItMatters}
                    </p>
                  </div>

                  <div className="p-3 rounded bg-white/70 dark:bg-slate-900/60 border border-slate-200/80 dark:border-slate-800 space-y-1">
                    <span className="font-semibold text-rose-800 dark:text-rose-300 block text-[11px] uppercase tracking-wide">
                      Possible Consequences
                    </span>
                    <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                      {risk.possibleConsequences}
                    </p>
                  </div>
                </div>

                {/* Verbatim Original Clause / Evidence Quote */}
                <div className="pt-1">
                  <div className="p-2.5 rounded bg-slate-100/80 dark:bg-slate-950/60 border border-slate-200 dark:border-slate-800 font-mono text-[11px] text-slate-800 dark:text-slate-300 leading-relaxed relative group">
                    <span className="text-[10px] uppercase font-sans font-bold text-slate-500 block mb-1">
                      Evidence Quote (Page {risk.sourcePage}):
                    </span>
                    &ldquo;{risk.evidenceQuote || risk.originalClause}&rdquo;

                    <button
                      type="button"
                      onClick={() => handleCopy(risk.id, risk.evidenceQuote || risk.originalClause)}
                      className="absolute top-2 right-2 p-1 rounded bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 opacity-0 group-hover:opacity-100 transition-opacity"
                      title="Copy quote"
                    >
                      {copiedId === risk.id ? (
                        <Check className="w-3 h-3 text-emerald-600" />
                      ) : (
                        <Copy className="w-3 h-3 text-slate-500" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Suggested Questions Section */}
                {questions.length > 0 && (
                  <div className="border-t border-slate-200/70 dark:border-slate-800 pt-3">
                    <button
                      type="button"
                      onClick={() => toggleExpand(risk.id)}
                      className="flex items-center justify-between w-full text-xs font-semibold text-slate-700 dark:text-slate-300 hover:text-blue-600 dark:hover:text-blue-400"
                    >
                      <span className="flex items-center gap-1.5">
                        <HelpCircle className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
                        Suggested Questions to Ask & Negotiate ({questions.length})
                      </span>
                      {isExpanded ? (
                        <ChevronUp className="w-4 h-4 text-slate-400" />
                      ) : (
                        <ChevronDown className="w-4 h-4 text-slate-400" />
                      )}
                    </button>

                    {isExpanded && (
                      <ul className="mt-2.5 space-y-1.5 pl-5 list-disc text-xs text-slate-700 dark:text-slate-300">
                        {questions.map((q, idx) => (
                          <li key={idx} className="leading-relaxed">
                            {q}
                          </li>
                        ))}
                      </ul>
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

