import { Link, Navigate, useParams } from "react-router-dom";
import { ArrowLeft, Clock } from "lucide-react";
import { getScenario } from "../data/scenarios";
import { DifficultyBadge, MetaLabel } from "../components/Meta";
import { PrimaryLink } from "../components/Cta";

export function BriefingPage() {
  const { id } = useParams();
  const scenario = getScenario(id);

  if (!scenario) {
    return <Navigate to="/scenarios" replace />;
  }

  return (
    <div className="space-y-14">
      <Link
        to="/scenarios"
        className="group inline-flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.2em] text-ink-faint transition-colors hover:text-signal"
      >
        <ArrowLeft size={14} className="transition-transform group-hover:-translate-x-1" />
        Back to library
      </Link>

      <header>
        <div className="flex flex-wrap items-center gap-3">
          <MetaLabel>Case {scenario.code}</MetaLabel>
          <span className="h-3 w-px bg-line-strong" />
          <MetaLabel>{scenario.category}</MetaLabel>
        </div>
        <h1 className="mt-5 max-w-3xl font-display text-4xl leading-[1.05] text-ink sm:text-5xl">
          {scenario.title}
        </h1>
        <div className="mt-8 flex flex-wrap items-center gap-x-8 gap-y-4">
          <DifficultyBadge level={scenario.difficulty} />
          <span className="inline-flex items-center gap-2 font-mono text-[11px] text-ink-faint">
            <Clock size={13} /> EST. {scenario.durationMinutes} MIN
          </span>
          <span className="font-mono text-[11px] uppercase tracking-[0.18em] text-ink-faint">
            Simulated 1:1 exchange
          </span>
        </div>
      </header>

      <section className="grid gap-10 lg:grid-cols-12">
        <div className="lg:col-span-7">
          <MetaLabel>Introduction</MetaLabel>
          <div className="mt-5 space-y-5">
            {scenario.intro.map((paragraph) => (
              <p
                key={paragraph.slice(0, 24)}
                className="text-[15px] leading-relaxed text-ink-soft first:text-lg first:leading-relaxed first:text-ink"
              >
                {paragraph}
              </p>
            ))}
          </div>
        </div>
        <aside className="lg:col-span-5 lg:border-l lg:border-line lg:pl-10">
          <MetaLabel>Learning objectives</MetaLabel>
          <ol className="mt-5">
            {scenario.objectives.map((objective, i) => (
              <li key={objective} className="flex gap-4 border-t border-line py-4">
                <span className="font-mono text-[11px] text-signal">0{i + 1}</span>
                <p className="text-sm leading-relaxed text-ink-soft">{objective}</p>
              </li>
            ))}
          </ol>
        </aside>
      </section>

      <section className="border border-line bg-surface/50 p-6 sm:p-10">
        <div className="flex flex-col gap-8 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <MetaLabel>Simulation status</MetaLabel>
            <p className="mt-3 font-display text-2xl text-ink">
              Case ready. Simulation live.
            </p>
            <p className="mt-2 max-w-md text-sm leading-relaxed text-ink-soft">
              Interactive training simulation is live for this case. Step into the exchange,
              recognise the pressure mechanics, and test your decision-making.
            </p>
          </div>
          <PrimaryLink to={`/scenarios/${scenario.id}/simulation`} large>
            Start simulation
          </PrimaryLink>
        </div>
      </section>
    </div>
  );
}
