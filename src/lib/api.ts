const API_BASE: string = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export type Role = "caller" | "user" | "system";

export interface TranscriptMessage {
  role: Role;
  text: string;
  ts: number;
  stage: string;
  system_note: boolean;
  warning: boolean;
}

export interface StageInfo {
  key: string;
  label: string;
  index: number;
  total: number;
  pct: number;
}

export interface DecisionEvent {
  type: string;
  label: string;
  pattern: string | null;
  turn: number;
  excerpt: string;
  stage: string;
}

export interface CategoryScore {
  score: number;
  note: string;
}

export interface SignItem {
  stage: string;
  technique: string;
  description: string;
  turn: number;
  quote: string;
}

export interface TechniqueItem {
  stage: string;
  name: string;
  description: string;
}

export interface ExampleItem {
  turn: number;
  kind: "safe" | "risky";
  label: string;
  quote: string;
  stage: string;
}

export interface ReportSummary {
  simulation_id: string;
  scenario_id: string;
  ended_at: number;
  turn: number;
  overall: number;
  rating: string;
}

export interface SimulationRecord {
  simulation_id: string;
  ended: boolean;
  turn: number;
  stage: StageInfo;
  transcript: TranscriptMessage[];
  evaluation: Evaluation | null;
}

export interface StartResponse {
  simulation_id: string;
  scenario_id: string;
  scenario_title: string;
  ai_configured: boolean;
  stage: StageInfo;
  transcript: TranscriptMessage[];
  disclaimer: string;
}

export interface MessageResponse {
  reply: TranscriptMessage;
  system_notes: TranscriptMessage[];
  events: DecisionEvent[];
  stage: StageInfo;
  turn: number;
  ai_mode: boolean;
  ended: boolean;
}

export interface Scores {
  overall: number;
  caution: number;
  awareness: number;
}

export interface Evaluation {
  scenario_id: string;
  ended_at: number;
  turns: number;
  duration_seconds: number;
  final_stage: string;
  decision_events: DecisionEvent[];
  counts: Record<string, number>;
  scores: Scores;
  rating: string;
  summary: string;
  ai_mode: boolean;
  fictional: boolean;
  categories: Record<string, CategoryScore>;
  signs_recognized: SignItem[];
  signs_questioned: SignItem[];
  signs_missed: SignItem[];
  techniques: TechniqueItem[];
  examples: ExampleItem[];
  recommendations: string[];
  assessment: string;
}

export interface EndResponse {
  simulation_id: string;
  transcript: TranscriptMessage[];
  evaluation: Evaluation;
}

/** status null = network failure (backend unreachable); otherwise the HTTP status. */
export class ApiError extends Error {
  status: number | null;

  constructor(message: string, status: number | null) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      headers: { "Content-Type": "application/json" },
      ...init,
    });
  } catch {
    throw new ApiError("The training API is not reachable.", null);
  }
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // non-JSON error body; keep statusText
    }
    throw new ApiError(detail, res.status);
  }
  return (await res.json()) as T;
}

export function startSimulation(scenarioId: string): Promise<StartResponse> {
  return request<StartResponse>("/api/simulations", {
    method: "POST",
    body: JSON.stringify({ scenario_id: scenarioId }),
  });
}

export function sendSimulationMessage(simulationId: string, text: string): Promise<MessageResponse> {
  return request<MessageResponse>(`/api/simulations/${simulationId}/messages`, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function endSimulation(simulationId: string): Promise<EndResponse> {
  return request<EndResponse>(`/api/simulations/${simulationId}/end`, { method: "POST" });
}

export function fetchEvaluation(simulationId: string): Promise<Evaluation> {
  return request<Evaluation>(`/api/simulations/${simulationId}/evaluation`);
}

export function fetchReports(): Promise<ReportSummary[]> {
  return request<ReportSummary[]>("/api/reports");
}

export function fetchSimulation(simulationId: string): Promise<SimulationRecord> {
  return request<SimulationRecord>(`/api/simulations/${simulationId}`);
}
