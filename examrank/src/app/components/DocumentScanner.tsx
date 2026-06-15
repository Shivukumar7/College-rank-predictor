"use client";

import React, { useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { UploadCloud, FileText, CheckCircle2, AlertTriangle, Loader2, X, RefreshCw } from "lucide-react";
import { createWorker } from "tesseract.js";

type DocType = "OBC-NCL" | "EWS" | "SC/ST";

interface ScanResult {
  text: string;
  isValid: boolean;
  issues: string[];
  confidence: number;
}

export default function DocumentScanner({ onClose }: { onClose?: () => void }) {
  const [docType, setDocType] = useState<DocType>("OBC-NCL");
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<ScanResult | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [progress, setProgress] = useState({ status: "", pct: 0 });
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateText = (text: string, type: DocType): ScanResult => {
    const issues: string[] = [];
    const lowerText = text.toLowerCase();
    let isValid = true;

    if (type === "OBC-NCL") {
      if (!lowerText.includes("non creamy") && !lowerText.includes("non-creamy") && !lowerText.includes("does not belong to")) {
        issues.push("Could not verify 'Non-Creamy Layer' wording. Ensure the certificate explicitly mentions this.");
        isValid = false;
      }
      
      // Look for a year like 2026, 2025, 2024
      const yearMatches = text.match(/20\d{2}/g);
      const currentAdmissionYear = 2026; // Assuming for 2026 admissions
      
      let foundValidYear = false;
      if (yearMatches) {
        for (const yr of yearMatches) {
          if (parseInt(yr) >= currentAdmissionYear || parseInt(yr) === currentAdmissionYear - 1) {
            foundValidYear = true;
            break;
          }
        }
      }
      if (!foundValidYear) {
        issues.push("Certificate issue date appears to be old or not readable. OBC-NCL must be issued after April 1 of the admission year.");
        isValid = false;
      }
    } else if (type === "EWS") {
      if (!lowerText.includes("economically weaker") && !lowerText.includes("ews")) {
        issues.push("Could not find 'Economically Weaker Section' wording.");
        isValid = false;
      }
    } else if (type === "SC/ST") {
      if (!lowerText.includes("scheduled caste") && !lowerText.includes("scheduled tribe") && !lowerText.includes("caste")) {
        issues.push("Could not verify SC/ST caste details clearly.");
        isValid = false;
      }
    }

    return {
      text,
      isValid,
      issues,
      confidence: 100, // placeholder
    };
  };

  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Create a preview
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target?.result as string);
    reader.readAsDataURL(file);

    setIsScanning(true);
    setResult(null);
    setProgress({ status: "Initializing Engine...", pct: 10 });

    try {
      const worker = await createWorker({
        logger: m => {
          if (m.status === "recognizing text") {
            setProgress({ status: "Scanning Document...", pct: Math.round(m.progress * 100) });
          }
        }
      });
      
      await worker.loadLanguage('eng');
      await worker.initialize('eng');
      
      setProgress({ status: "Extracting Text...", pct: 90 });
      const { data: { text, confidence } } = await worker.recognize(file);
      
      await worker.terminate();

      const validationResult = validateText(text, docType);
      validationResult.confidence = confidence;
      
      setResult(validationResult);
    } catch (err) {
      console.error(err);
      setResult({
        text: "",
        isValid: false,
        issues: ["Failed to scan the document. Please try a clearer image."],
        confidence: 0
      });
    } finally {
      setIsScanning(false);
      setProgress({ status: "", pct: 0 });
    }
  };

  const reset = () => {
    setImagePreview(null);
    setResult(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  return (
    <div className="bg-white rounded-3xl shadow-2xl border border-primary-200 overflow-hidden max-w-lg w-full flex flex-col relative z-50">
      <div className="bg-primary-900 p-4 sm:p-6 text-white flex justify-between items-center relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full blur-2xl -mr-10 -mt-10"></div>
        <div className="relative z-10">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <FileText className="w-6 h-6 text-accent-400" />
            Smart Document Scanner
          </h2>
          <p className="text-primary-200 text-sm mt-1">AI-powered validity check for JoSAA docs</p>
        </div>
        {onClose && (
          <button onClick={onClose} className="p-2 rounded-full hover:bg-white/10 transition-colors z-10">
            <X className="w-5 h-5 text-primary-200" />
          </button>
        )}
      </div>

      <div className="p-6">
        {!imagePreview ? (
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-semibold text-primary-900 mb-2">Select Document Type</label>
              <div className="flex gap-2">
                {(["OBC-NCL", "EWS", "SC/ST"] as DocType[]).map((type) => (
                  <button
                    key={type}
                    onClick={() => setDocType(type)}
                    className={`flex-1 py-2 px-3 text-sm font-medium rounded-xl border transition-all ${
                      docType === type 
                        ? "bg-accent-50 text-accent-700 border-accent-300 shadow-sm" 
                        : "bg-white text-primary-600 border-primary-200 hover:bg-primary-50"
                    }`}
                  >
                    {type}
                  </button>
                ))}
              </div>
            </div>

            <div 
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-primary-300 rounded-2xl p-8 flex flex-col items-center justify-center text-center cursor-pointer hover:border-accent-400 hover:bg-accent-50/30 transition-all group"
            >
              <input 
                type="file" 
                accept="image/*" 
                className="hidden" 
                ref={fileInputRef}
                onChange={handleImageUpload}
              />
              <div className="w-16 h-16 bg-primary-100 text-primary-500 rounded-full flex items-center justify-center mb-4 group-hover:bg-accent-100 group-hover:text-accent-600 transition-colors">
                <UploadCloud className="w-8 h-8" />
              </div>
              <h3 className="text-primary-900 font-bold mb-1">Upload Certificate Image</h3>
              <p className="text-sm text-primary-500">JPG, PNG up to 5MB</p>
            </div>
            
            <div className="bg-info-50 border border-info-100 rounded-xl p-4 text-sm text-info-800 flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-info-500 shrink-0 mt-0.5" />
              <p>We analyze the text to ensure critical keywords (like "Non-Creamy Layer") and dates are present before you upload to JoSAA.</p>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Scanning State */}
            {isScanning && (
              <div className="flex flex-col items-center justify-center py-10">
                <div className="relative mb-6">
                  <div className="w-24 h-24 rounded-2xl overflow-hidden border-2 border-primary-200 relative">
                    <img src={imagePreview} alt="Preview" className="w-full h-full object-cover blur-sm opacity-50" />
                    {/* Scanner line animation */}
                    <motion.div 
                      className="absolute top-0 left-0 right-0 h-1 bg-accent-500 shadow-[0_0_10px_2px_rgba(59,130,246,0.5)]"
                      animate={{ y: [0, 96, 0] }}
                      transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                    />
                  </div>
                </div>
                <h3 className="font-bold text-primary-900 mb-2">{progress.status}</h3>
                <div className="w-full max-w-[200px] h-2 bg-primary-100 rounded-full overflow-hidden">
                  <div className="h-full bg-accent-500 transition-all duration-300" style={{ width: `${progress.pct}%` }} />
                </div>
              </div>
            )}

            {/* Result State */}
            {!isScanning && result && (
              <AnimatePresence>
                <motion.div 
                  initial={{ opacity: 0, y: 10 }} 
                  animate={{ opacity: 1, y: 0 }}
                  className="space-y-4"
                >
                  <div className={`p-4 rounded-2xl border flex items-start gap-3 ${
                    result.isValid 
                      ? "bg-success-50 border-success-200 text-success-800" 
                      : "bg-danger-50 border-danger-200 text-danger-800"
                  }`}>
                    {result.isValid ? (
                      <CheckCircle2 className="w-6 h-6 text-success-500 shrink-0" />
                    ) : (
                      <AlertTriangle className="w-6 h-6 text-danger-500 shrink-0" />
                    )}
                    <div>
                      <h3 className="font-bold text-lg mb-1">
                        {result.isValid ? "Certificate Looks Good!" : "Potential Issues Found"}
                      </h3>
                      {!result.isValid && (
                        <ul className="list-disc pl-4 space-y-1 text-sm mt-2">
                          {result.issues.map((issue, i) => <li key={i}>{issue}</li>)}
                        </ul>
                      )}
                      {result.isValid && (
                        <p className="text-sm">We successfully verified the required keywords for your {docType} certificate.</p>
                      )}
                    </div>
                  </div>

                  <div className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                    <h4 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-2">Extracted Text Snippet</h4>
                    <p className="text-sm text-gray-700 font-mono line-clamp-4 leading-relaxed">
                      {result.text.substring(0, 200)}...
                    </p>
                    <div className="mt-3 text-xs text-gray-400">
                      Confidence Score: <span className="font-bold text-gray-600">{Math.round(result.confidence)}%</span>
                    </div>
                  </div>

                  <button 
                    onClick={reset}
                    className="w-full py-3 rounded-xl border border-primary-200 text-primary-700 font-bold hover:bg-primary-50 transition-colors flex items-center justify-center gap-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    Scan Another Document
                  </button>
                </motion.div>
              </AnimatePresence>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
