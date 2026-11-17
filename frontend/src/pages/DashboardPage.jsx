import React, { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";
import {
  Upload,
  FileText,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
  Search,
  ArrowRight,
  TrendingUp,
  RefreshCw,
} from "lucide-react";
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
} from "recharts";
import { getDashboardStats } from "../services/api";

const LEVEL_COLORS = {
  HIGH: "#dc2626",
  MEDIUM: "#d97706",
  LOW: "#16a34a",
  INFORMATIONAL: "#2563eb",
};

const CATEGORY_COLORS = ["#0f172a", "#2563eb", "#0d9488", "#7c3aed", "#d97706", "#dc2626", "#64748b"];

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchStats = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDashboardStats();
      setStats(data);
    } catch (err) {
      setError(err.response?.data?.message || "Failed to load dashboard statistics.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  // Filter recent documents by search query
  const filteredDocuments = useMemo(() => {
    if (!stats?.recentDocuments) return [];
    if (!searchQuery.trim()) return stats.recentDocuments;
    const q = searchQuery.toLowerCase();
    return stats.recentDocuments.filter(
      (doc) =>
        doc.originalFilename?.toLowerCase().includes(q) ||
        doc.status?.toLowerCase().includes(q) ||
        doc.fileType?.toLowerCase().includes(q)
    );
  }, [stats?.recentDocuments, searchQuery]);

  // Transform risk level distribution into chart data
  const levelChartData = useMemo(() => {
    if (!stats?.riskDistributionByLevel) return [];
    const dist = stats.riskDistributionByLevel;
    const items = [
      { name: "High", value: dist.HIGH || 0, color: LEVEL_COLORS.HIGH },
      { name: "Medium", value: dist.MEDIUM || 0, color: LEVEL_COLORS.MEDIUM },
      { name: "Low", value: dist.LOW || 0, color: LEVEL_COLORS.LOW },
      { name: "Informational", value: dist.INFORMATIONAL || 0, color: LEVEL_COLORS.INFORMATIONAL },
    ];
    return items;
  }, [stats?.riskDistributionByLevel]);

  const hasRiskData = useMemo(() => {
    return levelChartData.some((item) => item.value > 0);
  }, [levelChartData]);

  // Transform category distribution into chart data
  const categoryChartData = useMemo(() => {
    if (!stats?.riskDistributionByCategory) return [];
    return Object.entries(stats.riskDistributionByCategory).map(([cat, count], idx) => ({
      category: cat.length > 12 ? cat.substring(0, 10) + ".." : cat,
      fullName: cat,
      count: Number(count),
      color: CATEGORY_COLORS[idx % CATEGORY_COLORS.length],
    }));
  }, [stats?.riskDistributionByCategory]);

  const getStatusBadge = (status) => {
    switch (status) {
      case "COMPLETED":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 border border-emerald-200 dark:border-emerald-800">
            <CheckCircle2 className="w-3 h-3" /> Completed
          </span>
        );
      case "COMPLETED_WITH_WARNINGS":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300 border border-amber-200 dark:border-amber-800">
            <AlertTriangle className="w-3 h-3" /> Warnings
          </span>
        );
      case "FAILED":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-rose-50 text-rose-700 dark:bg-rose-950/40 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
            <XCircle className="w-3 h-3" /> Failed
          </span>
        );
      case "ANALYZING":
      case "EXTRACTING":
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-blue-50 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300 border border-blue-200 dark:border-blue-800">
            <RefreshCw className="w-3 h-3 animate-spin" /> {status}
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[11px] font-medium bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
            <Clock className="w-3 h-3" /> {status || "Uploaded"}
          </span>
        );
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div className="space-y-2">
            <div className="h-6 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
            <div className="h-4 w-72 bg-slate-100 dark:bg-slate-800/60 rounded animate-pulse" />
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-24 rounded border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 animate-pulse space-y-3">
              <div className="h-4 w-20 bg-slate-200 dark:bg-slate-800 rounded" />
              <div className="h-6 w-12 bg-slate-300 dark:bg-slate-700 rounded" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="border border-rose-200 dark:border-rose-900 rounded-lg p-6 bg-rose-50 dark:bg-rose-950/20 text-center space-y-3">
        <AlertTriangle className="w-8 h-8 text-rose-500 mx-auto" />
        <p className="text-sm font-medium text-rose-800 dark:text-rose-200">{error}</p>
        <button
          onClick={fetchStats}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-rose-600 text-white hover:bg-rose-700 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" /> Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">
            Workspace Dashboard
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Real-time aggregate portfolio metrics, risk exposure, and recent documents.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={fetchStats}
            title="Refresh statistics"
            className="p-2 rounded border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-400 transition-colors"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 bg-slate-900 hover:bg-slate-800 dark:bg-blue-600 dark:hover:bg-blue-700 text-white font-medium px-4 py-2 rounded text-sm transition-colors"
          >
            <Upload className="w-4 h-4" /> Upload Contract
          </Link>
        </div>
      </div>

      {/* 4 Core Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Documents Uploaded</span>
            <FileText className="w-4 h-4 text-slate-400" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900 dark:text-white">
              {stats?.totalDocuments || 0}
            </span>
            <span className="text-xs text-slate-400">total in workspace</span>
          </div>
        </div>

        <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Analyzed Contracts</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900 dark:text-white">
              {stats?.analyzedDocuments || 0}
            </span>
            <span className="text-xs text-emerald-600 dark:text-emerald-400">ready for review</span>
          </div>
        </div>

        <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Clauses Identified</span>
            <Layers className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900 dark:text-white">
              {stats?.totalClauses || 0}
            </span>
            <span className="text-xs text-slate-400">grounded clauses</span>
          </div>
        </div>

        <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Risk Findings</span>
            <AlertTriangle className="w-4 h-4 text-amber-600" />
          </div>
          <div className="mt-2 flex items-baseline gap-2">
            <span className="text-2xl font-bold text-slate-900 dark:text-white">
              {stats?.totalRisks || 0}
            </span>
            <span className="text-xs text-amber-600 dark:text-amber-400">
              {stats?.riskDistributionByLevel?.HIGH || 0} high severity
            </span>
          </div>
        </div>
      </div>

      {/* Analytics Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Risk Distribution Chart */}
        <div className="p-5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                Risk Distribution by Level
              </h2>
              <p className="text-xs text-slate-500">
                Proportion of identified contract risks across severity tiers.
              </p>
            </div>
            <TrendingUp className="w-4 h-4 text-slate-400" />
          </div>

          {hasRiskData ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={levelChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={48}
                    outerRadius={80}
                    paddingAngle={3}
                  >
                    {levelChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "rgba(15, 23, 42, 0.95)",
                      borderColor: "#334155",
                      borderRadius: "6px",
                      color: "#fff",
                      fontSize: "12px",
                    }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    iconType="circle"
                    wrapperStyle={{ fontSize: "11px", paddingTop: "12px" }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-xs space-y-2">
              <CheckCircle2 className="w-8 h-8 text-emerald-500" />
              <p>No risk findings recorded in workspace.</p>
            </div>
          )}
        </div>

        {/* Risk Distribution by Category Chart */}
        <div className="p-5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
                Risks by Legal Category
              </h2>
              <p className="text-xs text-slate-500">
                Categorical breakdown of potential liabilities and concerns.
              </p>
            </div>
            <Layers className="w-4 h-4 text-slate-400" />
          </div>

          {categoryChartData.length > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={categoryChartData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <XAxis
                    dataKey="category"
                    tick={{ fontSize: 10, fill: "#64748b" }}
                    angle={-20}
                    textAnchor="end"
                  />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11, fill: "#64748b" }} />
                  <Tooltip
                    formatter={(value, name, props) => [value, props.payload.fullName]}
                    contentStyle={{
                      backgroundColor: "rgba(15, 23, 42, 0.95)",
                      borderColor: "#334155",
                      borderRadius: "6px",
                      color: "#fff",
                      fontSize: "12px",
                    }}
                  />
                  <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                    {categoryChartData.map((entry, index) => (
                      <Cell key={`bar-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex flex-col items-center justify-center text-slate-400 text-xs space-y-2">
              <FileText className="w-8 h-8 text-slate-300 dark:text-slate-700" />
              <p>No categorized findings yet.</p>
            </div>
          )}
        </div>
      </div>

      {/* Recent Documents Table */}
      <div className="p-5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div>
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
              Recent Documents
            </h2>
            <p className="text-xs text-slate-500">
              Latest contracts uploaded and analyzed in your account.
            </p>
          </div>

          {/* Search Input */}
          <div className="relative w-full sm:w-64">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              placeholder="Search recent files..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-blue-500"
            />
          </div>
        </div>

        {filteredDocuments.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 dark:bg-slate-800/50 text-slate-500 border-b border-slate-200 dark:border-slate-800">
                <tr>
                  <th className="py-2.5 px-3 font-medium">Document Name</th>
                  <th className="py-2.5 px-3 font-medium">Format</th>
                  <th className="py-2.5 px-3 font-medium">Pages</th>
                  <th className="py-2.5 px-3 font-medium">Status</th>
                  <th className="py-2.5 px-3 font-medium">Uploaded Date</th>
                  <th className="py-2.5 px-3 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filteredDocuments.map((doc) => (
                  <tr key={doc.id} className="hover:bg-slate-50/70 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="py-2.5 px-3 font-medium text-slate-900 dark:text-white flex items-center gap-2">
                      <FileText className="w-4 h-4 text-slate-400 shrink-0" />
                      <span className="truncate max-w-xs">{doc.originalFilename}</span>
                    </td>
                    <td className="py-2.5 px-3 text-slate-500 uppercase">{doc.fileType || "PDF"}</td>
                    <td className="py-2.5 px-3 text-slate-500">{doc.pageCount || 1}</td>
                    <td className="py-2.5 px-3">{getStatusBadge(doc.status)}</td>
                    <td className="py-2.5 px-3 text-slate-500">
                      {doc.createdAt ? new Date(doc.createdAt).toLocaleDateString() : "Just now"}
                    </td>
                    <td className="py-2.5 px-3 text-right">
                      <Link
                        to={`/documents/${doc.id}`}
                        className="inline-flex items-center gap-1 text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
                      >
                        Inspect <ArrowRight className="w-3 h-3" />
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-10 text-center space-y-2 text-slate-500 text-xs">
            <FileText className="w-8 h-8 mx-auto text-slate-300 dark:text-slate-700" />
            <p>
              {searchQuery
                ? `No recent documents matching "${searchQuery}"`
                : "No contracts uploaded yet."}
            </p>
            {!searchQuery && (
              <Link
                to="/upload"
                className="inline-block text-blue-600 dark:text-blue-400 hover:underline pt-1"
              >
                Upload your first contract &rarr;
              </Link>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
