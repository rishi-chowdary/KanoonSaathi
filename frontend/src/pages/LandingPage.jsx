import React from "react";
import { Link } from "react-router-dom";
import { ArrowRight, ShieldCheck, FileSearch, MessageSquare } from "lucide-react";

export default function LandingPage() {
  return (
    <div className="space-y-16 py-6">
      <section className="text-center max-w-3xl mx-auto space-y-6">
        <h1 className="text-4xl sm:text-5xl font-bold tracking-tight text-slate-900 dark:text-white">
          Clear, grounded explanations for complex legal documents.
        </h1>
        <p className="text-lg text-slate-600 dark:text-slate-300 leading-relaxed">
          Upload any contract to extract key clauses, identify unusual risks, verify terms against source text, and query the agreement with page-cited answers.
        </p>
        <div className="flex items-center justify-center gap-4 pt-2">
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 bg-slate-900 hover:bg-slate-800 dark:bg-blue-600 dark:hover:bg-blue-700 text-white font-medium px-5 py-2.5 rounded-md transition-colors text-sm"
          >
            Upload a document <ArrowRight className="w-4 h-4" />
          </Link>
          <Link
            to="/login"
            className="inline-flex items-center font-medium px-5 py-2.5 rounded-md border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors text-sm"
          >
            Sign In
          </Link>
        </div>
      </section>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-6 pt-8 border-t border-slate-200 dark:border-slate-800">
        <div className="p-5 border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 space-y-2">
          <FileSearch className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="font-semibold text-slate-900 dark:text-white">1. Structured Extraction</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Converts PDF, DOCX, or scanned text into categorized clauses, summaries, and financial dates.
          </p>
        </div>

        <div className="p-5 border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 space-y-2">
          <ShieldCheck className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="font-semibold text-slate-900 dark:text-white">2. Evidence Verification</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Every identified clause and risk finding includes verbatim source text verified against original page numbers.
          </p>
        </div>

        <div className="p-5 border border-slate-200 dark:border-slate-800 rounded-lg bg-white dark:bg-slate-900 space-y-2">
          <MessageSquare className="w-5 h-5 text-blue-600 dark:text-blue-400" />
          <h2 className="font-semibold text-slate-900 dark:text-white">3. Page-Cited Chat</h2>
          <p className="text-sm text-slate-600 dark:text-slate-400">
            Ask specific contract questions. Answers cite exact document excerpts without inventing terms.
          </p>
        </div>
      </section>

      <section className="p-4 border border-slate-200 dark:border-slate-800 rounded-md bg-slate-100/60 dark:bg-slate-900/40 text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
        <strong>Privacy & Technical Limits:</strong> When running with cloud LLMs (Gemini), document text is transmitted to an external inference API. Switchable to local Ollama via configuration. Not a replacement for formal legal counsel.
      </section>
    </div>
  );
}

