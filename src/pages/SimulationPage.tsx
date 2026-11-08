import { Link, Navigate, useParams } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { getScenario } from "../data/scenarios";
import { MetaItem, MetaLabel } from "../components/Meta";
import { GhostLink, PrimaryLink } from "../components/Cta";

export function SimulationPage() {
  const { id } = useParams();
  const scenario = getScenario(id);

  if (!scenario) {
    return <Navigate to="/scenarios" replace />;
  }

  return (
    <div className="space-y-12">
      <Link
        to={`/scenarios/${scenario.id}`}
        className="group inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint transition-colors hover:text-signal"
      >
        <ArrowLeft size={14} className="transition-transform group-hover:-translate-x-1" />
        Return to briefing
      </Link>

      <header>
        <div className="flex flex-wrap items-center gap-3">
          <span className="border border-signal/60 px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.2em] text-signal">
            Runtime stub
          </span>
          <MetaLabel>Case {scenario.code}</MetaLabel>
        </div>
        <h1 className="mt-5 max-w-3xl font-display text-4xl leading-[1.05] text-ink sm:text-5xl">
          The simulation bay is empty.
        </h1>
        <p className="mt-5 max-w-2xl text-[15px] leading-relaxed text-ink-soft">
          The interactive simulation runtime is scheduled for Phase 2 of the build. This page
          exists to verify that case routing, metadata, and navigation are wired correctly —
          which, for {scenario.code}, they are.
        </p>
      </header>

      <section className="grid gap-x-8 gap-y-5 border border-line p-6 sm:grid-cols-2 sm:p-8 lg:grid-cols-4">
        <MetaItem label="Case" value={scenario.code} />
        <MetaItem label="Category" value={scenario.category} />
        <MetaItem label="Difficulty" value={scenario.difficulty} />
        <MetaItem label="Duration" value={`${scenario.durationMinutes} min`} />
      </section>

      <div className="flex flex-wrap gap-4">
        <PrimaryLink to={`/scenarios/${scenario.id}`}>Return to briefing</PrimaryLink>
        <GhostLink to="/scenarios">Back to library</GhostLink>
      </div>
    </div>
  );
}
