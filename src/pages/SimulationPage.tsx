import { useCallback, useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { getScenario } from "../data/scenarios";
import type { Scenario } from "../types";
import {
  ApiError,
  endSimulation,
  sendSimulationMessage,
  startSimulation,
  type DecisionEvent,
  type Evaluation,
  type StageInfo,
  type TranscriptMessage,
} from "../lib/api";
import { Composer } from "../components/simulation/Composer";
import { ProgressPanel } from "../components/simulation/ProgressPanel";
import { ReportView } from "../components/simulation/ReportView";
import { Transcript } from "../components/simulation/Transcript";
import { DifficultyBadge, MetaLabel } from "../components/Meta";
import { GhostLink, PrimaryLink } from "../components/Cta";

type Phase = "loading" | "error" | "running" | "ended";

export function SimulationPage() {
  const { id } = useParams();
  const scenario = getScenario(id);

  if (!scenario) {
    return <Navigate to="/scenarios" replace />;
  }

  return <SimulationRunner scenario={scenario} />;
}

interface ErrorInfo {
  label: string;
  title: string;
  detail: string;
}

function SimulationRunner({ scenario }: { scenario: Scenario }) {
  const [phase, setPhase] = useState<Phase>("loading");
  const [error, setError] = useState<ErrorInfo | null>(null);
  const [simulationId, setSimulationId] = useState("");
  const [transcript, setTranscript] = useState<TranscriptMessage[]>([]);
  const [stage, setStage] = useState<StageInfo | null>(null);
  const [events, setEvents] = useState<DecisionEvent[]>([]);
  const [aiMode, setAiMode] = useState(false);
  const [aiConfigured, setAiConfigured] = useState(false);
  const [disclaimer, setDisclaimer] = useState("");
  const [turn, setTurn] = useState(0);
  const [typing, setTyping] = useState(false);
  const [sendError, setSendError] = useState("");
  const [endedByCaller, setEndedByCaller] = useState(false);
  const [ending, setEnding] = useState(false);
  const [evaluation, setEvaluation] = useState<Evaluation | null>(null);

  const start = useCallback(async () => {
    setPhase("loading");
    setError(null);
    try {
      const targetScenarioId = scenario.apiId ?? scenario.id;
      const res = await startSimulation(targetScenarioId);
      setSimulationId(res.simulation_id);
      setTranscript(res.transcript);
      setStage(res.stage);
      setAiConfigured(res.ai_configured);
      setAiMode(false);
      setDisclaimer(res.disclaimer);
      setPhase("running");
    } catch (err) {
      if (err instanceof ApiError && err.status !== null) {
        setError({
          label: `API error · ${err.status}`,
          title: "Simulation request failed.",
          detail: err.message,
        });
      } else {
        setError({
          label: "Connection error",
          title: "The training API is not reachable.",
          detail: err instanceof Error ? err.message : "Failed to connect to the training API.",
        });
      }
      setPhase("error");
    }
  }, [scenario.apiId, scenario.id]);

  useEffect(() => {
    void start();
  }, [start]);

  const handleSend = useCallback(
    async (text: string) => {
      setSendError("");
      setTranscript((prev) => [
        ...prev,
        { role: "user", text, ts: Date.now(), stage: stage?.key ?? "", system_note: false, warning: false },
      ]);
      setTyping(true);
      try {
        const res = await sendSimulationMessage(simulationId, text);
        setTranscript((prev) => {
          const next = [...prev, res.reply];
          for (const note of res.system_notes) next.push(note);
          return next;
        });
        setEvents((prev) => [...prev, ...res.events]);
        setStage(res.stage);
        setAiMode(res.ai_mode);
        setTurn(res.turn);
        if (res.ended) setEndedByCaller(true);
      } catch (err) {
        setSendError(err instanceof Error ? err.message : "The reply could not be delivered.");
      } finally {
        setTyping(false);
      }
    },
    [simulationId, stage]
  );

  const handleEnd = useCallback(async () => {
    setEnding(true);
    setSendError("");
    try {
      const res = await endSimulation(simulationId);
      setEvaluation(res.evaluation);
      setPhase("ended");
    } catch (err) {
      setSendError(err instanceof Error ? err.message : "The simulation could not be ended.");
    } finally {
      setEnding(false);
    }
  }, [simulationId]);

  if (phase === "loading") {
    return (
      <div className="space-y-8">
        <BackLink to={`/scenarios/${scenario.id}`} />
        <div className="border border-line bg-surface/50 p-8 sm:p-10">
          <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-ink-faint">
            Initializing transmission channel
          </p>
          <p className="mt-3 font-display text-2xl text-ink">Opening case bay {scenario.code}…</p>
          <p className="mt-2 font-mono text-xs text-ink-soft">
            Synchronizing scenario state and loading intercept stream.
          </p>
        </div>
      </div>
    );
  }

  if (phase === "error") {
    return (
      <div className="space-y-12">
        <BackLink to={`/scenarios/${scenario.id}`} />
        <div className="border border-signal/60 bg-signal/10 p-8">
          <MetaLabel>{error?.label ?? "Connection error"}</MetaLabel>
          <p className="mt-4 font-display text-2xl text-ink">
            {error?.title ?? "The training API is not reachable."}
          </p>
          {error?.detail ? (
            <p className="mt-3 max-w-xl text-sm leading-relaxed text-ink-soft">{error.detail}</p>
          ) : null}
          <div className="mt-8 flex flex-wrap gap-4">
            <button
              onClick={() => void start()}
              className="bg-signal px-6 py-3.5 font-mono text-xs uppercase tracking-[0.2em] text-bg transition-colors hover:bg-ink"
            >
              Retry
            </button>
            <GhostLink to={`/scenarios/${scenario.id}`}>Back to briefing</GhostLink>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <BackLink to={`/scenarios/${scenario.id}`} />

      <div className="flex flex-wrap items-center justify-between gap-4 border border-line bg-surface/50 px-5 py-4">
        <div className="flex items-center gap-4">
          <SimBadge />
          <div>
            <p className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">
              {scenario.code} · {scenario.category}
            </p>
            <p className="mt-1 font-display text-lg leading-none text-ink">{scenario.title}</p>
          </div>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <DifficultyBadge level={scenario.difficulty} />
          <span className="border border-line px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-soft">
            {turn === 0
              ? (aiConfigured ? "AI standby" : "Deterministic")
              : (aiConfigured ? (aiMode ? "AI voice" : "AI · fallback") : "Deterministic")}
          </span>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-12">
        <div className="lg:col-span-8">
          <Transcript messages={transcript} typing={typing} />
          {phase === "running" ? (
            <>
              {sendError ? (
                <p className="mt-3 border border-signal/60 bg-signal/10 px-4 py-2.5 font-mono text-[11px] text-signal">
                  {sendError}
                </p>
              ) : null}
              <Composer
                onSend={(text) => void handleSend(text)}
                disabled={typing}
                endedByCaller={endedByCaller}
              />
              <p className="mt-3 font-mono text-[9px] uppercase tracking-[0.16em] leading-relaxed text-ink-faint">
                {disclaimer}
              </p>
            </>
          ) : null}
        </div>
        <div className="lg:col-span-4">
          <ProgressPanel
            stage={stage}
            turn={turn}
            events={events}
            onEnd={() => void handleEnd()}
            ending={ending}
          />
        </div>
      </div>

      {phase === "ended" && evaluation ? (
        <>
          <ReportView evaluation={evaluation} />
          <div className="flex flex-wrap gap-4">
            <PrimaryLink to={`/scenarios/${scenario.id}`}>Back to briefing</PrimaryLink>
            <GhostLink to="/progress">View progress</GhostLink>
          </div>
        </>
      ) : null}
    </div>
  );
}

function SimBadge() {
  return (
    <span className="flex shrink-0 items-center gap-2 border border-signal/60 bg-signal/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-signal">
      <span className="h-1.5 w-1.5 shrink-0 bg-signal" />
      Console · Active Intercept
    </span>
  );
}

function BackLink({ to }: { to: string }) {
  return (
    <Link
      to={to}
      className="group inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint transition-colors hover:text-signal"
    >
      <ArrowLeft size={14} className="transition-transform group-hover:-translate-x-1" />
      Return to briefing
    </Link>
  );
}
