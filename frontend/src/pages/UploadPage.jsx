import React from "react";
import { UploadCloud, FileUp } from "lucide-react";

export default function UploadPage() {
  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Upload Legal Document</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Upload agreements in PDF, DOCX, or TXT format (max 10MB).
        </p>
      </div>

      <div className="border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-lg p-10 text-center space-y-4 bg-white dark:bg-slate-900 transition-colors">
        <div className="mx-auto w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300">
          <UploadCloud className="w-6 h-6" />
        </div>

        <div className="space-y-1">
          <p className="text-sm font-medium text-slate-900 dark:text-white">
            Drag and drop your file here, or click to browse
          </p>
          <p className="text-xs text-slate-500">
            Supports PDF (including scanned docs), DOCX, and TXT up to 10 MB
          </p>
        </div>

        <button
          type="button"
          className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded bg-slate-900 hover:bg-slate-800 dark:bg-blue-600 dark:hover:bg-blue-700 text-white transition-colors"
        >
          <FileUp className="w-4 h-4" /> Choose File
        </button>
      </div>

      <div className="p-4 rounded-md border border-slate-200 dark:border-slate-800 bg-slate-100/50 dark:bg-slate-900/30 text-xs text-slate-500 dark:text-slate-400 space-y-1">
        <p className="font-medium text-slate-700 dark:text-slate-300">Privacy Notice:</p>
        <p>
          Uploaded documents are analyzed using configured AI inference providers. If Gemini is selected, text is transmitted to Google&apos;s API. Full document text is never stored in inference logs.
        </p>
      </div>
    </div>
  );
}

