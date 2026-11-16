import React from "react";
import { Link } from "react-router-dom";
import { FolderOpen } from "lucide-react";

export default function HistoryPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Document History</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          All documents processed under your account.
        </p>
      </div>

      <div className="border border-slate-200 dark:border-slate-800 rounded-lg p-10 bg-white dark:bg-slate-900 text-center space-y-3">
        <FolderOpen className="w-8 h-8 mx-auto text-slate-400" />
        <p className="text-sm text-slate-600 dark:text-slate-400">
          No previous documents found.
        </p>
        <Link
          to="/upload"
          className="inline-block text-xs font-medium text-blue-600 dark:text-blue-400 hover:underline"
        >
          Upload your first document &rarr;
        </Link>
      </div>
    </div>
  );
}
