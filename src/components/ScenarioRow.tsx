import { Link } from "react-router-dom";
import { ArrowRight, Clock } from "lucide-react";
import type { Scenario } from "../types";
import { DifficultyBadge, MetaLabel } from "./Meta";

export function ScenarioRow({ scenario }: { scenario: Scenario }) {
  return (
    <Link
      to={`/scenarios/${scenario.id}`}
      className="group -mx-4 grid grid-cols-1 gap-x-8 gap-y-5 border-t border-line px-4 py-8 transition-colors last:border-b hover:bg-surface md:grid-cols-12"
    >
      <div className="flex items-start gap-4 md:col-span-2 md:flex-col md:gap-3">
        <span className="font-mono text-xs tracking-[0.12em] text-ink-faint transition-colors group-hover:text-signal">
          {scenario.code}
        </span>
        <MetaLabel>{scenario.category}</MetaLabel>
      </div>
      <div className="md:col-span-6">
        <h3 className="font-display text-2xl leading-tight text-ink transition-colors group-hover:text-signal sm:text-[28px]">
          {scenario.title}
        </h3>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-ink-soft">
          {scenario.description}
        </p>
      </div>
      <div className="flex flex-wrap items-center gap-x-6 gap-y-3 md:col-span-4 md:flex-col md:items-end md:justify-center">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-3">
          <DifficultyBadge level={scenario.difficulty} />
          <span className="inline-flex items-center gap-1.5 font-mono text-[11px] text-ink-faint">
            <Clock size={12} /> {scenario.durationMinutes} MIN
          </span>
        </div>
        <span className="inline-flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-faint transition-colors group-hover:text-signal">
          Briefing
          <ArrowRight size={13} className="transition-transform group-hover:translate-x-1" />
        </span>
      </div>
    </Link>
  );
}
