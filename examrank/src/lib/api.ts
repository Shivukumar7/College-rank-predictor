const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Types
export interface JEEPredictionRequest {
  marks: number;
  shift: string;
  category: string;
  total_candidates?: number;
  board_marks?: number;
}

export interface JEEPredictionResponse {
  predicted_rank: number;
  category_rank: number;
  percentile: number;
  normalized_marks: number;
  confidence: number;
  shift: string;
  category: string;
  total_candidates: number;
  board_marks_used?: boolean;
  eligible?: boolean;
}

export interface HealthResponse {
  status: string;
}

// API Functions
export async function predictExam(examId: string, data: JEEPredictionRequest): Promise<JEEPredictionResponse> {
  const response = await fetch(`${API_BASE}/predict/${examId}/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}

export interface College {
  name: string;
  branch: string;
  type: string;
  closing_rank: number;
  opening_rank: number;
  chance: number;
  category: string;
  quota: string;
  fees_lpa?: number;
  avg_lpa?: number;
  high_lpa?: number;
  roi_index?: number;
  top_recruiters?: string[];
  location?: string;
  hostel?: string;
  coding_culture?: string;
  specialization?: string;
  choice_number?: number;
}

export async function getROIRanking(colleges: College[]): Promise<{colleges: College[]}> {
  const response = await fetch(`${API_BASE}/predict/roi-ranking/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ colleges }),
  });
  if (!response.ok) throw new Error("Failed to get ROI ranking");
  return response.json();
}

export async function getCollegePredictions(
  examId: string, 
  rank: number, 
  marks: number, 
  category: string,
  quota?: string
): Promise<{colleges: College[], total: number}> {
  const params = new URLSearchParams();
  if (rank) params.append("rank", rank.toString());
  if (marks) params.append("marks", marks.toString());
  if (category) params.append("category", category);
  if (quota) params.append("quota", quota);
  
  const response = await fetch(`${API_BASE}/predict/${examId}/colleges?${params.toString()}`);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  
  return response.json();
}

export async function optimizeChoices(colleges: College[], branchPreferences?: string[]): Promise<{colleges: College[]}> {
  const response = await fetch(`${API_BASE}/predict/optimize-choices/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ colleges, branch_preferences: branchPreferences }),
  });
  if (!response.ok) throw new Error("Failed to optimize choices");
  return response.json();
}

export interface ChatContext {
  exam?: string;
  rank?: number;
  category?: string;
  preferred_branches?: string[];
}

export async function askChatbot(message: string, context?: ChatContext): Promise<{reply: string}> {
  const response = await fetch(`${API_BASE}/predict/chatbot/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, context }),
  });
  if (!response.ok) {
    if (response.status === 429) {
      const errData = await response.json().catch(() => ({ detail: "Too many requests." }));
      throw new Error(errData.detail || "Rate limit exceeded.");
    }
    throw new Error("Chatbot failed");
  }
  return response.json();
}

export async function getTrends(exam: string, institute: string, branch: string, category: string, quota?: string): Promise<{trends: {year: number, opening_rank: number, closing_rank: number}[], institute: string, branch: string}> {
  const params = new URLSearchParams({ exam, institute, branch, category });
  if (quota) params.append("quota", quota);
  
  const response = await fetch(`${API_BASE}/predict/trends/?${params.toString()}`);
  if (!response.ok) throw new Error("Failed to fetch cutoff trends");
  return response.json();
}

export async function predictJEEMain(data: JEEPredictionRequest): Promise<JEEPredictionResponse> {
  return predictExam("jee-main", data);
}

export async function checkHealth(): Promise<HealthResponse> {
  const response = await fetch(`${API_BASE}/health`);
  if (!response.ok) throw new Error("Health check failed");
  return response.json();
}

export async function getShiftStats(shift: string) {
  const response = await fetch(`${API_BASE}/predict/jee-main/shift-stats/${shift}`);
  if (!response.ok) throw new Error("Failed to fetch shift stats");
  return response.json();
}

export async function getGlobalStats() {
  const response = await fetch(`${API_BASE}/predict/jee-main/global-stats`);
  if (!response.ok) throw new Error("Failed to fetch global stats");
  return response.json();
}

