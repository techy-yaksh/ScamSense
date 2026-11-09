export type Difficulty = "Foundation" | "Intermediate" | "Advanced";

export interface Scenario {
  id: string;
  apiId?: string;
  code: string;
  title: string;
  category: string;
  difficulty: Difficulty;
  durationMinutes: number;
  description: string;
  intro: string[];
  objectives: string[];
  featured?: boolean;
}

export type ScenarioStatus = "completed" | "in-progress" | "not-started";

export interface ScenarioProgress {
  scenarioId: string;
  status: ScenarioStatus;
  completion: number;
  updatedAt: string;
  recognition?: string;
}

export interface ActivityItem {
  id: string;
  at: string;
  title: string;
  detail: string;
  tag: string;
}

export interface DemoStat {
  label: string;
  value: string;
  note?: string;
}
