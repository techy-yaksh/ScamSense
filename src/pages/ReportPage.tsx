import { useEffect, useState } from "react";
import { Link, Navigate, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { fetchSimulation, type SimulationRecord } from "../lib/api";
import { getScenarioByApiId } from "../data/scenarios";
import { ReportView } from "../components/simulation/ReportView";
import { Transcript } from "../components/simulation/Transcript";
import { MetaLabel } from "../components/Meta";
import { GhostLink } from "../components/Cta";

type State =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; record: SimulationRecord };

export function ReportPage() {
  const { simulationId } = useParams();

  if (!simulationId) {
    return <Navigate to="/progress" replace />;
  }

  return <ReportRunner simulationId={simulationId} />;
}

function ReportRunner({ simulationId }: { simulationId: string }) {
  const [state, setState] = useState<State>({ status: "loading" });

  useEffect(() => {
    let active = true;
    setState({ status: "loading" });
    fetchSimulation(simulationId)
      .then((record) => {
        if (active) setState({ status: "ready", record });
      })
      .catch((err) => {
        if (active)
          setState({ status: "error", message: err instanceof Error ? err.message : "Report unavailable." });
      });
    return () => {
      active = false;
    };
  }, [simulationId]);

  if (state.status === "loading") {
    return (
      <div className="space-y-12">
        <BackLink />
        <div className="flex flex-col items-start gap-4 border border-line bg-surface/50 p-8">
          <MetaLabel>Retrieving report</MetaLabel>
          <span className="flex gap-1">
            <span className="h-1.5 w-1.5 animate-pulse bg-signal" />
            <span className="h-1.5 w-1.5 animate-pulse bg-signal [animation-delay:150ms]" />
            <span className="h-1.5 w-1.5 animate-pulse bg-signal [animation-delay:300ms]" />
          </span>
        </div>
      </div>
    );
  }

  if (state.status !== "ready" || !state.record.evaluation) {
    return (
      <div className="space-y-12">
        <BackLink />
        <div className="border border-signal/60 bg-signal/10 p-8">
          <MetaLabel>Report unavailable</MetaLabel>
          <p className="mt-4 font-display text-2xl text-ink">This report could not be loaded.</p>
          <p className="mt-3 max-w-xl text-sm leading-relaxed text-ink-soft">
            {state.status === "error"
              ? state.message
              : "The simulation has not been ended, or it is no longer stored on this device."}
          </p>
          <div className="mt-8">
            <GhostLink to="/progress">Back to progress</GhostLink>
          </div>
        </div>
      </div>
    );
  }

  const { record } = state;
  const evaluation = state.record.evaluation;

  const scenario = getScenarioByApiId(evaluation.scenario_id);
  const completedAt = new Date(evaluation.ended_at * 1000);

  return (
    <div className="space-y-10">
      <BackLink />

      <header>
        <div className="flex flex-wrap items-center gap-3">
          <MetaLabel>Report · {record.simulation_id.slice(0, 8).toUpperCase()}</MetaLabel>
          <span className="h-3 w-px bg-line-strong" />
          <MetaLabel>
            {completedAt.toLocaleDateString("en-GB", { day: "2-digit", month: "short" }).toUpperCase()}{" "}
            {completedAt.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false })}
          </MetaLabel>
        </div>
        <h1 className="mt-5 font-display text-4xl leading-[1.05] text-ink sm:text-5xl">
          {scenario ? scenario.title : "Simulation"}
        </h1>
        {scenario ? (
          <p className="mt-3 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
            {scenario.code} · {scenario.category}
          </p>
        ) : null}
      </header>

      <ReportView evaluation={evaluation} />

      <section>
        <SectionLabel>Transcript — as recorded</SectionLabel>
        <div className="mt-4">
          <Transcript messages={record.transcript} typing={false} />
        </div>
      </section>
    </div>
  );
}

function SectionLabel({ children }: { children: string }) {
  return (
    <p className="border-b border-line pb-3 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-faint">
      {children}
    </p>
  );
}

function BackLink() {
  return (
    <Link
      to="/progress"
      className="group inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint transition-colors hover:text-signal"
    >
      <ArrowLeft size={14} className="transition-transform group-hover:-translate-x-1" />
      Back to progress
    </Link>
  );
}
