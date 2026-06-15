"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/Card";
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  LineChart, Line, CartesianGrid,
} from "recharts";
import { Activity } from "lucide-react";
import { JEEPredictionResponse } from "@/lib/api";
import { PredictionMeta } from "../page";

interface Props {
  predictionData: JEEPredictionResponse | null;
  meta: PredictionMeta | null;
}

// Historical percentile trend (static — not user-specific)
const trendData = [
  { year: "2020", percentile: 98.8 },
  { year: "2021", percentile: 99.0 },
  { year: "2022", percentile: 99.1 },
  { year: "2023", percentile: 99.3 },
  { year: "2024", percentile: 99.5 },
  { year: "2025", percentile: 99.6 },
];

function subjectEstimate(marks: number, maxMarks: number) {
  // Estimate subject scores heuristically (equal distribution with slight variation)
  const base = marks / maxMarks;
  const physics     = Math.min(100, Math.round((base * 0.95 + 0.05) * (maxMarks / 3)));
  const chemistry   = Math.min(100, Math.round((base * 1.05 - 0.02) * (maxMarks / 3)));
  const mathematics = Math.max(0, marks - physics - chemistry);
  return { physics, chemistry, mathematics };
}

function accuracyFromMarks(marks: number, maxMarks: number) {
  return ((marks / maxMarks) * 100).toFixed(1);
}

function bracketFromPercentile(pct: number) {
  if (pct >= 99.5) return "Top 0.5%";
  if (pct >= 99)   return "Top 1%";
  if (pct >= 95)   return "Top 5%";
  if (pct >= 90)   return "Top 10%";
  if (pct >= 75)   return "Top 25%";
  return "Top 50%";
}

export default function AnalyticsDashboard({ predictionData, meta }: Props) {
  const marks      = meta?.marks ?? 0;
  const maxMarks   = meta?.maxMarks ?? 300;
  const shift      = meta?.shift ?? "shift1";
  const percentile = predictionData?.percentile ?? ((marks / maxMarks) * 100 * 0.997);

  const { physics, chemistry, mathematics } = subjectEstimate(marks, maxMarks);
  const accuracy = accuracyFromMarks(marks, maxMarks);
  const bracket  = bracketFromPercentile(percentile);

  // Shift comparison — user's shift is highlighted
  const shiftData = [
    { name: "Shift 1", marks: 156, fill: shift === "shift1" ? "#10b981" : "#e2e8f0" },
    { name: "Shift 2", marks: 142, fill: shift === "shift2" ? "#10b981" : "#e2e8f0" },
    { name: "You",     marks: Math.round(predictionData?.normalized_marks ?? marks), fill: "#3b82f6" },
  ];

  const subjectMax = Math.round(maxMarks / 3);

  return (
    <div className="w-full max-w-5xl mx-auto mt-12 mb-20 space-y-8">
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-8 h-8 text-info-500" />
        <h2 className="text-3xl font-bold text-primary-900">Shift-wise Analysis</h2>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Performance card */}
        <Card className="border-primary-200">
          <CardHeader>
            <CardTitle className="text-lg">Your Performance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center justify-between p-4 bg-bg-secondary rounded-xl mb-6">
              <div className="text-center">
                <div className="text-xs text-primary-500 uppercase font-bold mb-1">Score</div>
                <div className="text-2xl font-bold text-primary-900">
                  {marks}
                  <span className="text-sm text-primary-400">/{maxMarks}</span>
                </div>
              </div>
              <div className="w-px h-10 bg-primary-200" />
              <div className="text-center">
                <div className="text-xs text-primary-500 uppercase font-bold mb-1">Accuracy</div>
                <div className="text-2xl font-bold text-info-500">{accuracy}%</div>
              </div>
              <div className="w-px h-10 bg-primary-200" />
              <div className="text-center">
                <div className="text-xs text-primary-500 uppercase font-bold mb-1">Bracket</div>
                <div className="text-xl font-bold text-gold-500">{bracket}</div>
              </div>
            </div>

            <h4 className="text-sm font-bold text-primary-700 mb-3">
              Estimated Subject Breakdown
              <span className="text-xs font-normal text-primary-400 ml-2">(equal weight)</span>
            </h4>
            <div className="space-y-4">
              {[
                { name: "Physics",     score: physics,     color: "bg-accent-500", max: subjectMax },
                { name: "Chemistry",   score: chemistry,   color: "bg-info-500",   max: subjectMax },
                { name: "Mathematics", score: mathematics, color: "bg-warning-500", max: subjectMax },
              ].map(({ name, score, color, max }) => (
                <div key={name}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-primary-800">{name}</span>
                    <span className="font-bold">{score}<span className="text-primary-400 font-normal">/{max}</span></span>
                  </div>
                  <div className="h-2 bg-primary-100 rounded-full overflow-hidden">
                    <div
                      className={`h-full ${color} transition-all duration-700`}
                      style={{ width: `${Math.min(100, (score / max) * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Shift comparison chart */}
        <Card className="border-primary-200">
          <CardHeader>
            <CardTitle className="text-lg">Shift Comparison (Average vs Your Score)</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col h-[300px]">
            <div className="flex-1 min-h-[200px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart
                  data={shiftData}
                  layout="vertical"
                  margin={{ top: 0, right: 30, left: 0, bottom: 0 }}
                >
                  <XAxis type="number" hide />
                  <YAxis
                    dataKey="name"
                    type="category"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: "#475569", fontSize: 13, fontWeight: 600 }}
                    width={70}
                  />
                  <Tooltip
                    cursor={{ fill: "#f1f5f9" }}
                    contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)" }}
                    formatter={(v: any) => [v, "Marks"]}
                  />
                  <Bar dataKey="marks" radius={[0, 6, 6, 0]} barSize={26} fill="#e2e8f0" />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-4 p-3 bg-info-50 rounded-lg border border-info-100 flex items-center justify-between">
              <span className="text-sm font-medium text-info-700">
                Your Normalized Score ({shift.replace(/([a-z])(\d)/i, "$1 $2")})
              </span>
              <span className="text-lg font-bold text-info-600">
                {(predictionData?.normalized_marks ?? marks).toFixed(1)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Percentile trend */}
      <Card className="border-primary-200">
        <CardHeader>
          <CardTitle className="text-lg">Historical Top Percentile Trend (2020–2025)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[250px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="year" axisLine={false} tickLine={false} tick={{ fill: "#64748b" }} dy={10} />
                <YAxis
                  domain={["dataMin - 0.2", "dataMax + 0.1"]}
                  axisLine={false}
                  tickLine={false}
                  tick={{ fill: "#64748b" }}
                  dx={-10}
                />
                <Tooltip
                  contentStyle={{ borderRadius: "8px", border: "none", boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)" }}
                  formatter={(value: any) => [`${value}%ile`, "Percentile"]}
                />
                <Line
                  type="monotone"
                  dataKey="percentile"
                  stroke="#f59e0b"
                  strokeWidth={3}
                  dot={{ r: 6, fill: "#f59e0b", strokeWidth: 2, stroke: "#fff" }}
                  activeDot={{ r: 8 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-4 text-center text-sm font-medium text-primary-600 bg-gold-50 p-3 rounded-lg border border-gold-100">
            <span className="font-bold text-gold-600">
              Your Percentile: {Number(percentile).toFixed(2)}%
            </span>{" "}
            — {bracketFromPercentile(percentile)} of all {meta?.examLabel ?? "JEE Main"} candidates.
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
