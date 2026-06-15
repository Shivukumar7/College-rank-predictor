"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Input } from "@/components/ui/Input";
import { predictExam, JEEPredictionResponse } from "@/lib/api";
import { PredictionMeta } from "../page";

interface HeroProps {
  onPredict: (prediction: JEEPredictionResponse | null, meta: PredictionMeta) => void;
}

interface ExamConfig {
  id: string;
  label: string;
  fullName: string;
  maxMarks: number;
  color: string;
  badge?: string;
  shifts: { value: string; label: string }[];
  live: boolean;
}

const EXAMS: ExamConfig[] = [
  {
    id: "jee-main",
    label: "JEE Main",
    fullName: "JEE Main 2026",
    maxMarks: 300,
    color: "from-blue-500 to-indigo-600",
    shifts: [
      { value: "shift1", label: "Shift 1 (Morning)" },
      { value: "shift2", label: "Shift 2 (Evening)" },
    ],
    live: true,
  },
  {
    id: "jee-adv",
    label: "JEE Adv",
    fullName: "JEE Advanced 2026",
    maxMarks: 360,
    color: "from-violet-500 to-purple-700",
    shifts: [
      { value: "paper1", label: "Paper 1" },
      { value: "paper2", label: "Paper 2" },
    ],
    live: true,
  },
  {
    id: "neet",
    label: "NEET",
    fullName: "NEET UG 2026",
    maxMarks: 720,
    color: "from-rose-500 to-pink-700",
    shifts: [{ value: "single", label: "Single Session" }],
    live: true,
  },
  {
    id: "kcet",
    label: "KCET",
    fullName: "KCET 2026",
    maxMarks: 180,
    color: "from-amber-500 to-orange-600",
    shifts: [
      { value: "day1", label: "Day 1" },
      { value: "day2", label: "Day 2" },
    ],
    live: true,
  },
  {
    id: "mht-cet",
    label: "MHT-CET",
    fullName: "MHT-CET 2026",
    maxMarks: 200,
    color: "from-teal-500 to-emerald-600",
    shifts: [
      { value: "pcm", label: "PCM Group" },
      { value: "pcb", label: "PCB Group" },
    ],
    live: true,
  },
  {
    id: "comedk",
    label: "COMEDK",
    fullName: "COMEDK UGET 2026",
    maxMarks: 180,
    color: "from-cyan-500 to-sky-600",
    shifts: [{ value: "single", label: "Single Session" }],
    live: true,
  },
  {
    id: "bitsat",
    label: "BITSAT",
    fullName: "BITSAT 2026",
    maxMarks: 390,
    color: "from-fuchsia-500 to-pink-600",
    badge: "Soon",
    shifts: [
      { value: "session1", label: "Session 1" },
      { value: "session2", label: "Session 2" },
    ],
    live: false,
  },
  {
    id: "gate",
    label: "GATE",
    fullName: "GATE 2027",
    maxMarks: 100,
    color: "from-slate-500 to-gray-700",
    badge: "Soon",
    shifts: [{ value: "single", label: "Single Paper" }],
    live: false,
  },
];

const CATEGORIES = [
  { value: "general", label: "General (UR)" },
  { value: "ews",     label: "EWS" },
  { value: "obc",     label: "OBC-NCL" },
  { value: "sc",      label: "SC" },
  { value: "st",      label: "ST" },
  { value: "pwd",     label: "PwD" },
];

const KCET_VERTICAL_CATEGORIES = [
  { value: "GM", label: "General Merit (GM)" },
  { value: "SC", label: "Scheduled Caste (SC)" },
  { value: "ST", label: "Scheduled Tribe (ST)" },
  { value: "1", label: "Category I (Cat-I)" },
  { value: "2A", label: "Category 2A (2A)" },
  { value: "2B", label: "Category 2B (2B)" },
  { value: "3A", label: "Category 3A (3A)" },
  { value: "3B", label: "Category 3B (3B)" },
];

const KCET_HORIZONTAL_CATEGORIES = [
  { value: "G", label: "General (No Special Quota)" },
  { value: "K", label: "Kannada Medium" },
  { value: "R", label: "Rural" },
];

const selectClass =
  "w-full bg-black/40 border border-white/[0.08] text-white rounded-2xl p-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-400/50 focus:border-transparent transition-all hover:bg-white/[0.06] backdrop-blur-sm";
const optionClass = "text-primary-900 bg-white";

export default function Hero({ onPredict }: HeroProps) {
  const [selectedExam, setSelectedExam] = useState<ExamConfig>(EXAMS[0]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [comingSoon, setComingSoon] = useState(false);

  const handleExamSelect = (exam: ExamConfig) => {
    setSelectedExam(exam);
    setError(null);
    setComingSoon(false);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError(null);
    setComingSoon(false);

    const formData = new FormData(e.currentTarget);
    const marks    = Number(formData.get("marks"));
    
    let shift    = (formData.get("shift") as string) || "day1";
    let category = (formData.get("category") as string) || "general";
    let boardMarks: number | undefined = undefined;

    if (selectedExam.id === "kcet") {
      const boardMarksStr = formData.get("board_marks") as string;
      if (boardMarksStr) {
        boardMarks = Number(boardMarksStr);
      }
      const vertical = formData.get("kcet_vertical") as string;
      const horizontal = formData.get("kcet_horizontal") as string;
      if (vertical === "GM" && horizontal === "G") {
        category = "GM";
      } else {
        category = `${vertical}${horizontal}`;
      }
      shift = "day1";
    }

    const meta: PredictionMeta = {
      marks,
      maxMarks: selectedExam.maxMarks,
      shift,
      category,
      examId: selectedExam.id,
      examLabel: selectedExam.fullName,
      boardMarks,
    };

    if (!selectedExam.live) {
      setComingSoon(true);
      return;
    }

    setIsLoading(true);
    try {
      const examIdApi = selectedExam.id === "jee-adv" ? "jee-advanced" : selectedExam.id;
      const prediction = await predictExam(examIdApi, {
        marks,
        shift,
        category,
        board_marks: boardMarks
      });
      onPredict(prediction, meta);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Prediction failed. Please try again.");
      // Still navigate to results with null prediction so we show estimated data
      onPredict(null, meta);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="relative flex flex-col items-center justify-center min-h-screen overflow-hidden bg-black text-white">
      {/* ── Fluid 3D Spheres ── */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Sphere 1: Large Cyan */}
        <div
          className="absolute w-[45vw] h-[45vw] rounded-full animate-fluid-1"
          style={{
            top: '5%',
            left: '-10%',
            background: 'radial-gradient(circle at 35% 35%, #22d3ee, #06b6d4 40%, #0e7490 70%, transparent 100%)',
            filter: 'blur(60px)',
            opacity: 0.5,
          }}
        />
        {/* Sphere 2: Large Magenta / Fuchsia */}
        <div
          className="absolute w-[40vw] h-[40vw] rounded-full animate-fluid-2"
          style={{
            top: '30%',
            right: '-5%',
            background: 'radial-gradient(circle at 65% 35%, #e879f9, #c026d3 40%, #86198f 70%, transparent 100%)',
            filter: 'blur(50px)',
            opacity: 0.45,
          }}
        />
        {/* Sphere 3: Medium Violet-Blue */}
        <div
          className="absolute w-[35vw] h-[35vw] rounded-full animate-fluid-3"
          style={{
            bottom: '-5%',
            left: '25%',
            background: 'radial-gradient(circle at 50% 40%, #818cf8, #6366f1 40%, #4338ca 70%, transparent 100%)',
            filter: 'blur(70px)',
            opacity: 0.4,
          }}
        />
        {/* Sphere 4: Small warm accent */}
        <div
          className="absolute w-[20vw] h-[20vw] rounded-full animate-fluid-1 [animation-delay:5s]"
          style={{
            top: '60%',
            left: '5%',
            background: 'radial-gradient(circle at 50% 50%, #fb923c, #ea580c 50%, transparent 100%)',
            filter: 'blur(40px)',
            opacity: 0.3,
          }}
        />
      </div>

      {/* Fine grain noise texture */}
      <div className="absolute inset-0 opacity-[0.03] pointer-events-none" style={{ backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=\'0 0 256 256\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cfilter id=\'noise\'%3E%3CfeTurbulence type=\'fractalNoise\' baseFrequency=\'0.9\' numOctaves=\'4\' stitchTiles=\'stitch\'/%3E%3C/filter%3E%3Crect width=\'100%25\' height=\'100%25\' filter=\'url(%23noise)\'/%3E%3C/svg%3E")', backgroundRepeat: 'repeat', backgroundSize: '128px 128px' }} />

      <div className="relative z-10 w-full max-w-5xl px-4 text-center mt-12 mb-12">
        {/* Headline */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
        >
          <h1 className="font-display text-5xl md:text-7xl font-extrabold mb-5 tracking-tight leading-[1.1]">
            <span className="text-white/90">Predict Your Rank.</span> <br />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 via-fuchsia-400 to-violet-400">
              Shape Your Future.
            </span>
          </h1>
          <p className="text-lg md:text-xl text-white/50 mb-10 max-w-2xl mx-auto font-medium">
            AI-powered predictions built on 15 years of historical data for India&apos;s top exams.
          </p>
        </motion.div>

        {/* Exam Picker — Frosted glass pill bar */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.15 }}
          className="flex flex-wrap justify-center gap-1.5 mb-10 relative z-10 p-2 bg-white/[0.04] backdrop-blur-xl rounded-[20px] border border-white/[0.08] shadow-[0_4px_30px_rgba(0,0,0,0.4)]"
        >
          {EXAMS.map((exam) => {
            const isActive = selectedExam.id === exam.id;
            return (
              <button
                key={exam.id}
                type="button"
                onClick={() => handleExamSelect(exam)}
                className={`relative px-5 py-2.5 rounded-2xl text-sm font-semibold transition-all duration-300 z-10
                  ${isActive
                    ? 'text-white'
                    : 'text-white/40 hover:text-white/70'
                  }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="activeExam"
                    className="absolute inset-0 rounded-2xl -z-10 border border-white/[0.15] bg-white/[0.08] backdrop-blur-md shadow-[0_0_25px_rgba(34,211,238,0.15),inset_0_1px_0_rgba(255,255,255,0.1)]"
                    transition={{ type: "spring", stiffness: 350, damping: 30 }}
                  />
                )}
                <span className="relative z-10">{exam.label}</span>
                {exam.badge && (
                  <span className="absolute -top-2 -right-2 bg-gradient-to-r from-cyan-400 to-fuchsia-400 text-black text-[9px] font-extrabold px-1.5 py-0.5 rounded-full leading-none shadow-lg z-20">
                    {exam.badge}
                  </span>
                )}
              </button>
            );
          })}
        </motion.div>

        {/* Form Card — Heavy frosted glass with glowing gradient border */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 20 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.25, ease: [0.16, 1, 0.3, 1] }}
          className="relative max-w-xl w-full mx-auto"
        >
          {/* Animated gradient border glow */}
          <div className="absolute -inset-[1px] rounded-[28px] bg-gradient-to-br from-cyan-400/40 via-fuchsia-500/30 to-violet-500/40 blur-sm opacity-60 -z-10 pointer-events-none" />
          <div className="absolute -inset-[2px] rounded-[28px] bg-gradient-to-br from-cyan-400/20 via-fuchsia-500/15 to-violet-500/20 blur-xl opacity-40 -z-20 pointer-events-none" />

          {/* Glass card body */}
          <div className="relative bg-black/50 backdrop-blur-3xl border border-white/[0.08] rounded-[28px] p-8 shadow-[0_16px_64px_rgba(0,0,0,0.5),inset_0_1px_0_rgba(255,255,255,0.05)]">

          {/* Selected exam header */}
          <div className="flex items-center gap-3 mb-6 px-5 py-4 rounded-2xl bg-white/[0.04] border border-white/[0.06]">
            <div className="flex-1 text-left">
              <div className="text-[10px] font-semibold text-white/40 uppercase tracking-[0.2em]">Selected Exam</div>
              <div className="text-lg font-bold text-white/90">{selectedExam.fullName}</div>
            </div>
            <div className="text-right">
              <div className="text-[10px] font-semibold text-white/40 uppercase tracking-[0.2em]">Max Marks</div>
              <div className="text-lg font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-300 to-fuchsia-300">{selectedExam.maxMarks}</div>
            </div>
          </div>

          <AnimatePresence mode="wait">
            {comingSoon ? (
              <motion.div
                key="coming-soon"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="text-center py-6"
              >
                <div className="text-5xl mb-3">🚀</div>
                <h3 className="text-xl font-bold text-white mb-2">
                  {selectedExam.fullName} — Coming Soon!
                </h3>
                <p className="text-primary-300 text-sm mb-4">
                  We&apos;re training our models on historical data for this exam. Stay tuned!
                </p>
                <button
                  onClick={() => setComingSoon(false)}
                  className="text-accent-400 text-sm font-semibold underline underline-offset-2"
                >
                  ← Go back
                </button>
              </motion.div>
            ) : (
              <motion.form
                key={`form-${selectedExam.id}`}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ staggerChildren: 0.1, delayChildren: 0.1 }}
                className="flex flex-col gap-4 relative z-10"
                onSubmit={handleSubmit}
              >
                {error && (
                  <div className="bg-danger-500/20 text-danger-500 border border-danger-500/50 p-3 rounded-md text-sm">
                    {error}
                  </div>
                )}

                <Input
                  name="marks"
                  type="number"
                  placeholder={selectedExam.id === "kcet" ? `KCET Marks (out of ${selectedExam.maxMarks})` : `Your Marks (out of ${selectedExam.maxMarks})`}
                  glass
                  required
                  min={0}
                  max={selectedExam.maxMarks}
                  className="text-lg py-6"
                />

                {selectedExam.id === "kcet" && (
                  <Input
                    name="board_marks"
                    type="number"
                    placeholder="Board Marks (out of 300) - Optional"
                    glass
                    min={0}
                    max={300}
                    step="any"
                    className="text-lg py-6"
                  />
                )}

                <div className="grid grid-cols-2 gap-3">
                  {selectedExam.id === "kcet" ? (
                    <>
                      <select name="kcet_vertical" className={selectClass}>
                        {KCET_VERTICAL_CATEGORIES.map((c) => (
                          <option key={c.value} value={c.value} className={optionClass}>
                            {c.label}
                          </option>
                        ))}
                      </select>
                      <select name="kcet_horizontal" className={selectClass}>
                        {KCET_HORIZONTAL_CATEGORIES.map((h) => (
                          <option key={h.value} value={h.value} className={optionClass}>
                            {h.label}
                          </option>
                        ))}
                      </select>
                    </>
                  ) : (
                    <>
                      <select name="shift" className={selectClass}>
                        {selectedExam.shifts.map((s) => (
                          <option key={s.value} value={s.value} className={optionClass}>
                            {s.label}
                          </option>
                        ))}
                      </select>
                      <select name="category" className={selectClass}>
                        {CATEGORIES.map((c) => (
                          <option key={c.value} value={c.value} className={optionClass}>
                            {c.label}
                          </option>
                        ))}
                      </select>
                    </>
                  )}
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="mt-3 w-full relative overflow-hidden rounded-2xl py-4 text-lg font-bold tracking-wide text-white bg-gradient-to-r from-cyan-500 via-fuchsia-500 to-violet-500 shadow-[0_0_30px_rgba(34,211,238,0.25),0_0_30px_rgba(192,38,211,0.2)] hover:shadow-[0_0_40px_rgba(34,211,238,0.35),0_0_40px_rgba(192,38,211,0.3)] transition-shadow duration-300 disabled:opacity-60 group"
                >
                  <span className="relative z-10">{isLoading ? 'Predicting...' : selectedExam.live ? 'PREDICT MY RANK →' : `CHECK ${selectedExam.label} PREDICTION`}</span>
                  <div className="absolute inset-0 -translate-x-full bg-gradient-to-r from-transparent via-white/25 to-transparent group-hover:animate-shimmer z-0" />
                </button>

                <div className="text-xs text-white/30 text-center mt-2 tracking-wide">
                  <span className="font-semibold text-cyan-400/70">95.7% Accuracy</span>
                  <span className="mx-2">·</span>
                  12L+ Predictions Made
                </div>
              </motion.form>
            )}
          </AnimatePresence>
          </div>{/* Close glass card body */}
        </motion.div>

        {/* Trusted by — subtle frosted pill */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, delay: 0.9 }}
          className="mt-12 text-white/25 text-xs flex items-center justify-center gap-3 flex-wrap bg-white/[0.03] backdrop-blur-sm rounded-full px-6 py-3 border border-white/[0.05] mx-auto w-fit"
        >
          <span className="tracking-wider uppercase text-[10px]">Trusted by students from</span>
          {["Allen", "Aakash", "Resonance", "PW", "FIITJEE"].map((name) => (
            <span key={name} className="font-semibold text-white/40">{name}</span>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
