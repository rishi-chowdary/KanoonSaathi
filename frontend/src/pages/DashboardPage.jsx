import React from "react";
import { Link } from "react-router-dom";
import { Upload, FileText, AlertTriangle, CheckCircle2 } from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Document Dashboard</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Overview of uploaded contracts, clause metrics, and risk levels.
          </p>
        </div>
        <Link
          to="/upload"
          className="inline-flex items-center gap-2 bg-slate-900 hover:bg-slate-800 dark:bg-blue-600 dark:hover:bg-blue-700 text-white font-medium px-4 py-2 rounded text-sm transition-colors"
        >
          <Upload className="w-4 h-4" /> Upload Contract
        </Link>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Total Documents</span>
            <FileText className="w-4 h-4" />
          </div>
          <div className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">0</div>
        </div>

        <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Completed Analyses</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">0</div>
        </div>

        <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>High Risk Findings</span>
            <AlertTriangle className="w-4 h-4 text-rose-600" />
          </div>
          <div className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">0</div>
        </div>

        <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900">
          <div className="flex items-center justify-between text-slate-500 text-xs">
            <span>Clauses Extracted</span>
            <FileText className="w-4 h-4 text-blue-600" />
          </div>
          <div className="mt-2 text-2xl font-semibold text-slate-900 dark:text-white">0</div>
        </div>
      </div>

      <div className="border border-slate-200 dark:border-slate-800 rounded-lg p-8 bg-white dark:bg-slate-900 text-center space-y-3">
        <p className="text-slate-600 dark:text-slate-400 text-sm">
          No documents analyzed yet. Upload a contract to begin.
        </p>
        <Link
          to="/upload"
          className="inline-block text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
        >
          Go to upload page &rarr;
        </Link>
      </div>
    </div>
  );
}

