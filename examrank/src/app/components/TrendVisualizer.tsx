"use client";

import React, { useMemo } from "react";
import { Card, CardContent } from "@/components/ui/Card";
import { ResponsiveContainer, LineChart, Line, CartesianGrid, XAxis, YAxis, Tooltip, Legend } from "recharts";
import { TrendingUp, AlertCircle } from "lucide-react";
import { College } from "@/lib/api";

interface Props {
  selectedColleges: College[];
  trends: Record<string, any[]>;
}

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ef4444"];

export default function TrendVisualizer({ selectedColleges, trends }: Props) {
  // Process data for the overlay chart
  const chartData = useMemo(() => {
    // Collect all unique years
    const yearSet = new Set<number>();
    Object.values(trends).forEach((collegeTrends) => {
      collegeTrends.forEach((t) => yearSet.add(t.year));
    });

    const years = Array.from(yearSet).sort((a, b) => a - b);

    // Build data points per year
    return years.map((year) => {
      const dataPoint: any = { year };
      selectedColleges.forEach((college) => {
        const key = `${college.name}-${college.branch}`;
        const collegeTrends = trends[key] || [];
        const yearTrend = collegeTrends.find((t) => t.year === year);
        if (yearTrend) {
          dataPoint[key] = yearTrend.closing_rank;
        }
      });
      return dataPoint;
    });
  }, [trends, selectedColleges]);

  if (selectedColleges.length === 0 || chartData.length === 0) return null;

  return (
    <Card className="mt-8 overflow-hidden border-primary-200/80 shadow-xl bg-white/80 backdrop-blur-xl">
      <div className="p-4 bg-primary-50/50 border-b border-primary-100 flex items-center justify-between">
        <h3 className="text-xl font-bold text-primary-900 flex items-center gap-2">
          <TrendingUp className="w-6 h-6 text-accent-500" />
          Interactive Cutoff Trend Visualizer
        </h3>
        <div className="flex items-center gap-2 text-xs font-bold bg-white px-3 py-1.5 rounded-full border border-primary-200 text-primary-600 shadow-sm">
          <AlertCircle className="w-4 h-4 text-warning-500" />
          Lower rank means higher competition
        </div>
      </div>
      <CardContent className="p-6">
        <div className="h-[400px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 10 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis 
                dataKey="year" 
                tick={{ fill: "#64748b", fontWeight: 600 }} 
                tickLine={false} 
                axisLine={{ stroke: "#cbd5e1" }}
              />
              <YAxis 
                tick={{ fill: "#64748b", fontWeight: 600 }} 
                tickLine={false} 
                axisLine={{ stroke: "#cbd5e1" }}
                domain={['auto', 'auto']}
                reversed={true} // lower rank is better, so put it at the top
              />
              <Tooltip
                contentStyle={{ borderRadius: "12px", border: "1px solid #e2e8f0", boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)", fontWeight: 500 }}
                formatter={(value: any) => [value.toLocaleString(), "Closing Rank"]}
              />
              <Legend 
                wrapperStyle={{ paddingTop: "20px" }}
                formatter={(value) => <span className="text-sm font-semibold text-primary-700">{value}</span>}
              />
              {selectedColleges.map((college, idx) => {
                const key = `${college.name}-${college.branch}`;
                return (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    name={`${college.name} (${college.branch})`}
                    stroke={COLORS[idx % COLORS.length]}
                    strokeWidth={3}
                    dot={{ r: 4, fill: COLORS[idx % COLORS.length], strokeWidth: 2, stroke: "#fff" }}
                    activeDot={{ r: 6, strokeWidth: 0 }}
                    connectNulls
                  />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
