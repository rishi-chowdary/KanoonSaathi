import React from "react";
import { User, LogOut } from "lucide-react";

export default function ProfilePage() {
  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">User Profile</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Account details and session settings.
        </p>
      </div>

      <div className="border border-slate-200 dark:border-slate-800 rounded-lg p-6 bg-white dark:bg-slate-900 space-y-4">
        <div className="flex items-center gap-3 pb-4 border-b border-slate-200 dark:border-slate-800">
          <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300">
            <User className="w-5 h-5" />
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900 dark:text-white">Guest User</p>
            <p className="text-xs text-slate-500">guest@lexilegal.local</p>
          </div>
        </div>

        <div className="text-xs text-slate-500 space-y-2">
          <p>
            Data isolation: Your analyses and uploaded documents are isolated to your user ID.
          </p>
        </div>

        <button
          type="button"
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded border border-rose-300 dark:border-rose-800 text-rose-600 dark:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
        >
          <LogOut className="w-3.5 h-3.5" /> Sign Out
        </button>
      </div>
    </div>
  );
}
