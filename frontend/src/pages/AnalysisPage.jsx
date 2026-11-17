import React, { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import api from "../services/api";
import SummaryTab from "../components/analysis/SummaryTab";
import ClausesTab from "../components/clauses/ClausesTab";
import RisksTab from "../components/risks/RisksTab";
import KeyInfoTab from "../components/keyinfo/KeyInfoTab";
import MissingProvisionsTab from "../components/missing/MissingProvisionsTab";
import ChatTab from "../components/chat/ChatTab";
import ReportTab from "../components/report/ReportTab";
import { downloadReportPdf } from "../services/api";
import {
  FileText,
  ShieldAlert,
  Key,
  HelpCircle,
  MessageSquare,
  Download,
  Loader2,
  AlertCircle,
  AlertTriangle,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Calendar,
  Layers,
} from "lucide-react";

export default function AnalysisPage() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState("preview");
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloadingReport, setDownloadingReport] = useState(false);

  // Text preview state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageText, setPageText] = useState("");
  const [loadingText, setLoadingText] = useState(false);

  const isFinished = document?.status === "COMPLETED" || document?.status === "COMPLETED_WITH_WARNINGS";

  const handleHeaderDownloadReport = async () => {
    if (!document || !isFinished) return;
    try {
      setDownloadingReport(true);
      const baseName = document.originalFilename ? document.originalFilename.replace(/\.[^/.]+$/, "") : "contract";
      await downloadReportPdf(id, `lexilegal_${baseName}_report.pdf`);
    } catch (err) {
      console.error("Failed to download report:", err);
    } finally {
      setDownloadingReport(false);
    }
  };

  useEffect(() => {
    let timer = null;

    async function loadDocument() {
      try {
        const resp = await api.get(`/documents/${id}`);
        setDocument(resp.data);
        setError(null);

        // If still extracting or analyzing, poll status
        if (
          resp.data.status === "EXTRACTING" ||
          resp.data.status === "UPLOADED" ||
          resp.data.status === "ANALYZING"
        ) {
          timer = setTimeout(loadDocument, 2000);
        }
      } catch (err) {
        setError(err.response?.data?.message || "Failed to load document.");
      } finally {
        setLoading(false);
      }
    }

    loadDocument();
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [id]);

  useEffect(() => {
    async function loadPageText() {
      if (
        !id ||
        !document ||
        document.status === "EXTRACTING" ||
        document.status === "UPLOADED" ||
        document.status === "FAILED"
      ) {
        return;
      }
      try {
        setLoadingText(true);
        const resp = await api.get(`/documents/${id}/text`, {
          params: { page: currentPage },
        });
        setPageText(resp.data.text || "(No text content found on this page)");
      } catch (err) {
        setPageText("(Could not load text for this page)");
      } finally {
        setLoadingText(false);
      }
    }

    loadPageText();
  }, [id, currentPage, document?.status]);

  const totalPages = document?.pageCount || 1;

  const tabs = [
    { id: "preview", label: "Document Text", icon: BookOpen },
    { id: "summary", label: "Summary", icon: FileText },
    { id: "clauses", label: "Clauses", icon: Layers },
    { id: "risks", label: "Risks", icon: ShieldAlert },
    { id: "key-info", label: "Key Information", icon: Key },
    { id: "missing", label: "Missing Clauses", icon: HelpCircle },
    { id: "chat", label: "Document Chat", icon: MessageSquare },
    { id: "report", label: "Report Dossier", icon: Download },
  ];

  if (loading) {
    return (
      <div className="py-20 text-center text-slate-500 text-xs">
        <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
        Loading document workspace...
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto py-12 space-y-4 text-center">
        <AlertCircle className="w-10 h-10 text-rose-500 mx-auto" />
        <h2 className="text-base font-semibold text-slate-900 dark:text-white">Document Not Available</h2>
        <p className="text-xs text-slate-500">{error}</p>
        <Link
          to="/history"
          className="inline-block text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
        >
          &larr; Back to Document History
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Document Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800 gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
              {document.originalFilename}
            </h1>
            <span className="px-2 py-0.5 rounded text-[11px] font-medium uppercase bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300">
              {document.fileType}
            </span>
          </div>
          <div className="flex items-center gap-3 text-xs text-slate-500 mt-1">
            <span>Pages: {document.pageCount || 1}</span>
            <span>&bull;</span>
            <span>Status: {document.status}</span>
            <span>&bull;</span>
            <span className="flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5" />
              {new Date(document.createdAt).toLocaleDateString()}
            </span>
          </div>
        </div>

        <button
          type="button"
          onClick={handleHeaderDownloadReport}
          disabled={!isFinished || downloadingReport}
          className={`inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded border transition-colors ${
            !isFinished
              ? "border-slate-200 dark:border-slate-800 text-slate-400 cursor-not-allowed"
              : downloadingReport
              ? "border-blue-500 bg-blue-50 text-blue-600 dark:bg-blue-950/40 dark:text-blue-300"
              : "border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-700 dark:text-slate-300 shadow-sm"
          }`}
          title={
            isFinished
              ? "Download 10-section PDF report"
              : "Report will be available once analysis is completed"
          }
        >
          {downloadingReport ? (
            <Loader2 className="w-3.5 h-3.5 animate-spin text-blue-600" />
          ) : (
            <Download className="w-3.5 h-3.5" />
          )}
          {downloadingReport ? "Generating..." : "Download Report"}
        </button>
      </div>

      {document?.status === "COMPLETED_WITH_WARNINGS" && (
        <div className="mb-4 bg-amber-50 dark:bg-amber-950/30 border border-amber-200 dark:border-amber-800 rounded p-3 text-xs text-amber-800 dark:text-amber-200 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 mt-0.5 shrink-0" />
          <div>
            <span className="font-semibold">Analysis completed with warnings:</span>{" "}
            {document.failureReason || "Some secondary analyzers encountered issues, but the core analysis and clauses are available."}
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="flex border-b border-slate-200 dark:border-slate-800 gap-1 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              type="button"
              className={`flex items-center gap-2 px-3.5 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
                active
                  ? "border-blue-600 text-blue-600 dark:text-blue-400 font-semibold"
                  : "border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <Icon className="w-3.5 h-3.5" />
              {tab.label}
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      {activeTab === "summary" && (
        <SummaryTab
          documentId={id}
          documentStatus={document.status}
          onStatusChange={(newStatus) =>
            setDocument((prev) => (prev ? { ...prev, status: newStatus } : prev))
          }
        />
      )}

      {activeTab === "clauses" && (
        <ClausesTab
          documentId={id}
          onSelectPage={(page) => {
            setCurrentPage(page);
            setActiveTab("preview");
          }}
        />
      )}

      {activeTab === "risks" && (
        <RisksTab
          documentId={id}
          onSelectPage={(page) => {
            setCurrentPage(page);
            setActiveTab("preview");
          }}
        />
      )}

      {activeTab === "key-info" && (
        <KeyInfoTab
          documentId={id}
          onSelectPage={(page) => {
            setCurrentPage(page);
            setActiveTab("preview");
          }}
        />
      )}

      {activeTab === "missing" && (
        <MissingProvisionsTab
          documentId={id}
        />
      )}

      {activeTab === "chat" && (
        <ChatTab
          documentId={id}
          onSelectPage={(page) => {
            setCurrentPage(page);
            setActiveTab("preview");
          }}
        />
      )}

      {activeTab === "report" && (
        <ReportTab
          documentId={id}
          document={document}
        />
      )}

      {activeTab === "preview" && (
        <div className="space-y-4">
          {document.status === "EXTRACTING" ? (
            <div className="p-12 text-center rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs text-slate-500">
              <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
              Extracting document pages and section references...
            </div>
          ) : document.status === "FAILED" ? (
            <div className="p-6 rounded-lg border border-rose-200 dark:border-rose-900 bg-rose-50 dark:bg-rose-950/40 text-xs text-rose-700 dark:text-rose-300">
              <strong>Extraction Error:</strong> {document.failureReason || "Could not extract text from document."}
            </div>
          ) : (
            <div className="border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 overflow-hidden shadow-sm">
              {/* Page Navigator Toolbar */}
              <div className="px-4 py-3 bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs">
                <span className="font-medium text-slate-700 dark:text-slate-300">
                  Page {currentPage} of {totalPages}
                </span>

                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                    disabled={currentPage <= 1}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-slate-300 dark:border-slate-700 disabled:opacity-40 text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-800"
                  >
                    <ChevronLeft className="w-3.5 h-3.5" /> Prev
                  </button>
                  <button
                    type="button"
                    onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                    disabled={currentPage >= totalPages}
                    className="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-slate-300 dark:border-slate-700 disabled:opacity-40 text-slate-700 dark:text-slate-300 hover:bg-white dark:hover:bg-slate-800"
                  >
                    Next <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {/* Text Preview Body */}
              <div className="p-6 min-h-[360px] font-legal text-sm leading-relaxed text-slate-800 dark:text-slate-200 whitespace-pre-wrap select-text">
                {loadingText ? (
                  <div className="py-12 text-center text-xs text-slate-400">Loading page text...</div>
                ) : (
                  pageText
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab !== "preview" &&
        activeTab !== "summary" &&
        activeTab !== "clauses" &&
        activeTab !== "risks" &&
        activeTab !== "key-info" &&
        activeTab !== "missing" &&
        activeTab !== "chat" && (
        <div className="p-8 border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 text-xs text-slate-500 space-y-2">
          <p className="font-medium text-slate-700 dark:text-slate-300">
            {activeTab.toUpperCase()} Module
          </p>
          <p>
            Document text has been extracted and executive summary analyzed. Structured extraction for {activeTab} will be activated in upcoming phases.
          </p>
          <button
            type="button"
            onClick={() => setActiveTab("summary")}
            className="text-blue-600 dark:text-blue-400 hover:underline pt-2 inline-block"
          >
            &larr; Switch to Summary Analysis
          </button>
        </div>
      )}
    </div>
  );
}
