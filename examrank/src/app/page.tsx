"use client";

import { useState } from "react";
import Hero from "./components/Hero";
import RankResultCard from "./components/RankResultCard";
import CollegePredictorDashboard from "./components/CollegePredictorDashboard";
import AnalyticsDashboard from "./components/AnalyticsDashboard";
import { motion, AnimatePresence } from "framer-motion";
import { JEEPredictionResponse } from "@/lib/api";
import AdmissionsChatbot from "./components/AdmissionsChatbot";
import DocumentScanner from "./components/DocumentScanner";
import { FileText } from "lucide-react";

export interface PredictionMeta {
  marks: number;
  maxMarks: number;
  shift: string;
  category: string;
  examId: string;
  examLabel: string;
  boardMarks?: number;
}

export default function Home() {
  const [showResults, setShowResults] = useState(false);
  const [predictionData, setPredictionData] = useState<JEEPredictionResponse | null>(null);
  const [meta, setMeta] = useState<PredictionMeta | null>(null);
  const [showScanner, setShowScanner] = useState(false);

  const handlePredict = (
    prediction: JEEPredictionResponse | null,
    predictionMeta: PredictionMeta
  ) => {
    if (prediction) setPredictionData(prediction);
    setMeta(predictionMeta);
    setShowResults(true);
    setTimeout(() => window.scrollTo({ top: 0, behavior: "smooth" }), 100);
  };

  const handleReset = () => {
    setShowResults(false);
    setPredictionData(null);
    setMeta(null);
  };

  return (
    <main className="min-h-screen bg-bg-secondary flex flex-col items-center">
      <AnimatePresence mode="wait">
        {!showResults ? (
          <motion.div
            key="hero"
            className="w-full"
            exit={{ opacity: 0, y: -50 }}
            transition={{ duration: 0.5 }}
          >
            <Hero onPredict={handlePredict} />
          </motion.div>
        ) : (
          <motion.div
            key="results"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="w-full px-4 py-8"
          >
            {/* Back button */}
            <div className="w-full max-w-5xl mx-auto mb-4">
              <button
                onClick={handleReset}
                className="text-sm font-semibold text-primary-500 hover:text-primary-800 flex items-center gap-1 transition-colors"
              >
                ← Predict again
              </button>
            </div>

            <RankResultCard predictionData={predictionData} meta={meta} />
            <CollegePredictorDashboard predictionData={predictionData} meta={meta} />
            <AnalyticsDashboard predictionData={predictionData} meta={meta} />
          </motion.div>
        )}
      </AnimatePresence>
      <AdmissionsChatbot context={
        meta ? {
          exam: meta.examLabel,
          rank: predictionData?.predicted_rank || undefined,
          category: meta.category,
        } : undefined
      } />

      {/* Floating Scanner Button */}
      <motion.button
        whileHover={{ scale: 1.05 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setShowScanner(true)}
        className="fixed bottom-24 right-6 bg-white border border-primary-200 text-primary-800 p-3 rounded-full shadow-lg hover:shadow-xl hover:border-accent-400 z-40 group flex items-center gap-2"
      >
        <div className="bg-primary-100 p-2 rounded-full group-hover:bg-accent-100 group-hover:text-accent-600 transition-colors">
          <FileText className="w-5 h-5" />
        </div>
        <span className="font-bold pr-2 hidden md:block">Scan Docs</span>
      </motion.button>

      {/* Scanner Modal */}
      <AnimatePresence>
        {showScanner && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 bg-black/60 backdrop-blur-sm"
              onClick={() => setShowScanner(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="relative z-10 w-full max-w-lg"
            >
              <DocumentScanner onClose={() => setShowScanner(false)} />
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </main>
  );
}
