"use client";

import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { BarChart3, Building2, Download } from "lucide-react";
import { useEffect, useState } from "react";
import { JEEPredictionResponse } from "@/lib/api";
import { PredictionMeta } from "../page";

interface Props {
  predictionData: JEEPredictionResponse | null;
  meta: PredictionMeta | null;
}

// Estimate rank from marks when backend is unavailable
function estimateRank(marks: number, maxMarks: number, examId: string): number {
  const pct = (marks / maxMarks) * 100;
  if (examId === "kcet") {
    if (pct >= 95) return Math.round(250 + (100 - pct) * 50);
    if (pct >= 90) return Math.round(2000 + (95 - pct) * 350);
    if (pct >= 85) return Math.round(5000 + (90 - pct) * 600);
    if (pct >= 80) return Math.round(10000 + (85 - pct) * 1000);
    if (pct >= 75) return Math.round(20000 + (80 - pct) * 2000);
    if (pct >= 70) return Math.round(40000 + (75 - pct) * 4000);
    if (pct >= 60) return Math.round(85000 + (70 - pct) * 4500);
    return Math.round(85000 + (60 - pct) * 5875);
  }
  if (examId === "mht-cet") {
    if (pct >= 80) return Math.round(2200 + (100 - pct) * 4015);
    if (pct >= 70) return Math.round(5500 + (80 - pct) * 550);
    if (pct >= 65) return Math.round(11000 + (70 - pct) * 1100);
    if (pct >= 55) return Math.round(19200 + (65 - pct) * 560);
    if (pct >= 50) return Math.round(27500 + (55 - pct) * 3300);
    if (pct >= 40) return Math.round(82500 + (50 - pct) * 11000);
    if (pct >= 30) return Math.round(192500 + (40 - pct) * 10750);
    return Math.round(300000 + (30 - pct) * 5000);
  }
  // Rough JEE Main/other rank formula
  if (pct >= 99) return Math.round((100 - pct) * 12000);
  if (pct >= 95) return Math.round((100 - pct) * 18000);
  if (pct >= 80) return Math.round((100 - pct) * 22000);
  return Math.round((100 - pct) * 25000);
}

function estimatePercentile(marks: number, maxMarks: number): number {
  const pct = (marks / maxMarks) * 100;
  return Math.min(99.99, Math.max(0, pct * 0.997 + 0.5)).toFixed(2) as unknown as number;
}

function categoryLabel(cat: string) {
  const map: Record<string, string> = {
    general: "General", ews: "EWS", obc: "OBC-NCL",
    sc: "SC", st: "ST", pwd: "PwD",
  };
  const catUpper = cat.toUpperCase();
  if (catUpper.startsWith("GM") || /^\d[A-Z]{0,2}/.test(catUpper) || catUpper.startsWith("SC") || catUpper.startsWith("ST")) {
    // KCET parsing
    let vertical = "";
    let horizontal = "";
    if (catUpper.startsWith("GM")) {
      vertical = "General Merit";
      horizontal = catUpper.slice(2);
    } else if (catUpper.startsWith("SC")) {
      vertical = "Scheduled Caste";
      horizontal = catUpper.slice(2);
    } else if (catUpper.startsWith("ST")) {
      vertical = "Scheduled Tribe";
      horizontal = catUpper.slice(2);
    } else {
      const match = catUpper.match(/^(\d[A-Z]?)(.*)$/);
      if (match) {
        vertical = `Category ${match[1]}`;
        horizontal = match[2];
      }
    }
    let horizText = "General";
    if (horizontal === "K") horizText = "Kannada Medium";
    if (horizontal === "R") horizText = "Rural";
    
    return `${vertical} (${horizText})`;
  }
  return map[cat.toLowerCase()] ?? cat.toUpperCase();
}

function useCountUp(target: number, duration = 1500) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    setValue(0);
    if (target === 0) return;
    const steps = 60;
    const increment = target / steps;
    let current = 0;
    let frame = 0;
    const timer = setInterval(() => {
      frame++;
      current += increment;
      if (frame >= steps) {
        setValue(target);
        clearInterval(timer);
      } else {
        setValue(Math.round(current));
      }
    }, duration / steps);
    return () => clearInterval(timer);
  }, [target, duration]);
  return value;
}

export default function RankResultCard({ predictionData, meta }: Props) {
  const marks      = meta?.marks ?? 0;
  const maxMarks   = meta?.maxMarks ?? 300;
  const category   = meta?.category ?? "general";
  const boardMarks = meta?.boardMarks;

  let effectiveMarks = marks;
  if (meta?.examId === "kcet" && boardMarks !== undefined && boardMarks !== null) {
    const kcetPct = (marks / 180.0) * 50.0;
    const boardPct = (boardMarks / 300.0) * 50.0;
    effectiveMarks = ((kcetPct + boardPct) / 100.0) * 180.0;
  }

  const rank       = predictionData?.predicted_rank    ?? estimateRank(effectiveMarks, maxMarks, meta?.examId ?? "jee-main");
  const catRank    = predictionData?.category_rank     ?? Math.round(rank * 0.75);
  const percentile = predictionData?.percentile        ?? estimatePercentile(effectiveMarks, maxMarks);
  const confidence = predictionData?.confidence        ?? 78;
  const normMarks  = predictionData?.normalized_marks  ?? effectiveMarks;
  const isEstimate = !predictionData;

  const animatedRank = useCountUp(rank);
  const confidencePct = Math.round(confidence);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, type: "spring" }}
      className="w-full max-w-2xl mx-auto mt-8"
    >
      <Card className="overflow-hidden shadow-2xl border-primary-200">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-900 to-primary-800 p-6 text-center border-b border-primary-700">
          {isEstimate && (
            <div className="inline-block bg-warning-500/20 text-warning-500 border border-warning-500/30 text-xs font-bold px-3 py-1 rounded-full mb-3 mr-2">
              ⚡ Estimated (backend offline)
            </div>
          )}
          {predictionData?.eligible === false && (
            <div className="inline-block bg-danger-500/20 text-danger-400 border border-danger-500/30 text-xs font-bold px-3 py-1 rounded-full mb-3">
              ⚠️ Ineligible (Subject/Total Cutoff Not Cleared)
            </div>
          )}
          <h2 className="text-primary-200 text-sm font-bold tracking-widest uppercase mb-4">
            🎯 Your Predicted Rank — {meta?.examLabel ?? "JEE Main 2026"}
          </h2>

          <div className="flex flex-col items-center">
            <span className="text-primary-400 text-xl font-medium mb-1">
              {meta?.examId === "kcet" || meta?.examId === "mht-cet" || meta?.examId === "comedk" ? "State Rank" : "AIR"}
            </span>
            <div className="text-6xl font-extrabold text-accent-400 mb-2 font-mono">
              {animatedRank.toLocaleString()}
            </div>
            <div className="h-1 w-32 bg-primary-700 rounded-full mb-3 overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: "100%" }}
                transition={{ duration: 1.5, delay: 0.5 }}
                className="h-full bg-accent-500"
              />
            </div>
            <div className="text-gold-400 font-mono text-xl">
              {typeof percentile === "number" ? percentile.toFixed(2) : percentile} Percentile
            </div>
            <div className="mt-1 text-primary-300 text-sm">
              Normalized Score: <span className="font-bold text-white">{normMarks.toFixed(1)}</span> / {maxMarks}
            </div>
          </div>
        </div>

        <CardContent className="p-0">
          {/* Stats row */}
          <div className="grid grid-cols-3 divide-x divide-primary-100 border-b border-primary-100 bg-bg-secondary">
            <div className="p-4 text-center">
              <div className="text-xs text-primary-600 font-semibold uppercase mb-1">Marks</div>
              <div className="font-bold text-primary-900 text-lg">{marks}</div>
              <div className="text-xs text-primary-500 font-medium">out of {maxMarks}</div>
            </div>
            <div className="p-4 text-center">
              <div className="text-xs text-primary-600 font-semibold uppercase mb-1">Category Rank</div>
              <div className="font-bold text-primary-900 text-lg">{catRank.toLocaleString()}</div>
              <div className="text-xs text-primary-500 font-medium">{categoryLabel(category)}</div>
            </div>
            {meta?.examId === "kcet" ? (
              <div className="p-4 text-center">
                <div className="text-xs text-primary-600 font-semibold uppercase mb-1">Board Marks</div>
                <div className="font-bold text-primary-900 text-lg">
                  {boardMarks !== undefined && boardMarks !== null ? boardMarks : "N/A"}
                </div>
                <div className="text-xs text-primary-500 font-medium">out of 300</div>
              </div>
            ) : (
              <div className="p-4 text-center">
                <div className="text-xs text-primary-600 font-semibold uppercase mb-1">Shift</div>
                <div className="font-bold text-primary-900 text-lg capitalize">
                  {(meta?.shift ?? "shift1").replace(/([a-z])(\d)/i, "$1 $2")}
                </div>
                <div className="text-xs text-primary-500 font-medium">{meta?.examLabel?.split(" ")[0]}</div>
              </div>
            )}
          </div>

          {/* Confidence bar */}
          <div className="p-6 bg-white">
            <div className="flex justify-between items-end mb-2">
              <span className="text-sm font-semibold text-primary-700">Prediction Confidence</span>
              <span className="text-sm font-bold text-primary-900">{confidencePct}%</span>
            </div>
            <div className="h-2 w-full bg-primary-100 rounded-full overflow-hidden mb-3">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${confidencePct}%` }}
                transition={{ duration: 1, delay: 0.8 }}
                className={`h-full ${confidencePct > 85 ? "bg-info-500" : "bg-warning-500"}`}
              />
            </div>
            <p className="text-xs text-primary-500 text-center mb-6">
              {isEstimate
                ? "Backend unavailable — rough estimate based on marks percentage"
                : `Based on historical data for ${meta?.shift ?? "this shift"}`}
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Button variant="outline" className="w-full flex gap-2">
                <BarChart3 className="w-4 h-4" /> Analysis
              </Button>
              <Button variant="primary" className="w-full flex gap-2">
                <Building2 className="w-4 h-4" /> Colleges
              </Button>
              <Button variant="secondary" className="w-full flex gap-2">
                <Download className="w-4 h-4" /> Download
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
