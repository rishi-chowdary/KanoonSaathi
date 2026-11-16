import React, { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "../services/api";
import {
  FolderOpen,
  Search,
  Filter,
  Trash2,
  FileText,
  ExternalLink,
  Loader2,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";

export default function HistoryPage() {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("ALL");
  const [page, setPage] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [totalElements, setTotalElements] = useState(0);
  const [deletingId, setDeletingId] = useState(null);

  const fetchDocuments = async (p = 0, q = search, st = statusFilter) => {
    try {
      setLoading(true);
      const params = { page: p, size: 10 };
      if (q.trim()) params.search = q.trim();
      if (st && st !== "ALL") params.status = st;

      const resp = await api.get("/documents", { params });
      setDocuments(resp.data.content || []);
      setPage(resp.data.page);
      setTotalPages(resp.data.totalPages);
      setTotalElements(resp.data.totalElements);
    } catch (err) {
      console.error("Failed to load documents", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments(0, search, statusFilter);
  }, [statusFilter]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchDocuments(0, search, statusFilter);
  };

  const handleDelete = async (id, name) => {
    if (!window.confirm(`Are you sure you want to delete "${name}"? This will permanently remove its file and all analysis data.`)) {
      return;
    }
    try {
      setDeletingId(id);
      await api.delete(`/documents/${id}`);
      fetchDocuments(page, search, statusFilter);
    } catch (err) {
      alert("Failed to delete document: " + (err.response?.data?.message || err.message));
    } finally {
      setDeletingId(null);
    }
  };

  const formatFileSize = (bytes) => {
    if (!bytes) return "0 KB";
    if (bytes >= 1024 * 1024) return (bytes / (1024 * 1024)).toFixed(1) + " MB";
    return (bytes / 1024).toFixed(1) + " KB";
  };

  const formatDate = (isoString) => {
    if (!isoString) return "-";
    return new Date(isoString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case "EXTRACTED":
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-100 text-emerald-800 dark:bg-emerald-950/60 dark:text-emerald-300">
            Extracted
          </span>
        );
      case "EXTRACTING":
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-amber-100 text-amber-800 dark:bg-amber-950/60 dark:text-amber-300 animate-pulse">
            Extracting...
          </span>
        );
      case "FAILED":
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-rose-100 text-rose-800 dark:bg-rose-950/60 dark:text-rose-300">
            Failed
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Document History</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Vault of all legal agreements processed under your account ({totalElements} total).
          </p>
        </div>

        <Link
          to="/upload"
          className="inline-flex items-center gap-2 px-3.5 py-2 text-xs font-medium rounded bg-blue-600 hover:bg-blue-700 text-white transition-colors self-start sm:self-auto"
        >
          <FileText className="w-4 h-4" /> Upload Document
        </Link>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <form onSubmit={handleSearchSubmit} className="flex-1 relative">
          <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search documents by filename..."
            className="w-full pl-9 pr-3 py-2 text-xs rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none focus:ring-1 focus:ring-blue-600"
          />
        </form>

        <div className="flex items-center gap-2">
          <Filter className="w-3.5 h-3.5 text-slate-500" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 text-xs rounded border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 text-slate-900 dark:text-white focus:outline-none"
          >
            <option value="ALL">All Statuses</option>
            <option value="EXTRACTED">Extracted</option>
            <option value="EXTRACTING">Extracting</option>
            <option value="FAILED">Failed</option>
            <option value="UPLOADED">Uploaded</option>
          </select>
        </div>
      </div>

      {/* Documents Table */}
      {loading ? (
        <div className="p-12 text-center text-slate-500 text-xs">
          <Loader2 className="w-6 h-6 animate-spin mx-auto mb-2 text-blue-600" />
          Loading document vault...
        </div>
      ) : documents.length === 0 ? (
        <div className="border border-slate-200 dark:border-slate-800 rounded-lg p-10 bg-white dark:bg-slate-900 text-center space-y-3">
          <FolderOpen className="w-8 h-8 mx-auto text-slate-400" />
          <p className="text-sm font-medium text-slate-700 dark:text-slate-300">
            {search || statusFilter !== "ALL" ? "No matching documents found." : "No documents uploaded yet."}
          </p>
          <p className="text-xs text-slate-500">
            {search || statusFilter !== "ALL"
              ? "Try adjusting your search terms or filters."
              : "Upload a contract or agreement to extract clauses and view text."}
          </p>
          <Link
            to="/upload"
            className="inline-block text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline pt-2"
          >
            Upload a document &rarr;
          </Link>
        </div>
      ) : (
        <div className="border border-slate-200 dark:border-slate-800 rounded-lg overflow-hidden bg-white dark:bg-slate-900">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/60 border-b border-slate-200 dark:border-slate-800 text-slate-500 font-medium">
                <tr>
                  <th className="px-4 py-3">Document Name</th>
                  <th className="px-3 py-3">Format</th>
                  <th className="px-3 py-3">Size</th>
                  <th className="px-3 py-3">Pages</th>
                  <th className="px-3 py-3">Status</th>
                  <th className="px-3 py-3">Uploaded</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="px-4 py-3 font-medium text-slate-900 dark:text-white max-w-[240px] truncate">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="hover:text-blue-600 dark:hover:text-blue-400"
                        title={doc.originalFilename}
                      >
                        {doc.originalFilename}
                      </Link>
                    </td>
                    <td className="px-3 py-3 text-slate-500 uppercase">{doc.fileType}</td>
                    <td className="px-3 py-3 text-slate-500">{formatFileSize(doc.fileSize)}</td>
                    <td className="px-3 py-3 text-slate-500">{doc.pageCount || 1}</td>
                    <td className="px-3 py-3">{getStatusBadge(doc.status)}</td>
                    <td className="px-3 py-3 text-slate-500">{formatDate(doc.createdAt)}</td>
                    <td className="px-4 py-3 text-right space-x-2">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="inline-flex items-center gap-1 text-slate-600 dark:text-slate-400 hover:text-blue-600 dark:hover:text-blue-400"
                        title="View document"
                      >
                        <ExternalLink className="w-3.5 h-3.5" />
                      </Link>
                      <button
                        type="button"
                        onClick={() => handleDelete(doc.id, doc.originalFilename)}
                        disabled={deletingId === doc.id}
                        className="text-slate-400 hover:text-rose-600 transition-colors disabled:opacity-50"
                        title="Delete document"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-800 flex items-center justify-between text-xs text-slate-500">
              <span>
                Page {page + 1} of {totalPages}
              </span>
              <div className="flex items-center gap-1">
                <button
                  type="button"
                  onClick={() => fetchDocuments(page - 1, search, statusFilter)}
                  disabled={page === 0}
                  className="p-1 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-40"
                >
                  <ChevronLeft className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => fetchDocuments(page + 1, search, statusFilter)}
                  disabled={page + 1 >= totalPages}
                  className="p-1 rounded border border-slate-200 dark:border-slate-800 disabled:opacity-40"
                >
                  <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
