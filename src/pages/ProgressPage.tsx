import { Link } from "react-router-dom";
import { Check } from "lucide-react";
import { scenarios } from "../data/scenarios";
import { demoProgress } from "../data/demo";
import { PageHeader } from "../components/PageHeader";
import { SectionHeader } from "../components/SectionHeader";
import { ProgressBar } from "../components/ProgressBar";
import { Stat } from "../components/Stat";
import type { ScenarioStatus } from "../types";

const statusLabel: Record<ScenarioStatus, string> = {
  completed: "Cleared",
  "in-progress": "In progress",
  "not-started": "Not started",
};

export function ProgressPage() {
  const rows = demoProgress.map((progress) => ({
    ...progress,
    scenario: scenarios.find((s) => s.id === progress.scenarioId),
  }));
  const completed = rows.filter((row) => row.status === "completed");
  const clearedCount = completed.length;
  const overall = Math.round((clearedCount / rows.length) * 100);

  return (
    <div className="space-y-14">
      <PageHeader
        index="03"
        kicker="Progress"
        title="The training record."
        description="What you have run, what is in flight, and how recognition is trending across the loaded cases."
        aside={
          <span className="border border-signal/60 bg-signal/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-signal">
            Demo data
          </span>
        }
      />

      <section>
        <div className="grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-4">
          <Stat label="Overall completion" value={`${overall}%`} note={`${clearedCount} of ${rows.length} cases cleared`} />
          <Stat label="Sessions run" value="07" note="Demo data" />
          <Stat label="Avg. recognition" value="86%" note="Demo data" />
          <Stat label="Study streak" value="05 days" note="Demo data" />
        </div>
        <p className="mt-8 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">
          All figures in this view are sample data from the Phase 1 build.
        </p>
      </section>

      <section>
        <SectionHeader index="§1" title="Case progress" aside="Per case" />
        <div className="border-b border-line">
          {rows.map((row) =>
            row.scenario ? (
              <div
                key={row.scenarioId}
                className="grid grid-cols-1 gap-x-8 gap-y-4 border-t border-line py-6 sm:grid-cols-12 sm:items-center"
              >
                <span className="font-mono text-xs text-ink-faint sm:col-span-1">
                  {row.scenario.code}
                </span>
                <div className="sm:col-span-5">
                  <Link
                    to={`/scenarios/${row.scenario.id}`}
                    className="font-display text-lg text-ink transition-colors hover:text-signal"
                  >
                    {row.scenario.title}
                  </Link>
                  <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">
                    {statusLabel[row.status]}
                    {row.updatedAt ? ` · ${row.updatedAt}` : ""}
                  </p>
                </div>
                <div className="sm:col-span-5">
                  <ProgressBar pct={row.completion} />
                </div>
                <span className="font-mono text-xs text-ink-soft sm:col-span-1 sm:text-right">
                  {row.completion}%
                </span>
              </div>
            ) : null
          )}
        </div>
      </section>

      <section>
        <SectionHeader index="§2" title="Completed scenarios" aside="Demo data" />
        {completed.length > 0 ? (
          <ul className="border-b border-line">
            {completed.map(
              (row) =>
                row.scenario && (
                  <li
                    key={row.scenarioId}
                    className="flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-line py-5"
                  >
                    <span className="flex h-7 w-7 items-center justify-center border border-signal/60 text-signal">
                      <Check size={14} />
                    </span>
                    <Link
                      to={`/scenarios/${row.scenario.id}`}
                      className="font-display text-lg text-ink transition-colors hover:text-signal"
                    >
                      {row.scenario.title}
                    </Link>
                    <span className="ml-auto font-mono text-[11px] text-ink-faint">
                      Cleared {row.updatedAt}
                      {row.recognition ? ` · Recognition ${row.recognition}` : ""}
                    </span>
                  </li>
                )
            )}
          </ul>
        ) : (
          <p className="border-t border-line py-5 text-sm text-ink-soft">
            No scenarios cleared yet. Start with the featured case.
          </p>
        )}
      </section>
    </div>
  );
}
