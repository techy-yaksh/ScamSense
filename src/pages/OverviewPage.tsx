import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { featuredScenario, getScenarioByApiId, scenarios } from "../data/scenarios";
import { fetchReports, type ReportSummary } from "../lib/api";
import { GhostLink, PrimaryLink } from "../components/Cta";
import { MetaItem, MetaLabel } from "../components/Meta";
import { SectionHeader } from "../components/SectionHeader";
import { Stat } from "../components/Stat";

function formatTs(ts: number) {
  const date = new Date(ts * 1000);
  const day = date.toLocaleDateString("en-GB", { day: "2-digit", month: "short" }).toUpperCase();
  const time = date.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", hour12: false });
  return `${day} · ${time}`;
}

export function OverviewPage() {
  const featured = featuredScenario;
  const [reports, setReports] = useState<ReportSummary[] | null>(null);

  useEffect(() => {
    let active = true;
    fetchReports()
      .then((data) => {
        if (active) setReports(data);
      })
      .catch(() => {
        if (active) setReports([]);
      });
    return () => {
      active = false;
    };
  }, []);

  const totalRuns = reports?.length ?? 0;
  const uniqueCases = new Set(reports?.map((r) => r.scenario_id) ?? []).size;
  const avgScore =
    reports && reports.length > 0
      ? Math.round(reports.reduce((acc, r) => acc + r.overall, 0) / reports.length)
      : 0;
  const topScore =
    reports && reports.length > 0 ? Math.max(...reports.map((r) => r.overall)) : 0;

  return (
    <div className="space-y-16 lg:space-y-20">
      <section className="max-w-3xl">
        <p className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.24em] text-ink-faint">
          <span className="h-px w-8 bg-signal" />
          Field manual · Social engineering
        </p>
        <h1 className="mt-6 font-display text-5xl leading-[1.02] text-ink sm:text-6xl">
          Scams are patterns.
          <br />
          <span className="text-ink-soft">Patterns can be read.</span>
        </h1>
        <p className="mt-7 text-base leading-relaxed text-ink-soft sm:text-[17px]">
          ScamSense runs controlled simulations of the social-engineering sequences most
          likely to reach you, then debriefs each attempt against the pattern. No real
          money, no real risk — only the sequence, and the skill to name it.
        </p>
        <div className="mt-9 flex flex-wrap items-center gap-4">
          <PrimaryLink to={`/scenarios/${featured.id}`} large>
            Start case {featured.code}
          </PrimaryLink>
          <GhostLink to="/scenarios">Browse case library</GhostLink>
        </div>
      </section>

      <section>
        <SectionHeader index="§1" title="Featured case" aside="Primary sequence" />
        <article className="grid gap-8 border border-line bg-surface/50 p-6 sm:p-10 lg:grid-cols-12">
          <div className="lg:col-span-8">
            <div className="flex flex-wrap items-center gap-3">
              <MetaLabel>Case {featured.code}</MetaLabel>
              <span className="h-3 w-px bg-line-strong" />
              <MetaLabel>Featured</MetaLabel>
            </div>
            <h3 className="mt-4 font-display text-3xl text-ink sm:text-4xl">
              {featured.title}
            </h3>
            <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-ink-soft">
              {featured.description}
            </p>
          </div>
          <div className="flex flex-col justify-between gap-8 lg:col-span-4 lg:border-l lg:border-line lg:pl-8">
            <div className="space-y-4">
              <MetaItem label="Category" value={featured.category} />
              <MetaItem label="Difficulty" value={featured.difficulty} />
              <MetaItem label="Duration" value={`est. ${featured.durationMinutes} min`} />
            </div>
            <PrimaryLink to={`/scenarios/${featured.id}`}>Open briefing</PrimaryLink>
          </div>
        </article>
      </section>

      <section>
        <SectionHeader index="§2" title="Training telemetry" aside="Verified records" />
        {reports === null ? (
          <p className="border-t border-line py-6 font-mono text-[11px] text-ink-faint">
            Loading telemetry…
          </p>
        ) : reports.length === 0 ? (
          <div className="border border-line bg-surface/30 p-6 sm:p-8">
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
              No session records on file
            </p>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-ink-soft">
              Performance metrics calculate dynamically once your first simulation is completed.
              Launch any case from the library to establish baseline awareness data.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-4">
            <Stat
              label="Sessions run"
              value={String(totalRuns).padStart(2, "0")}
              note="Evaluated simulations"
            />
            <Stat
              label="Average score"
              value={`${avgScore}`}
              note="Across all evaluations"
            />
            <Stat
              label="Cases evaluated"
              value={`${uniqueCases} / ${scenarios.length}`}
              note="Library coverage"
            />
            <Stat
              label="Top score"
              value={`${topScore}`}
              note="Highest evaluation"
            />
          </div>
        )}
      </section>

      <section>
        <SectionHeader index="§3" title="Recent debriefs" aside="Intelligence ledger" />
        {reports === null ? (
          <p className="border-t border-line py-6 font-mono text-[11px] text-ink-faint">
            Loading debriefs…
          </p>
        ) : reports.length === 0 ? (
          <div className="border border-line bg-surface/30 p-6 sm:p-8">
            <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint">
              Ledger is clear
            </p>
            <p className="mt-2 max-w-xl text-sm leading-relaxed text-ink-soft">
              No simulation debriefs have been filed yet. Completed scenarios and their
              evidence-backed evaluations will be archived here.
            </p>
          </div>
        ) : (
          <div className="border-b border-line">
            {reports.slice(0, 5).map((item) => {
              const sc = getScenarioByApiId(item.scenario_id);
              return (
                <div
                  key={item.simulation_id}
                  className="grid grid-cols-1 gap-2 border-t border-line py-5 sm:grid-cols-12 sm:items-baseline"
                >
                  <span className="font-mono text-[11px] text-ink-faint sm:col-span-3">
                    {formatTs(item.ended_at)}
                  </span>
                  <div className="sm:col-span-5">
                    <p className="text-sm text-ink">
                      {sc ? `${sc.code} · ${sc.title}` : `Simulation ${item.simulation_id.slice(0, 8)}`}
                    </p>
                    <p className="mt-0.5 font-mono text-[10px] uppercase tracking-[0.16em] text-ink-faint">
                      {item.turn} turns · Score {item.overall}/100
                    </p>
                  </div>
                  <div className="flex items-center gap-4 sm:col-span-4 sm:justify-end">
                    <span className="border border-line px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.16em] text-ink-soft">
                      {item.rating}
                    </span>
                    <Link
                      to={`/reports/${item.simulation_id}`}
                      className="font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint transition-colors hover:text-signal"
                    >
                      Report →
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </section>
    </div>
  );
}
