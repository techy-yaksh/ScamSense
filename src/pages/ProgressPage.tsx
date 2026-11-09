import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getScenarioByApiId, scenarios } from "../data/scenarios";
import { fetchReports, type ReportSummary } from "../lib/api";
import { PageHeader } from "../components/PageHeader";
import { SectionHeader } from "../components/SectionHeader";
import { ProgressBar } from "../components/ProgressBar";
import { Stat } from "../components/Stat";
import { PrimaryLink } from "../components/Cta";

function formatTs(ts: number) {
  const date = new Date(ts * 1000);
  const day = date.toLocaleDateString("en-GB", { day: "2-digit", month: "short" }).toUpperCase();
  const time = date.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false });
  return `${day} · ${time}`;
}

export function ProgressPage() {
  const [reports, setReports] = useState<ReportSummary[] | null>(null);
  const [reportsError, setReportsError] = useState("");

  useEffect(() => {
    let active = true;
    fetchReports()
      .then((result) => {
        if (active) setReports(result);
      })
      .catch((err) => {
        if (active) setReportsError(err instanceof Error ? err.message : "Unavailable.");
      });
    return () => {
      active = false;
    };
  }, []);

  const totalRuns = reports?.length ?? 0;
  const uniqueCleared = new Set(reports?.map((r) => r.scenario_id) ?? []).size;
  const overallCoverage = Math.round((uniqueCleared / scenarios.length) * 100);
  const avgScore =
    reports && reports.length > 0
      ? Math.round(reports.reduce((acc, r) => acc + r.overall, 0) / reports.length)
      : 0;
  const topScore =
    reports && reports.length > 0 ? Math.max(...reports.map((r) => r.overall)) : 0;

  return (
    <div className="space-y-14">
      <PageHeader
        index="03"
        kicker="Progress"
        title="The training record."
        description="Documented history of completed simulation runs, performance evaluations, and scenario coverage."
        aside={
          reports === null ? (
            <span className="border border-line px-3 py-1 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">
              Loading
            </span>
          ) : reports.length > 0 ? (
            <span className="border border-signal/60 bg-signal/10 px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-signal">
              {reports.length} {reports.length === 1 ? "Report" : "Reports"} on file
            </span>
          ) : (
            <span className="border border-line px-3 py-1.5 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">
              Standing record
            </span>
          )
        }
      />

      <section>
        <div className="grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-4">
          <Stat
            label="Library coverage"
            value={`${overallCoverage}%`}
            note={`${uniqueCleared} of ${scenarios.length} cases cleared`}
          />
          <Stat
            label="Sessions completed"
            value={reports === null ? "—" : String(totalRuns).padStart(2, "0")}
            note="Archived evaluations"
          />
          <Stat
            label="Average score"
            value={reports && reports.length > 0 ? `${avgScore}` : "—"}
            note="Across completed runs"
          />
          <Stat
            label="Top score"
            value={reports && reports.length > 0 ? `${topScore}` : "—"}
            note="Highest evaluation"
          />
        </div>
      </section>

      <section>
        <SectionHeader index="§1" title="Completed reports" aside="Live dossier" />
        {reportsError ? (
          <p className="border-t border-line py-5 font-mono text-[11px] text-ink-faint">
            Training API offline — live reports unavailable.
          </p>
        ) : reports === null ? (
          <p className="border-t border-line py-5 font-mono text-[11px] text-ink-faint">
            Loading archived reports…
          </p>
        ) : reports.length === 0 ? (
          <div className="border border-line bg-surface/30 p-6 sm:p-8">
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
              No completed simulations on file
            </p>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-ink-soft">
              When you complete an interactive case, its evidence-backed intelligence debrief and
              decision audit are permanently archived here.
            </p>
            <div className="mt-6">
              <PrimaryLink to="/scenarios">Start a simulation</PrimaryLink>
            </div>
          </div>
        ) : (
          <ul className="border-b border-line">
            {reports.map((report) => {
              const scenario = getScenarioByApiId(report.scenario_id);
              return (
                <li key={report.simulation_id}>
                  <Link
                    to={`/reports/${report.simulation_id}`}
                    className="group flex flex-wrap items-center gap-x-6 gap-y-2 border-t border-line py-5 transition-colors hover:bg-surface/30"
                  >
                    <span className="font-mono text-xs text-ink-faint">
                      {scenario?.code ?? report.scenario_id}
                    </span>
                    <span className="font-display text-lg text-ink transition-colors group-hover:text-signal">
                      {scenario?.title ?? "Simulation"}
                    </span>
                    <span className="font-mono text-[11px] text-ink-faint">
                      {formatTs(report.ended_at)}
                    </span>
                    <span className="ml-auto flex items-center gap-3">
                      <span className="font-mono text-xs text-ink-faint">
                        {report.turn} turns
                      </span>
                      <span className="font-mono text-sm text-ink">{report.overall}</span>
                      <span className="border border-line px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.14em] text-ink-soft">
                        {report.rating}
                      </span>
                      <span className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint transition-colors group-hover:text-signal">
                        Open report →
                      </span>
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      <section>
        <SectionHeader index="§2" title="Case coverage" aside="Per registered case" />
        <div className="border-b border-line">
          {scenarios.map((scenario) => {
            const caseReports =
              reports?.filter(
                (r) => r.scenario_id === scenario.apiId || r.scenario_id === scenario.id
              ) ?? [];
            const isCleared = caseReports.length > 0;
            const completion = isCleared ? 100 : 0;
            const latestTs = isCleared ? Math.max(...caseReports.map((r) => r.ended_at)) : null;

            return (
              <div
                key={scenario.id}
                className="grid grid-cols-1 gap-x-8 gap-y-4 border-t border-line py-6 sm:grid-cols-12 sm:items-center"
              >
                <span className="font-mono text-xs text-ink-faint sm:col-span-1">
                  {scenario.code}
                </span>
                <div className="sm:col-span-5">
                  <Link
                    to={`/scenarios/${scenario.id}`}
                    className="font-display text-lg text-ink transition-colors hover:text-signal"
                  >
                    {scenario.title}
                  </Link>
                  <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">
                    {isCleared
                      ? `Cleared (${caseReports.length} ${caseReports.length === 1 ? "run" : "runs"})`
                      : "Not started"}
                    {latestTs ? ` · Last: ${formatTs(latestTs)}` : ""}
                  </p>
                </div>
                <div className="sm:col-span-5">
                  <ProgressBar pct={completion} />
                </div>
                <span className="font-mono text-xs text-ink-soft sm:col-span-1 sm:text-right">
                  {completion}%
                </span>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
