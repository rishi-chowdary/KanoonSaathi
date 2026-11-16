import React from "react";
import { Link, Outlet } from "react-router-dom";
import { FileText, Sun, Moon } from "lucide-react";
import { useTheme } from "../hooks/useTheme";

export default function AuthLayout() {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="min-h-screen flex flex-col justify-between bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 transition-colors">
      <header className="px-6 py-4 flex justify-between items-center">
        <Link to="/" className="flex items-center gap-2 font-semibold">
          <FileText className="w-5 h-5 text-blue-700 dark:text-blue-400" />
          <span className="font-legal text-lg tracking-tight">LexiLegal AI</span>
        </Link>
        <button
          onClick={toggleTheme}
          type="button"
          className="p-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white rounded-md hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
          aria-label="Toggle theme"
        >
          {theme === "dark" ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
        </button>
      </header>

      <main className="flex-1 flex items-center justify-center p-4">
        <div className="w-full max-w-md bg-white dark:bg-slate-900 p-8 rounded-lg border border-slate-200 dark:border-slate-800 shadow-sm">
          <Outlet />
        </div>
      </main>

      <footer className="py-4 text-center text-xs text-slate-400 dark:text-slate-600">
        LexiLegal AI &mdash; Informational legal document simplification
      </footer>
    </div>
  );
}
