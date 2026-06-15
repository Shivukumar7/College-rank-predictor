"use client";

import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/Card";
import { Building2, ChevronDown, ChevronUp, GraduationCap, Loader2, Scale } from "lucide-react";
import { useState, useEffect } from "react";
import { JEEPredictionResponse, getCollegePredictions, College } from "@/lib/api";
import { PredictionMeta } from "../page";
import CollegeComparer from "./CollegeComparer";
import ChoiceOptimizer from "./ChoiceOptimizer";
import PlacementAnalytics from "./PlacementAnalytics";

interface Props {
  predictionData: JEEPredictionResponse | null;
  meta: PredictionMeta | null;
}

const TYPE_COLORS: Record<string, string> = {
  NIT:     "bg-blue-100 text-blue-700",
  IIIT:    "bg-purple-100 text-purple-700",
  GFTI:    "bg-emerald-100 text-emerald-700",
  Private: "bg-amber-100 text-amber-700",
  IIT:     "bg-indigo-100 text-indigo-700",
  AIIMS:   "bg-rose-100 text-rose-700",
  JIPMER:  "bg-pink-100 text-pink-700",
  Medical: "bg-red-100 text-red-700",
  "Govt Medical": "bg-red-100 text-red-700",
  Engineering: "bg-blue-100 text-blue-700",
  "Private Engineering": "bg-amber-100 text-amber-700",
  Auto: "bg-gray-100 text-gray-700",
};

function chanceColor(chance: number) {
  if (chance >= 80) return "text-success-600";
  if (chance >= 50) return "text-warning-500";
  return "text-danger-500";
}

function estimateRank(marks: number, maxMarks: number, examId: string) {
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
  if (pct >= 99) return Math.round((100 - pct) * 12000);
  if (pct >= 95) return Math.round((100 - pct) * 18000);
  if (pct >= 80) return Math.round((100 - pct) * 22000);
  return Math.round((100 - pct) * 25000);
}

export default function CollegePredictorDashboard({ predictionData, meta }: Props) {
  const [showLow, setShowLow] = useState(false);
  const [colleges, setColleges] = useState<College[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Quota & Compare states
  const [quota, setQuota] = useState<string>("Other State");
  const [selectedColleges, setSelectedColleges] = useState<College[]>([]);

  const marks      = meta?.marks ?? 0;
  const maxMarks   = meta?.maxMarks ?? 300;
  const examId     = meta?.examId ?? "jee-main";
  const category   = meta?.category ?? "general";
  const boardMarks = meta?.boardMarks;

  let effectiveMarks = marks;
  if (examId === "kcet" && boardMarks !== undefined && boardMarks !== null) {
    const kcetPct = (marks / 180.0) * 50.0;
    const boardPct = (boardMarks / 300.0) * 50.0;
    effectiveMarks = ((kcetPct + boardPct) / 100.0) * 180.0;
  }

  const rank     = predictionData?.predicted_rank ?? estimateRank(effectiveMarks, maxMarks, examId);

  useEffect(() => {
    let mounted = true;
    
    async function fetchColleges() {
      setLoading(true);
      setError(null);
      try {
        const examIdApi = examId === "jee-adv" ? "jee-advanced" : examId;
        const data = await getCollegePredictions(examIdApi, rank, marks, category, quota);
        if (mounted) {
          setColleges(data.colleges || []);
        }
      } catch (err) {
        if (mounted) {
          setError("Failed to fetch college predictions.");
          console.error(err);
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }
    
    fetchColleges();
    return () => { mounted = false; };
  }, [examId, rank, marks, category, quota]);

  const toggleCompare = (college: College) => {
    const isSelected = selectedColleges.some(
      (c) => c.name === college.name && c.branch === college.branch
    );
    if (isSelected) {
      setSelectedColleges(selectedColleges.filter(
        (c) => !(c.name === college.name && c.branch === college.branch)
      ));
    } else {
      if (selectedColleges.length >= 3) {
        alert("You can compare up to 3 colleges side-by-side.");
        return;
      }
      setSelectedColleges([...selectedColleges, college]);
    }
  };

  const high     = colleges.filter((c) => c.chance >= 80);
  const moderate = colleges.filter((c) => c.chance >= 40 && c.chance < 80);
  const low      = colleges.filter((c) => c.chance < 40);

  return (
    <div className="w-full max-w-5xl mx-auto mt-12 space-y-8 print:space-y-0">
      
      {/* College Comparer component (if any colleges are selected) */}
      <CollegeComparer
        selectedColleges={selectedColleges}
        onRemove={toggleCompare}
        examId={examId === "jee-adv" ? "jee-advanced" : examId}
        category={category}
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 print:hidden">
        <h2 className="text-3xl font-bold text-primary-900 flex items-center gap-3">
          <Building2 className="w-8 h-8 text-accent-500" />
          College Predictions
        </h2>
        
        <div className="flex flex-wrap items-center gap-3">
          {/* Quota Selector dropdown */}
          {examId === "jee-main" && (
            <div className="flex items-center gap-2">
              <label htmlFor="quota-select" className="text-sm font-semibold text-primary-600">Quota:</label>
              <select
                id="quota-select"
                value={quota}
                onChange={(e) => setQuota(e.target.value)}
                className="text-sm bg-white border border-primary-200 px-3 py-1.5 rounded-lg focus:outline-none focus:border-accent-500 font-semibold text-primary-850 cursor-pointer shadow-sm"
              >
                <option value="Other State">Other State (OS)</option>
                <option value="Home State">Home State (HS)</option>
              </select>
            </div>
          )}

          <div className="text-sm text-primary-500 font-medium bg-bg-secondary border border-primary-200 px-3 py-1.5 rounded-lg">
            Based on Predicted Rank: <span className="font-bold text-primary-900">{rank.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 space-y-4">
          <Loader2 className="w-12 h-12 text-accent-500 animate-spin" />
          <p className="text-primary-600 font-medium">Analyzing real historical data...</p>
        </div>
      ) : error ? (
        <div className="text-center py-12 text-danger-500 font-medium">{error}</div>
      ) : colleges.length === 0 ? (
        <div className="text-center py-12 text-primary-500 font-medium">No colleges found for this rank and category.</div>
      ) : (
        <>
          {/* HIGH CHANCE */}
          <section className="print:hidden">
            <div className="flex items-center justify-between mb-4 border-b border-primary-200 pb-2">
              <h3 className="text-xl font-bold text-success-700">HIGH CHANCE (80%+)</h3>
              <span className="text-sm font-medium text-primary-500">{high.length} Colleges</span>
            </div>

            {high.length === 0 ? (
              <p className="text-primary-500 text-sm italic">No colleges in this tier for your rank. Try improving your score!</p>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {high.map((college, i) => {
                  const isCompared = selectedColleges.some(
                    (c) => c.name === college.name && c.branch === college.branch
                  );
                  return (
                    <motion.div
                      key={`${college.name}-${college.branch}-${i}`}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.08 }}
                      className="relative overflow-hidden bg-white border border-primary-200 rounded-2xl p-6 hover:-translate-y-1 hover:shadow-xl transition-all duration-300 before:absolute before:top-0 before:left-0 before:right-0 before:h-1 before:bg-gradient-success group flex flex-col justify-between min-h-[200px]"
                    >
                      <div>
                        <div className="absolute top-4 right-4 bg-success-50 text-success-600 text-xs font-bold px-2 py-1 rounded-md">
                          {college.chance}% Chance
                        </div>
                        <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center mb-4 text-primary-600 group-hover:text-accent-500 transition-colors">
                          <Building2 className="w-6 h-6" />
                        </div>
                        <h4 className="text-base font-bold text-primary-900 mb-0.5">{college.name}</h4>
                        <p className="text-primary-600 text-sm font-medium mb-1 line-clamp-2">{college.branch}</p>
                        <div className="mt-2 flex flex-wrap gap-2">
                          <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${TYPE_COLORS[college.type] || "bg-gray-100 text-gray-700"}`}>
                            {college.type}
                          </span>
                          <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-primary-100 text-primary-700">
                            {college.quota}
                          </span>
                        </div>
                      </div>

                      <div className="flex justify-between items-center pt-4 mt-4 border-t border-primary-100">
                        <div className="text-sm">
                          <span className="text-primary-400">Closing: </span>
                          <span className="font-bold text-primary-800">{college.closing_rank.toLocaleString()}</span>
                        </div>
                        <button
                          onClick={() => toggleCompare(college)}
                          className={`text-xs font-bold px-3 py-1.5 rounded-lg border transition-all flex items-center gap-1 cursor-pointer ${
                            isCompared
                              ? "bg-accent-500 border-accent-500 text-white shadow-sm"
                              : "bg-white border-primary-200 text-primary-600 hover:border-accent-500 hover:text-accent-600"
                          }`}
                        >
                          <Scale className="w-3.5 h-3.5" />
                          {isCompared ? "Compared" : "Compare"}
                        </button>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </section>

          {/* MODERATE CHANCE */}
          <section className="print:hidden">
            <div className="flex items-center justify-between mb-4 border-b border-primary-200 pb-2">
              <h3 className="text-xl font-bold text-warning-500">MODERATE CHANCE (40–80%)</h3>
              <span className="text-sm font-medium text-primary-500">{moderate.length} Colleges</span>
            </div>

            {moderate.length === 0 ? (
              <p className="text-primary-500 text-sm italic">No colleges in this tier for your rank.</p>
            ) : (
              <Card className="overflow-hidden border-primary-200">
                <div className="overflow-x-auto">
                  <table className="w-full text-left border-collapse">
                    <thead>
                      <tr className="bg-bg-secondary text-primary-600 text-sm uppercase tracking-wider">
                        <th className="p-4 font-semibold">#</th>
                        <th className="p-4 font-semibold">College</th>
                        <th className="p-4 font-semibold">Branch</th>
                        <th className="p-4 font-semibold">Type/Quota</th>
                        <th className="p-4 font-semibold">Chance</th>
                        <th className="p-4 font-semibold">Closing Rank</th>
                        <th className="p-4 font-semibold">Compare</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-primary-100">
                      {moderate.map((college, i) => {
                        const isCompared = selectedColleges.some(
                          (c) => c.name === college.name && c.branch === college.branch
                        );
                        return (
                          <tr key={`${college.name}-${college.branch}-${i}`} className="hover:bg-primary-50 transition-colors">
                            <td className="p-4 text-primary-500 font-medium">{i + 1}</td>
                            <td className="p-4 font-bold text-primary-900">
                              <div className="flex items-center gap-2">
                                <GraduationCap className="w-4 h-4 text-primary-400 shrink-0" />
                                <span className="line-clamp-2 max-w-xs">{college.name}</span>
                              </div>
                            </td>
                            <td className="p-4 text-primary-600 text-sm max-w-xs truncate" title={college.branch}>{college.branch}</td>
                            <td className="p-4">
                              <div className="flex flex-col gap-1 items-start">
                                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${TYPE_COLORS[college.type] || "bg-gray-100 text-gray-700"}`}>
                                  {college.type}
                                </span>
                                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-primary-100 text-primary-700">
                                  {college.quota}
                                </span>
                              </div>
                            </td>
                            <td className="p-4">
                              <div className="flex items-center gap-2">
                                <span className={`font-semibold ${chanceColor(college.chance)}`}>{college.chance}%</span>
                                <div className="w-16 h-1.5 bg-primary-100 rounded-full overflow-hidden">
                                  <div
                                    className="h-full bg-warning-500"
                                    style={{ width: `${college.chance}%` }}
                                  />
                                </div>
                              </div>
                            </td>
                            <td className="p-4 font-mono font-medium text-primary-700">
                              {college.closing_rank.toLocaleString()}
                            </td>
                            <td className="p-4">
                              <button
                                onClick={() => toggleCompare(college)}
                                className={`p-2 rounded-lg border transition-all cursor-pointer ${
                                  isCompared
                                    ? "bg-accent-500 border-accent-500 text-white shadow-sm"
                                    : "bg-white border-primary-200 text-primary-500 hover:border-accent-500 hover:text-accent-600"
                                }`}
                              >
                                <Scale className="w-4 h-4" />
                              </button>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>
            )}
          </section>

          {/* LOW CHANCE */}
          <section className="print:hidden">
            <div className="flex items-center justify-between mb-4 border-b border-primary-200 pb-2">
              <h3 className="text-xl font-bold text-danger-500">LOW CHANCE (&lt;40%)</h3>
              <span className="text-sm font-medium text-primary-500">{low.length} Colleges</span>
            </div>

            <Card
              className="border-primary-200 border-dashed bg-bg-secondary hover:bg-primary-50 transition-colors cursor-pointer"
              onClick={() => setShowLow((v) => !v)}
            >
              <CardContent className="p-4 flex items-center justify-center gap-2 text-primary-600 font-medium">
                {showLow ? (
                  <>Hide {low.length} colleges <ChevronUp className="w-4 h-4" /></>
                ) : (
                  <>Expand to view {low.length} more colleges <ChevronDown className="w-4 h-4" /></>
                )}
              </CardContent>
            </Card>

            {showLow && low.length > 0 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="mt-4"
              >
                <Card className="overflow-hidden border-primary-200">
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse">
                      <thead>
                        <tr className="bg-bg-secondary text-primary-600 text-xs uppercase tracking-wider">
                          <th className="p-3 font-semibold">#</th>
                          <th className="p-3 font-semibold">College</th>
                          <th className="p-3 font-semibold">Branch</th>
                          <th className="p-3 font-semibold">Chance</th>
                          <th className="p-3 font-semibold">Closing Rank</th>
                          <th className="p-3 font-semibold">Compare</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-primary-100">
                        {low.map((college, i) => {
                          const isCompared = selectedColleges.some(
                            (c) => c.name === college.name && c.branch === college.branch
                          );
                          return (
                            <tr key={`${college.name}-${college.branch}-${i}`} className="hover:bg-primary-50 transition-colors opacity-75">
                              <td className="p-3 text-primary-500 text-sm">{i + 1}</td>
                              <td className="p-3 font-medium text-primary-800 text-sm">{college.name}</td>
                              <td className="p-3 text-primary-600 text-sm">{college.branch}</td>
                              <td className="p-3">
                                <span className="text-danger-500 font-semibold text-sm">{college.chance}%</span>
                              </td>
                              <td className="p-3 font-mono text-primary-600 text-sm">{college.closing_rank.toLocaleString()}</td>
                              <td className="p-3">
                                <button
                                  onClick={() => toggleCompare(college)}
                                  className={`p-1.5 rounded-lg border transition-all cursor-pointer ${
                                    isCompared
                                      ? "bg-accent-500 border-accent-500 text-white shadow-sm"
                                      : "bg-white border-primary-200 text-primary-400 hover:border-accent-500 hover:text-accent-600"
                                  }`}
                                >
                                  <Scale className="w-3.5 h-3.5" />
                                </button>
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </Card>
              </motion.div>
            )}
          </section>

          {/* Placement Analytics component */}
          <PlacementAnalytics colleges={colleges} />

          {/* Choice Filling Optimizer component */}
          <ChoiceOptimizer colleges={colleges} examName={examId} />
        </>
      )}
    </div>
  );
}
