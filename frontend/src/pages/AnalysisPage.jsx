import React, { useState } from "react";
import { useParams } from "react-router-dom";
import { FileText, ShieldAlert, Key, HelpCircle, MessageSquare, Download } from "lucide-react";

export default function AnalysisPage() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = useState("summary");

  const tabs = [
    { id: "summary", label: "Summary", icon: FileText },
    { id: "clauses", label: "Clauses", icon: FileText },
    { id: "risks", label: "Risks", icon: ShieldAlert },
    { id: "key-info", label: "Key Information", icon: Key },
    { id: "missing", label: "Missing Clauses", icon: HelpCircle },
    { id: "chat", label: "Document Chat", icon: MessageSquare },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800 gap-4">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-white">
            Document Analysis
          </h1>
          <p className="text-xs text-slate-500">ID: {id || "sample-doc-id"}</p>
        </div>

        <button
          type="button"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded border border-slate-300 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
        >
          <Download className="w-3.5 h-3.5" /> Download PDF Report
        </button>
      </div>

      <div className="flex border-b border-slate-200 dark:border-slate-800 gap-1 overflow-x-auto">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const active = activeTab === tab.id;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              type="button"
              className={`flex items-center gap-2 px-3 py-2 text-xs font-medium border-b-2 transition-colors whitespace-nowrap ${
                active
                  ? "border-blue-600 text-blue-600 dark:text-blue-400"
                  : "border-transparent text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
              }`}
            >
              <Icon className="w-4 h-4" />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="p-6 border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 text-sm text-slate-600 dark:text-slate-400">
        Active tab: <strong className="text-slate-900 dark:text-white">{activeTab}</strong>. Detailed analysis views will be connected in Phase 8 and 9.
      </div>
    </div>
  );
}

