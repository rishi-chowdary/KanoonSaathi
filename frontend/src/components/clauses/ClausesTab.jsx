import React, { useState, useEffect, useCallback } from "react";
import {
  Search,
  Filter,
  Layers,
  AlertCircle,
  Loader2,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  X,
  FileText,
  RotateCcw,
} from "lucide-react";
import api from "../../services/api";
import ClauseCard from "./ClauseCard";

const CATEGORIES = [
  "All",
  "Confidentiality",
  "Termination",
  "Intellectual Property",
  "Liability and Indemnification",
  "Dispute Resolution",
  "Governing Law",
  "Payment Terms",
  "Representations and Warranties",
  "Non-Compete and Non-Solicitation",
  "Force Majeure",
  "Assignment",
  "Severability",
  "Amendment",
  "Notices",
  "Term and Renewal",
  "Data Protection and Privacy",
  "Insurance",
  "Other",
];

const IMPORTANCE_LEVELS = [
  { id: "ALL", label: "All Importance" },
  { id: "HIGH", label: "High" },
  { id: "MEDIUM", label: "Medium" },
  { id: "LOW", label: "Low" },
];

export default function ClausesTab({ documentId, onSelectPage = null }) {
  const [clauses, setClauses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [categoryFilter, setCategoryFilter] = useState("All");
  const [importanceFilter, setImportanceFilter] = useState("ALL");
  const [searchInput, setSearchInput] = useState("");
  const [activeSearch, setActiveSearch] = useState("");
  const [globalMode, setGlobalMode] = useState("simple");

  // Pagination
  const [page, setPage] = useState(0);
  const [pageSize] = useState(10);
  const [totalPages, setTotalPages] = useState(0);
  const [totalElements, setTotalElements] = useState(0);

  // Side panel for page inspection
  const [sidePanelPage, setSidePanelPage] = useState(null);
  const [sidePanelText, setSidePanelText] = useState("");
  const [sidePanelLoading, setSidePanelLoading] = useState(false);

  // Load clauses
  const loadClauses = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const params = {
        page,
        size: pageSize,
      };
      if (categoryFilter && categoryFilter !== "All") {
        params.category = categoryFilter;
      }
      if (importanceFilter && importanceFilter !== "ALL") {
        params.importance = importanceFilter;
      }
      if (activeSearch && activeSearch.trim().length > 0) {
        params.search = activeSearch.trim();
      }

      const res = await api.get(`/documents/${documentId}/clauses`, { params });
      setClauses(res.data.content || []);
      setTotalPages(res.data.totalPages || 0);
      setTotalElements(res.data.totalElements || 0);
    } catch (err) {
      console.error("Failed to load clauses", err);
      setError("Unable to load extracted clauses. Please ensure analysis is completed.");
    } finally {
      setLoading(false);
    }
  }, [documentId, page, pageSize, categoryFilter, importanceFilter, activeSearch]);

  useEffect(() => {
    loadClauses();
  }, [loadClauses]);

  // Load page text for side panel drawer
  useEffect(() => {
    if (sidePanelPage === null) {
      setSidePanelText("");
      return;
    }

    async function fetchPageText() {
      try {
        setSidePanelLoading(true);
        const res = await api.get(`/documents/${documentId}/text`, {
          params: { page: sidePanelPage },
        });
        setSidePanelText(res.data.text || "(No text content found on this page)");
      } catch (err) {
        setSidePanelText("(Could not load text for this page)");
      } finally {
        setSidePanelLoading(false);
      }
    }

    fetchPageText();
  }, [documentId, sidePanelPage]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    setActiveSearch(searchInput);
  };

  const handleResetFilters = () => {
    setCategoryFilter("All");
    setImportanceFilter("ALL");
    setSearchInput("");
    setActiveSearch("");
    setPage(0);
  };

  const hasActiveFilters =
    categoryFilter !== "All" ||
    importanceFilter !== "ALL" ||
    activeSearch.trim().length > 0;

  return (
    <div className="space-y-6">
      {/* Top Filter and Configuration Bar */}
      <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-3">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          {/* Search form */}
          <form
            onSubmit={handleSearchSubmit}
            className="flex-1 max-w-md relative flex items-center"
          >
            <Search className="w-4 h-4 absolute left-3 text-slate-400" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Search clauses by keyword or title..."
              className="w-full pl-9 pr-8 py-1.5 text-xs rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-200 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
            {searchInput && (
              <button
                type="button"
                onClick={() => {
                  setSearchInput("");
                  setActiveSearch("");
                  setPage(0);
                }}
                className="absolute right-2.5 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            )}
          </form>

          {/* Global Explanation Mode Selector */}
          <div className="flex items-center gap-2 self-start md:self-auto">
            <span className="text-[11px] font-medium text-slate-500 dark:text-slate-400">
              Explanation:
            </span>
            <div className="inline-flex p-0.5 rounded border border-slate-200 dark:border-slate-800 bg-slate-100/80 dark:bg-slate-800 text-xs">
              <button
                type="button"
                onClick={() => setGlobalMode("simple")}
                className={`px-3 py-1 rounded font-medium transition-colors ${
                  globalMode === "simple"
                    ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                Simple English
              </button>
              <button
                type="button"
                onClick={() => setGlobalMode("detailed")}
                className={`px-3 py-1 rounded font-medium transition-colors ${
                  globalMode === "detailed"
                    ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                Detailed
              </button>
              <button
                type="button"
                onClick={() => setGlobalMode("professional")}
                className={`px-3 py-1 rounded font-medium transition-colors ${
                  globalMode === "professional"
                    ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-xs"
                    : "text-slate-600 dark:text-slate-400 hover:text-slate-900"
                }`}
              >
                Professional
              </button>
            </div>
          </div>
        </div>

        {/* Dropdowns Row */}
        <div className="flex items-center gap-3 flex-wrap pt-1 border-t border-slate-100 dark:border-slate-800 text-xs">
          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
              <Filter className="w-3 h-3 text-slate-400" /> Category:
            </span>
            <select
              value={categoryFilter}
              onChange={(e) => {
                setCategoryFilter(e.target.value);
                setPage(0);
              }}
              className="py-1 px-2.5 rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat === "All" ? "All Categories" : cat}
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] text-slate-500 font-medium">Importance:</span>
            <select
              value={importanceFilter}
              onChange={(e) => {
                setImportanceFilter(e.target.value);
                setPage(0);
              }}
              className="py-1 px-2.5 rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-950 text-slate-800 dark:text-slate-200 text-xs focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              {IMPORTANCE_LEVELS.map((lvl) => (
                <option key={lvl.id} value={lvl.id}>
                  {lvl.label}
                </option>
              ))}
            </select>
          </div>

          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleResetFilters}
              className="inline-flex items-center gap-1 text-[11px] text-blue-600 dark:text-blue-400 hover:underline ml-auto"
            >
              <RotateCcw className="w-3 h-3" />
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* Status & Counts Header */}
      <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 px-1">
        <span>
          Showing <strong className="text-slate-800 dark:text-slate-200">{clauses.length}</strong> of{" "}
          <strong className="text-slate-800 dark:text-slate-200">{totalElements}</strong> extracted clause(s)
          {categoryFilter !== "All" && ` in ${categoryFilter}`}
        </span>

        {totalPages > 1 && (
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage((p) => Math.max(0, p - 1))}
              disabled={page === 0}
              className="p-1 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="text-[11px]">
              Page {page + 1} of {totalPages}
            </span>
            <button
              type="button"
              onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
              disabled={page >= totalPages - 1}
              className="p-1 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>

      {/* Loading Skeletons */}
      {loading && (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              className="p-5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 animate-pulse space-y-3"
            >
              <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/3" />
              <div className="h-14 bg-slate-100 dark:bg-slate-800/60 rounded" />
              <div className="h-4 bg-slate-200 dark:bg-slate-800 rounded w-1/4" />
            </div>
          ))}
        </div>
      )}

      {/* Error state */}
      {!loading && error && (
        <div className="p-6 rounded-lg border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 text-xs text-rose-700 dark:text-rose-300 flex items-start gap-3">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <div className="space-y-1">
            <p className="font-semibold">{error}</p>
            <p>Ensure the document analysis has finished processing.</p>
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && clauses.length === 0 && (
        <div className="py-16 text-center border border-dashed border-slate-200 dark:border-slate-800 rounded-lg bg-white/50 dark:bg-slate-900/50 space-y-3">
          <Layers className="w-10 h-10 text-slate-400 mx-auto" />
          <h3 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
            No Clauses Found
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {hasActiveFilters
              ? "No clauses matched your active filter criteria. Try clearing filters or search terms."
              : "No specific legal clauses were extracted from this document."}
          </p>
          {hasActiveFilters && (
            <button
              type="button"
              onClick={handleResetFilters}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded border border-slate-200 dark:border-slate-800 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
            >
              <RotateCcw className="w-3 h-3" /> Clear Filters
            </button>
          )}
        </div>
      )}

      {/* Clauses List */}
      {!loading && !error && clauses.length > 0 && (
        <div className="space-y-4">
          {clauses.map((clause) => (
            <ClauseCard
              key={clause.id}
              clause={clause}
              globalMode={globalMode}
              onViewPage={(pageNum) => setSidePanelPage(pageNum)}
            />
          ))}
        </div>
      )}

      {/* Pagination Footer */}
      {!loading && totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4 border-t border-slate-200 dark:border-slate-800 text-xs">
          <button
            type="button"
            onClick={() => setPage((p) => Math.max(0, p - 1))}
            disabled={page === 0}
            className="px-3 py-1.5 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
          >
            Previous
          </button>
          <span className="text-slate-500 px-2">
            Page {page + 1} of {totalPages}
          </span>
          <button
            type="button"
            onClick={() => setPage((p) => Math.min(totalPages - 1, p + 1))}
            disabled={page >= totalPages - 1}
            className="px-3 py-1.5 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-40 hover:bg-slate-100 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300"
          >
            Next
          </button>
        </div>
      )}

      {/* Side Panel Drawer for Page Inspection */}
      {sidePanelPage !== null && (
        <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-[480px] bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl flex flex-col">
          {/* Drawer Header */}
          <div className="px-5 py-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <BookOpen className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <h3 className="text-sm font-semibold text-slate-900 dark:text-white">
                Page {sidePanelPage} Text
              </h3>
            </div>

            <div className="flex items-center gap-2">
              {onSelectPage && (
                <button
                  type="button"
                  onClick={() => {
                    onSelectPage(sidePanelPage);
                    setSidePanelPage(null);
                  }}
                  className="px-2.5 py-1 text-[11px] font-medium rounded border border-slate-200 dark:border-slate-800 text-blue-600 dark:text-blue-400 hover:bg-slate-50 dark:hover:bg-slate-800"
                >
                  Open in Document Viewer
                </button>
              )}
              <button
                type="button"
                onClick={() => setSidePanelPage(null)}
                className="p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Drawer Body */}
          <div className="p-5 flex-1 overflow-y-auto select-text font-legal text-xs leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap">
            {sidePanelLoading ? (
              <div className="py-20 text-center text-slate-400 text-xs">
                <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2 text-blue-600" />
                Loading text for page {sidePanelPage}...
              </div>
            ) : (
              sidePanelText
            )}
          </div>
        </div>
      )}
    </div>
  );
}
