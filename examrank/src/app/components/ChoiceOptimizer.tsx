"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Card, CardContent } from "@/components/ui/Card";
import { ArrowUpDown, Download, Printer, Settings, Sparkles, Check, Trash2, ArrowUp, ArrowDown } from "lucide-react";
import { College, optimizeChoices } from "@/lib/api";
import { Button } from "@/components/ui/Button";
import { generateChoicePDF } from "@/lib/pdfGenerator";

interface Props {
  colleges: College[];
  examName?: string;
}

export default function ChoiceOptimizer({ colleges, examName = "College" }: Props) {
  const [optimizedList, setOptimizedList] = useState<College[]>([]);
  const [branchPreferences, setBranchPreferences] = useState<string[]>(["Computer Science", "IT", "Electronics"]);
  const [newPref, setNewPref] = useState("");
  const [studentName, setStudentName] = useState("");
  const [optimizing, setOptimizing] = useState(false);

  const handleOptimize = async () => {
    if (colleges.length === 0) return;
    setOptimizing(true);
    try {
      const data = await optimizeChoices(colleges, branchPreferences);
      setOptimizedList(data.colleges || []);
    } catch (err) {
      console.error("Failed to optimize choices:", err);
    } finally {
      setOptimizing(false);
    }
  };

  useEffect(() => {
    if (colleges.length > 0) {
      handleOptimize();
    } else {
      setOptimizedList([]);
    }
  }, [colleges]);

  const addPreference = (e: React.FormEvent) => {
    e.preventDefault();
    if (newPref.trim() && !branchPreferences.includes(newPref.trim())) {
      setBranchPreferences([...branchPreferences, newPref.trim()]);
      setNewPref("");
    }
  };

  const removePreference = (index: number) => {
    setBranchPreferences(branchPreferences.filter((_, i) => i !== index));
  };

  const moveItem = (index: number, direction: "up" | "down") => {
    const newList = [...optimizedList];
    const targetIdx = direction === "up" ? index - 1 : index + 1;
    if (targetIdx < 0 || targetIdx >= newList.length) return;
    
    // Swap
    const temp = newList[index];
    newList[index] = newList[targetIdx];
    newList[targetIdx] = temp;
    
    // Update choice numbers
    newList.forEach((item, idx) => {
      item.chance = newList[idx].chance; // Keep other props
      // Wait, we can add/overwrite choice_number
      (item as any).choice_number = idx + 1;
    });
    
    setOptimizedList(newList);
  };

  const downloadCSV = () => {
    if (optimizedList.length === 0) return;
    const headers = ["Choice Number", "Institute", "Branch", "Type", "Quota", "Chance (%)", "Closing Rank"];
    const rows = optimizedList.map((col, idx) => [
      idx + 1,
      `"${col.name}"`,
      `"${col.branch}"`,
      col.type,
      col.quota,
      `${col.chance}%`,
      col.closing_rank
    ]);
    
    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
      
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "optimized_college_choices.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const printPDF = () => {
    if (optimizedList.length === 0) return;
    generateChoicePDF(studentName, examName, optimizedList);
  };

  if (colleges.length === 0) return null;

  return (
    <div className="w-full max-w-5xl mx-auto mt-12 mb-10 print:mt-0 print:mb-0">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6 print:hidden">
        <div>
          <h2 className="text-3xl font-bold text-primary-900 flex items-center gap-3">
            <ArrowUpDown className="w-8 h-8 text-info-500" />
            Choice Filling Optimizer
          </h2>
          <p className="text-primary-500 text-sm mt-1">
            Sorts choices based on college tiers, branch priorities, and probability of admission.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 items-end sm:items-center">
          <input 
            type="text" 
            placeholder="Student Name (for PDF)" 
            value={studentName}
            onChange={(e) => setStudentName(e.target.value)}
            className="px-3 py-2 text-sm rounded-lg border border-primary-200 focus:outline-none focus:border-accent-500 max-w-[200px]"
          />
          <Button
            onClick={downloadCSV}
            variant="outline"
            className="flex items-center gap-2 border-primary-200 text-primary-700 bg-white"
          >
            <Download className="w-4 h-4" />
            CSV
          </Button>
          <Button
            onClick={printPDF}
            className="flex items-center gap-2 bg-gradient-to-r from-accent-500 to-info-500 text-white shadow-lg shadow-info-500/20"
          >
            <Printer className="w-4 h-4" />
            Premium PDF
          </Button>
        </div>
      </div>

      {/* Preferences Setup */}
      <Card className="mb-6 border-primary-200/60 shadow-lg bg-white/75 backdrop-blur-xl print:hidden">
        <CardContent className="p-6">
          <h3 className="text-base font-bold text-primary-900 flex items-center gap-2 mb-3">
            <Settings className="w-4 h-4 text-primary-400" />
            Custom Branch Preferences (Drag/Reorder Prioritizer)
          </h3>
          <form onSubmit={addPreference} className="flex gap-3 mb-4">
            <input
              type="text"
              placeholder="e.g. Computer Science, Mechanical, ECE"
              value={newPref}
              onChange={(e) => setNewPref(e.target.value)}
              className="flex-1 px-4 py-2 text-sm rounded-xl border border-primary-200 focus:outline-none focus:border-accent-500 bg-white"
            />
            <Button type="submit" variant="primary" className="bg-accent-500 hover:bg-accent-600 text-white">
              Add Branch
            </Button>
          </form>

          <div className="flex flex-wrap gap-2">
            {branchPreferences.map((pref, idx) => (
              <span
                key={`${pref}-${idx}`}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-primary-100/80 text-primary-800 text-xs font-bold border border-primary-200"
              >
                <span>{idx + 1}. {pref}</span>
                <button
                  type="button"
                  onClick={() => removePreference(idx)}
                  className="hover:text-danger-500 transition-colors"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </span>
            ))}
          </div>

          <div className="mt-4 flex justify-end">
            <Button
              onClick={handleOptimize}
              disabled={optimizing}
              className="bg-primary-900 text-white font-bold px-5 py-2.5 rounded-xl hover:bg-primary-800 transition-all flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4 text-yellow-400 animate-pulse" />
              {optimizing ? "Re-Optimizing..." : "Apply & Optimize Choices"}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Main List */}
      <Card className="border-primary-200 shadow-xl overflow-hidden bg-white">
        <div className="p-4 bg-bg-secondary border-b border-primary-200 flex justify-between items-center print:bg-white print:border-none">
          <h3 className="font-bold text-primary-900 print:text-xl">Optimized Sequence Choice List</h3>
          <span className="text-sm font-semibold text-primary-500 print:hidden">{optimizedList.length} Choices</span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-primary-50/50 text-primary-600 text-xs uppercase tracking-wider print:bg-transparent">
                <th className="p-4 font-bold">Choice #</th>
                <th className="p-4 font-bold">College / Institute</th>
                <th className="p-4 font-bold">Branch Name</th>
                <th className="p-4 font-bold">Type</th>
                <th className="p-4 font-bold">Admission Chance</th>
                <th className="p-4 font-bold">Closing Rank</th>
                <th className="p-4 font-bold print:hidden">Reorder</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-primary-100">
              <AnimatePresence initial={false}>
                {optimizedList.map((college, idx) => (
                  <motion.tr
                    key={`${college.name}-${college.branch}-${idx}`}
                    layout
                    className="hover:bg-primary-50/40 transition-colors"
                  >
                    <td className="p-4 font-bold text-primary-800 text-sm">
                      #{idx + 1}
                    </td>
                    <td className="p-4 font-bold text-primary-900">
                      <span className="line-clamp-2 max-w-sm">{college.name}</span>
                    </td>
                    <td className="p-4 text-primary-700 text-sm font-medium">
                      {college.branch}
                    </td>
                    <td className="p-4 text-xs font-bold">
                      <span className="px-2.5 py-1 rounded-full bg-primary-100 text-primary-700 border border-primary-200/50">
                        {college.type}
                      </span>
                    </td>
                    <td className="p-4">
                      <span className={`font-semibold ${college.chance >= 80 ? "text-success-600" : college.chance >= 40 ? "text-warning-500" : "text-danger-500"}`}>
                        {college.chance}%
                      </span>
                    </td>
                    <td className="p-4 font-mono text-primary-700 text-sm">
                      {college.closing_rank.toLocaleString()}
                    </td>
                    <td className="p-4 print:hidden">
                      <div className="flex gap-1">
                        <button
                          onClick={() => moveItem(idx, "up")}
                          disabled={idx === 0}
                          className="p-1.5 rounded-lg border border-primary-200 hover:bg-primary-100 text-primary-500 disabled:opacity-30 disabled:hover:bg-transparent"
                        >
                          <ArrowUp className="w-3.5 h-3.5" />
                        </button>
                        <button
                          onClick={() => moveItem(idx, "down")}
                          disabled={idx === optimizedList.length - 1}
                          className="p-1.5 rounded-lg border border-primary-200 hover:bg-primary-100 text-primary-500 disabled:opacity-30 disabled:hover:bg-transparent"
                        >
                          <ArrowDown className="w-3.5 h-3.5" />
                        </button>
                      </div>
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
