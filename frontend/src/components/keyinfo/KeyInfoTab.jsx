import React, { useState, useEffect } from "react";
import {
  DollarSign,
  Calendar,
  Clock,
  AlertCircle,
  FileText,
  CheckCircle2,
  ListChecks,
  Copy,
  Check,
  ShieldCheck,
  Flag,
} from "lucide-react";
import { getDocumentKeyInfo } from "../../services/api";

function FactRow({ label, value, page, quote, verified, onSelectPage }) {
  const [copied, setCopied] = useState(false);
  const isNotSpecified = !value || value.toLowerCase() === "not specified";

  const handleCopy = () => {
    if (isNotSpecified) return;
    navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-2 hover:border-slate-300 dark:hover:border-slate-700 transition-colors">
      <div className="flex items-center justify-between text-xs">
        <span className="font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider text-[11px]">
          {label}
        </span>
        {page && !isNotSpecified && (
          <button
            type="button"
            onClick={() => onSelectPage && onSelectPage(page)}
            className="text-[11px] text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
          >
            <FileText className="w-3 h-3" /> Page {page}
          </button>
        )}
      </div>

      <div className="flex items-start justify-between gap-2">
        <div className="text-sm font-medium text-slate-900 dark:text-white leading-snug">
          {isNotSpecified ? (
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-normal text-slate-400 dark:text-slate-500 bg-slate-100 dark:bg-slate-800 italic">
              Not specified
            </span>
          ) : (
            value
          )}
        </div>

        {!isNotSpecified && (
          <button
            type="button"
            onClick={handleCopy}
            className="p-1 rounded text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
            title="Copy value"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5" />}
          </button>
        )}
      </div>

      {quote && !isNotSpecified && (
        <div className="pt-1">
          <div className="p-2 rounded bg-slate-50 dark:bg-slate-950/40 border border-slate-100 dark:border-slate-800/80 font-mono text-[11px] text-slate-600 dark:text-slate-400 leading-relaxed flex items-start justify-between gap-2">
            <span>&ldquo;{quote}&rdquo;</span>
            {verified && (
              <span className="text-emerald-600 dark:text-emerald-400 flex items-center gap-0.5 text-[10px] flex-shrink-0 font-sans">
                <CheckCircle2 className="w-3 h-3" /> Verified
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default function KeyInfoTab({ documentId, onSelectPage = null }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadKeyInfo() {
      try {
        setLoading(true);
        setError(null);
        const result = await getDocumentKeyInfo(documentId);
        setData(result);
      } catch (err) {
        console.error("Failed to load key info", err);
        setError("Unable to retrieve key information. Please verify document status.");
      } finally {
        setLoading(false);
      }
    }
    loadKeyInfo();
  }, [documentId]);

  if (loading) {
    return (
      <div className="py-16 text-center text-xs text-slate-500">
        <Clock className="w-8 h-8 animate-pulse text-blue-600 mx-auto mb-2" />
        Extracting contract terms, payment deadlines, milestones, and dates...
      </div>
    );
  }

  if (error || !data) {
    return (
      <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-xs text-slate-500 text-center">
        {error || "No key information extracted yet. Document may still be processing."}
      </div>
    );
  }

  const obligations = data.obligations || [];
  const importantDates = data.importantDates || [];

  return (
    <div className="space-y-6">
      {/* Financial Provisions Section */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
          <DollarSign className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider text-xs">
            Financial & Payment Terms
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <FactRow
            label="Contract Amount / Fee"
            value={data.contractAmount}
            page={data.contractAmountPage}
            onSelectPage={onSelectPage}
          />
          <FactRow
            label="Payment Deadlines & Schedule"
            value={data.paymentDeadlines}
            page={data.paymentDeadlinesPage}
            onSelectPage={onSelectPage}
          />
          <FactRow
            label="Penalties / Late Charges"
            value={data.penalties}
            page={data.penaltiesPage}
            onSelectPage={onSelectPage}
          />
        </div>
      </div>

      {/* Contract Duration & Termination Timeline Section */}
      <div className="space-y-3">
        <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
          <Calendar className="w-4 h-4 text-blue-600 dark:text-blue-400" />
          <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider text-xs">
            Term, Renewal & Termination Conditions
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <FactRow
            label="Effective / Start Date"
            value={data.startDate}
            page={data.startDatePage}
            onSelectPage={onSelectPage}
          />
          <FactRow
            label="Expiration / End Date"
            value={data.endDate}
            page={data.endDatePage}
            onSelectPage={onSelectPage}
          />
          <FactRow
            label="Renewal Terms / Date"
            value={data.renewalDate}
            page={data.renewalDatePage}
            onSelectPage={onSelectPage}
          />
          <FactRow
            label="Notice Period for Termination"
            value={data.noticePeriod}
            page={data.noticePeriodPage}
            onSelectPage={onSelectPage}
          />
          <div className="md:col-span-2">
            <FactRow
              label="Termination Conditions & Grounds"
              value={data.terminationConditions}
              page={data.terminationConditionsPage}
              onSelectPage={onSelectPage}
            />
          </div>
        </div>
      </div>

      {/* Important Dates Timeline */}
      {importantDates.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
            <Clock className="w-4 h-4 text-purple-600 dark:text-purple-400" />
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider text-xs">
              Key Dates & Milestones Timeline ({importantDates.length})
            </h2>
          </div>

          <div className="relative pl-6 space-y-4 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
            {importantDates.map((item, idx) => {
              const eventTitle = item.event || item.event_description || "Milestone";
              const dateVal = item.date_value || item.date || item.value || "Date not specified";
              const page = item.source_page || item.page;

              return (
                <div key={idx} className="relative group">
                  <div className="absolute -left-6 top-1 w-2.5 h-2.5 rounded-full bg-blue-600 ring-4 ring-white dark:ring-slate-900" />
                  <div className="p-3.5 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div>
                      <span className="text-xs font-semibold text-slate-900 dark:text-white block">
                        {eventTitle}
                      </span>
                      <span className="text-xs text-blue-600 dark:text-blue-400 font-medium">
                        {dateVal}
                      </span>
                    </div>

                    {page && (
                      <button
                        type="button"
                        onClick={() => onSelectPage && onSelectPage(page)}
                        className="text-[11px] text-slate-500 hover:text-blue-600 dark:hover:text-blue-400 flex items-center gap-1 self-start sm:self-auto"
                      >
                        <FileText className="w-3 h-3" /> Page {page}
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Ongoing Contractual Obligations */}
      {obligations.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2 border-b border-slate-200 dark:border-slate-800 pb-2">
            <ListChecks className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white uppercase tracking-wider text-xs">
              Core Ongoing Obligations ({obligations.length})
            </h2>
          </div>

          <div className="rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 divide-y divide-slate-100 dark:divide-slate-800/80">
            {obligations.map((ob, idx) => (
              <div key={idx} className="p-3 text-xs text-slate-800 dark:text-slate-200 flex items-start gap-2.5">
                <CheckCircle2 className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 mt-0.5 flex-shrink-0" />
                <span className="leading-relaxed">{ob}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

