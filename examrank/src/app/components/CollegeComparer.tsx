"use client";

import { motion } from "framer-motion";
import { Card, CardContent } from "@/components/ui/Card";
import { X, Scale, Sparkles, TrendingUp, BarChart2 } from "lucide-react";
import { College, getTrends } from "@/lib/api";
import { useState, useEffect } from "react";
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip } from "recharts";
import TrendVisualizer from "./TrendVisualizer";

interface Props {
  selectedColleges: College[];
  onRemove: (college: College) => void;
  examId: string;
  category: string;
}

const TYPE_COLORS: Record<string, string> = {
  NIT: "bg-blue-500/15 text-blue-400 border border-blue-500/30",
  IIIT: "bg-purple-500/15 text-purple-400 border border-purple-500/30",
  GFTI: "bg-emerald-500/15 text-emerald-400 border border-emerald-500/30",
  Private: "bg-amber-500/15 text-amber-400 border border-amber-500/30",
  IIT: "bg-indigo-500/15 text-indigo-400 border border-indigo-500/30",
  AIIMS: "bg-rose-500/15 text-rose-400 border border-rose-500/30",
  JIPMER: "bg-pink-500/15 text-pink-400 border border-pink-500/30",
  Medical: "bg-red-500/15 text-red-400 border border-red-500/30",
  "Govt Medical": "bg-red-500/15 text-red-400 border border-red-500/30",
  Engineering: "bg-blue-500/15 text-blue-400 border border-blue-500/30",
  "Private Engineering": "bg-amber-500/15 text-amber-400 border border-amber-500/30",
};

export default function CollegeComparer({ selectedColleges, onRemove, examId, category }: Props) {
  const [trends, setTrends] = useState<Record<string, any[]>>({});
  const [loadingTrends, setLoadingTrends] = useState<Record<string, boolean>>({});
  const [activeTrendCollege, setActiveTrendCollege] = useState<string | null>(null);

  useEffect(() => {
    selectedColleges.forEach((col) => {
      const key = `${col.name}-${col.branch}`;
      if (!trends[key] && !loadingTrends[key]) {
        setLoadingTrends((prev) => ({ ...prev, [key]: true }));
        getTrends(examId, col.name, col.branch, category, col.quota)
          .then((data) => {
            setTrends((prev) => ({ ...prev, [key]: data.trends }));
          })
          .catch((err) => console.error("Error loading trends for comparator:", err))
          .finally(() => {
            setLoadingTrends((prev) => ({ ...prev, [key]: false }));
          });
      }
    });
  }, [selectedColleges, examId, category]);

  if (selectedColleges.length === 0) return null;

  return (
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-5xl mx-auto mt-10"
    >
      <div className="flex items-center gap-3 mb-6">
        <Scale className="w-8 h-8 text-accent-500" />
        <h3 className="text-2xl font-bold text-primary-900">Compare Selected Colleges ({selectedColleges.length}/3)</h3>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {selectedColleges.map((college, idx) => {
          const trendKey = `${college.name}-${college.branch}`;
          const collegeTrends = trends[trendKey] || [];
          const isTrendLoading = loadingTrends[trendKey];

          return (
            <motion.div
              key={`${college.name}-${college.branch}-${idx}`}
              layout
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.9 }}
              className="relative overflow-hidden bg-white/60 backdrop-blur-xl border border-primary-200/80 rounded-3xl p-6 shadow-xl hover:shadow-2xl transition-all duration-300 group flex flex-col justify-between"
            >
              <button
                onClick={() => onRemove(college)}
                className="absolute top-4 right-4 p-1.5 rounded-full bg-primary-100 hover:bg-danger-100 text-primary-500 hover:text-danger-600 transition-colors z-10"
              >
                <X className="w-4 h-4" />
              </button>

              <div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${TYPE_COLORS[college.type] || "bg-primary-100 text-primary-700"} mb-3 inline-block`}>
                  {college.type}
                </span>

                <h4 className="text-lg font-bold text-primary-900 pr-6 mb-1 line-clamp-2">{college.name}</h4>
                <p className="text-primary-600 text-sm font-medium mb-4">{college.branch}</p>

                <div className="space-y-3 pt-4 border-t border-primary-100">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-primary-400">Admission Chance</span>
                    <span className={`font-bold ${college.chance >= 80 ? "text-success-600" : college.chance >= 40 ? "text-warning-500" : "text-danger-500"}`}>
                      {college.chance}%
                    </span>
                  </div>

                  <div className="flex justify-between items-center text-sm">
                    <span className="text-primary-400">Closing Rank</span>
                    <span className="font-mono font-bold text-primary-800">{college.closing_rank.toLocaleString()}</span>
                  </div>

                  <div className="flex justify-between items-center text-sm">
                    <span className="text-primary-400">Opening Rank</span>
                    <span className="font-mono font-bold text-primary-700">{college.opening_rank.toLocaleString()}</span>
                  </div>

                  <div className="flex justify-between items-center text-sm">
                    <span className="text-primary-400">Quota</span>
                    <span className="font-medium text-primary-600 bg-primary-50 px-2 py-0.5 rounded text-xs">{college.quota || "All India"}</span>
                  </div>
                </div>
              </div>

              <div className="mt-6">
                {collegeTrends.length > 0 ? (
                  <div>
                    <button
                      onClick={() => setActiveTrendCollege(activeTrendCollege === trendKey ? null : trendKey)}
                      className="w-full flex items-center justify-center gap-2 py-2 px-3 text-xs font-bold rounded-xl border border-accent-500/20 bg-accent-50/50 hover:bg-accent-500 hover:text-white text-accent-700 transition-all"
                    >
                      <TrendingUp className="w-3.5 h-3.5" />
                      {activeTrendCollege === trendKey ? "Hide Trend Graph" : "View Cutoff Trends"}
                    </button>

                    {activeTrendCollege === trendKey && (
                      <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        className="mt-4 bg-primary-50/50 p-2 rounded-2xl border border-primary-100"
                      >
                        <p className="text-[10px] font-bold text-primary-500 text-center mb-2">Historical Closing Ranks</p>
                        <div className="h-[120px] w-full">
                          <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={collegeTrends} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                              <XAxis dataKey="year" fontSize={9} tickLine={false} tick={{ fill: "#64748b" }} />
                              <YAxis fontSize={9} tickLine={false} tick={{ fill: "#64748b" }} />
                              <Tooltip
                                contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)", fontSize: 10 }}
                                formatter={(value: any) => [value.toLocaleString(), "Closing Rank"]}
                              />
                              <Line
                                type="monotone"
                                dataKey="closing_rank"
                                stroke="#3b82f6"
                                strokeWidth={2}
                                dot={{ r: 3, fill: "#3b82f6" }}
                              />
                            </LineChart>
                          </ResponsiveContainer>
                        </div>
                      </motion.div>
                    )}
                  </div>
                ) : isTrendLoading ? (
                  <div className="text-center py-2 text-xs text-primary-400 font-medium">Loading trends...</div>
                ) : (
                  <div className="text-center py-2 text-xs text-primary-400 italic">No trend data available</div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      <TrendVisualizer selectedColleges={selectedColleges} trends={trends} />
    </motion.div>
  );
}
