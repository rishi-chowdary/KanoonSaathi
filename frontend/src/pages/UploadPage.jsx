import React, { useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import api from "../services/api";
import {
  UploadCloud,
  FileUp,
  FileText,
  CheckCircle2,
  AlertCircle,
  Loader2,
  ArrowRight,
  ShieldCheck,
} from "lucide-react";

export default function UploadPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [dragOver, setDragOver] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [consentGiven, setConsentGiven] = useState(true);
  const [error, setError] = useState(null);

  // Processing state machine: IDLE -> UPLOADING -> EXTRACTING -> EXTRACTED | FAILED
  const [processStep, setProcessStep] = useState("IDLE");
  const [docId, setDocId] = useState(null);
  const [docInfo, setDocInfo] = useState(null);
  const [isDuplicate, setIsDuplicate] = useState(false);

  const MAX_SIZE = 10 * 1024 * 1024; // 10MB
  const ALLOWED_EXTS = ["pdf", "docx", "txt"];

  const validateFile = (file) => {
    setError(null);
    if (!file) return false;

    if (file.size === 0) {
      setError("The selected file is empty. Please select a valid document.");
      return false;
    }

    if (file.size > MAX_SIZE) {
      setError("File exceeds the 10MB limit. Please upload a smaller document.");
      return false;
    }

    const ext = file.name.split(".").pop().toLowerCase();
    if (!ALLOWED_EXTS.includes(ext)) {
      setError("Unsupported file format. Please upload a PDF, DOCX, or TXT file.");
      return false;
    }

    return true;
  };

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file && validateFile(file)) {
      setSelectedFile(file);
    }
  };

  const pollStatus = async (id) => {
    try {
      const resp = await api.get(`/documents/${id}/status`);
      const { status, failureReason, pageCount } = resp.data;

      if (status === "EXTRACTED") {
        setProcessStep("EXTRACTED");
        setDocInfo((prev) => ({ ...prev, pageCount, status }));
      } else if (status === "FAILED") {
        setProcessStep("FAILED");
        setError(failureReason || "Text extraction failed.");
      } else {
        // Still EXTRACTING or UPLOADED: poll again in 2s
        setProcessStep("EXTRACTING");
        setTimeout(() => pollStatus(id), 2000);
      }
    } catch (err) {
      setProcessStep("FAILED");
      setError("Could not check processing status.");
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    if (!consentGiven) {
      setError("Please acknowledge the privacy consent notice before uploading.");
      return;
    }

    setError(null);
    setUploading(true);
    setUploadProgress(0);
    setProcessStep("UPLOADING");

    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await api.post("/documents/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
            setUploadProgress(percent);
          }
        },
      });

      const { id, duplicate, originalFilename, fileSize, status } = response.data;
      setDocId(id);
      setIsDuplicate(duplicate);
      setDocInfo({ id, originalFilename, fileSize, status });
      setUploading(false);

      if (duplicate || status === "EXTRACTED") {
        setProcessStep("EXTRACTED");
      } else {
        setProcessStep("EXTRACTING");
        setTimeout(() => pollStatus(id), 1500);
      }
    } catch (err) {
      setUploading(false);
      setProcessStep("FAILED");
      const msg = err.response?.data?.message || err.message || "Upload failed. Please check the file and try again.";
      setError(msg);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setProcessStep("IDLE");
    setDocId(null);
    setDocInfo(null);
    setError(null);
    setUploadProgress(0);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white">Upload Legal Document</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400">
          Upload agreements in PDF, DOCX, or TXT format (max 10MB).
        </p>
      </div>

      {error && (
        <div className="p-3 text-xs rounded bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900 flex items-start gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {processStep === "IDLE" && (
        <>
          <div
            onDragOver={(e) => {
              e.preventDefault();
              setDragOver(true);
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-10 text-center space-y-4 transition-colors ${
              dragOver
                ? "border-blue-500 bg-blue-50/50 dark:bg-blue-950/20"
                : "border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900"
            }`}
          >
            <div className="mx-auto w-12 h-12 rounded-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-slate-600 dark:text-slate-300">
              <UploadCloud className="w-6 h-6" />
            </div>

            <div className="space-y-1">
              <p className="text-sm font-medium text-slate-900 dark:text-white">
                Drag and drop your file here, or click to browse
              </p>
              <p className="text-xs text-slate-500">
                Supports PDF (text or scanned), DOCX, and TXT up to 10 MB
              </p>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt"
              className="hidden"
            />

            <button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded bg-slate-900 hover:bg-slate-800 dark:bg-blue-600 dark:hover:bg-blue-700 text-white transition-colors"
            >
              <FileUp className="w-4 h-4" /> Choose File
            </button>
          </div>

          {selectedFile && (
            <div className="p-4 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  <div>
                    <p className="text-sm font-medium text-slate-900 dark:text-white">{selectedFile.name}</p>
                    <p className="text-xs text-slate-500">{(selectedFile.size / 1024).toFixed(1)} KB</p>
                  </div>
                </div>
                <button
                  type="button"
                  onClick={resetUpload}
                  className="text-xs text-slate-500 hover:text-rose-600 dark:hover:text-rose-400"
                >
                  Remove
                </button>
              </div>

              <div className="pt-2 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
                <label className="flex items-center gap-2 text-xs text-slate-600 dark:text-slate-400 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={consentGiven}
                    onChange={(e) => setConsentGiven(e.target.checked)}
                    className="rounded border-slate-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span>I agree to transmit this contract for automated legal analysis</span>
                </label>

                <button
                  type="button"
                  onClick={handleUpload}
                  className="px-4 py-2 text-xs font-medium rounded bg-blue-600 hover:bg-blue-700 text-white transition-colors"
                >
                  Upload & Process
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {processStep !== "IDLE" && (
        <div className="p-6 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 space-y-6">
          <div className="space-y-1">
            <h2 className="text-sm font-semibold text-slate-900 dark:text-white">Document Processing Pipeline</h2>
            <p className="text-xs text-slate-500">
              {docInfo?.originalFilename || selectedFile?.name}
            </p>
          </div>

          {/* Stepper */}
          <div className="space-y-4">
            {/* Step 1: Upload */}
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                {processStep === "UPLOADING" ? (
                  <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                ) : (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                )}
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-center text-xs font-medium text-slate-900 dark:text-white">
                  <span>1. File Upload & Validation</span>
                  {processStep === "UPLOADING" && <span>{uploadProgress}%</span>}
                </div>
                {processStep === "UPLOADING" && (
                  <div className="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full mt-1.5 overflow-hidden">
                    <div
                      className="bg-blue-600 h-1.5 rounded-full transition-all duration-300"
                      style={{ width: `${uploadProgress}%` }}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Step 2: Extraction & Chunking */}
            <div className="flex items-start gap-3">
              <div className="mt-0.5">
                {processStep === "EXTRACTING" ? (
                  <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                ) : processStep === "EXTRACTED" ? (
                  <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                ) : processStep === "FAILED" ? (
                  <AlertCircle className="w-5 h-5 text-rose-600" />
                ) : (
                  <div className="w-5 h-5 rounded-full border border-slate-300 dark:border-slate-700" />
                )}
              </div>
              <div className="flex-1">
                <div className="text-xs font-medium text-slate-900 dark:text-white">
                  2. Text Extraction & OCR Chunking
                </div>
                <p className="text-xs text-slate-500 mt-0.5">
                  {processStep === "EXTRACTING" && "Parsing pages, detecting clauses, and indexing chunks..."}
                  {processStep === "EXTRACTED" && `Extracted ${docInfo?.pageCount || 1} page(s) successfully.`}
                  {processStep === "FAILED" && "Extraction could not be completed."}
                  {processStep === "UPLOADING" && "Pending upload completion."}
                </p>
              </div>
            </div>
          </div>

          {/* Results / Next Actions */}
          {processStep === "EXTRACTED" && (
            <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between">
              <div className="flex items-center gap-2 text-xs text-emerald-700 dark:text-emerald-400">
                <ShieldCheck className="w-4 h-4" />
                {isDuplicate ? "Document already exists in your vault." : "Document extracted and indexed."}
              </div>

              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={resetUpload}
                  className="px-3 py-1.5 text-xs rounded border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
                >
                  Upload Another
                </button>
                <Link
                  to={`/documents/${docId}`}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded bg-blue-600 hover:bg-blue-700 text-white transition-colors"
                >
                  <span>View Extracted Text</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          )}

          {processStep === "FAILED" && (
            <div className="pt-4 border-t border-slate-100 dark:border-slate-800 flex justify-end">
              <button
                type="button"
                onClick={resetUpload}
                className="px-4 py-2 text-xs font-medium rounded bg-slate-900 dark:bg-blue-600 text-white"
              >
                Try Again
              </button>
            </div>
          )}
        </div>
      )}

      {/* Privacy Notice Box */}
      <div className="p-4 rounded-md border border-slate-200 dark:border-slate-800 bg-slate-100/50 dark:bg-slate-900/30 text-xs text-slate-500 dark:text-slate-400 space-y-1">
        <p className="font-medium text-slate-700 dark:text-slate-300">Privacy & Data Grounding Policy:</p>
        <p>
          Uploaded documents are analyzed using configured AI inference providers. If Gemini is selected, text is transmitted to Google&apos;s API. Full document text is never stored in inference logs.
        </p>
      </div>
    </div>
  );
}
