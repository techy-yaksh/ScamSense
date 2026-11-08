import type { ActivityItem, DemoStat, ScenarioProgress } from "../types";

export const overviewStats: DemoStat[] = [
  { label: "Sessions completed", value: "07", note: "Sample data" },
  { label: "Avg. recognition", value: "86%", note: "Sample data" },
  { label: "Patterns covered", value: "12", note: "Sample data" },
  { label: "Study streak", value: "05 days", note: "Sample data" },
];

export const recentActivity: ActivityItem[] = [
  {
    id: "a-01",
    at: "NOV 04 · 14:22",
    title: "SS-101 · UPI / Banking Fraud",
    detail: "Session completed — full sequence walked",
    tag: "Cleared",
  },
  {
    id: "a-02",
    at: "NOV 02 · 09:10",
    title: "SS-301 · Fake Job / Internship",
    detail: "Briefing opened, simulation queued",
    tag: "In flight",
  },
  {
    id: "a-03",
    at: "OCT 30 · 18:45",
    title: "SS-201 · Digital Arrest",
    detail: "Case added to the training queue",
    tag: "Queued",
  },
];

export const demoProgress: ScenarioProgress[] = [
  {
    scenarioId: "upi-banking-fraud",
    status: "completed",
    completion: 100,
    updatedAt: "NOV 04",
    recognition: "91%",
  },
  {
    scenarioId: "fake-job-internship",
    status: "in-progress",
    completion: 60,
    updatedAt: "NOV 02",
  },
  {
    scenarioId: "digital-arrest",
    status: "not-started",
    completion: 0,
    updatedAt: "",
  },
];
