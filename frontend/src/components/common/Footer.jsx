import React from "react";

export default function Footer() {
  return (
    <footer className="border-t border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 py-6 text-xs text-slate-500 dark:text-slate-400">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4">
        <p>LexiLegal AI &mdash; Academic Project.</p>
        <p className="text-center sm:text-right text-slate-400 dark:text-slate-500">
          Automated analysis aid. Does not constitute formal legal counsel.
        </p>
      </div>
    </footer>
  );
}

