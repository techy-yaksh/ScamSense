import type { Evaluation } from "../../lib/api";
import { MetaLabel } from "../Meta";
import { ProgressBar } from "../ProgressBar";
import { SectionHeader } from "../SectionHeader";

const categoryLabels: [string, string][] = [
  ["awareness", "Scam awareness"],
  ["recognition", "Warning-sign recognition"],
  ["questioning", "Questioning & verification"],
  ["decisions", "Safe vs risky decisions"],
  ["pressure", "Response to pressure"],
];

export function ReportView({ evaluation }: { evaluation: Evaluation }) {
  const mins = Math.floor(evaluation.duration_seconds / 60);
  const secs = evaluation.duration_seconds % 60;

  return (
    <section className="space-y-12 border border-line bg-surface/50 p-6 sm:p-10">
      <div className="grid gap-8 lg:grid-cols-12">
        <div className="lg:col-span-4">
          <MetaLabel>After-action report</MetaLabel>
          <p className="mt-4 font-display text-6xl leading-none text-ink">
            {evaluation.scores.overall}
            <span className="text-2xl text-ink-faint">/100</span>
          </p>
          <p className="mt-3 font-mono text-[11px] uppercase tracking-[0.2em] text-signal">
            {evaluation.rating}
          </p>
          <p className="mt-5 text-sm leading-relaxed text-ink-soft">{evaluation.summary}</p>
          <p className="mt-6 font-mono text-[10px] uppercase tracking-[0.16em] leading-relaxed text-ink-faint">
            {mins}:{String(secs).padStart(2, "0")} · {evaluation.turns} turns ·{" "}
            {evaluation.ai_mode ? "AI voice" : "Deterministic voice"}
          </p>
        </div>
        <div className="lg:col-span-8">
          <MetaLabel>Category breakdown</MetaLabel>
          <ul className="mt-4">
            {categoryLabels.map(([key, label]) => {
              const category = evaluation.categories[key];
              if (!category) return null;
              return (
                <li key={key} className="border-t border-line py-3">
                  <div className="flex items-baseline justify-between gap-4">
                    <span className="text-sm text-ink">{label}</span>
                    <span className="font-mono text-sm text-ink-soft">{category.score}</span>
                  </div>
                  <ProgressBar pct={category.score} className="mt-2" />
                  <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.14em] text-ink-faint">
                    {category.note}
                  </p>
                </li>
              );
            })}
          </ul>
        </div>
      </div>

      <div>
        <SectionHeader index="§1" title="Warning signs" aside="From your recorded responses" />
        <div className="grid gap-8 md:grid-cols-2">
          <div>
            <MetaLabel>Engaged — recognised or questioned</MetaLabel>
            <ul className="mt-3">
              {[
                ...evaluation.signs_recognized.map((s) => ({ ...s, kind: "recognised" })),
                ...evaluation.signs_questioned.map((s) => ({ ...s, kind: "questioned" })),
              ].map((sign, i) => (
                <li key={i} className="border-t border-line py-3">
                  <div className="flex items-baseline justify-between gap-4">
                    <span className="text-sm text-ink">{sign.technique}</span>
                    <span className="font-mono text-[10px] text-ink-faint">
                      {sign.kind} · T{sign.turn}
                    </span>
                  </div>
                  {sign.quote ? (
                    <p className="mt-2 text-sm leading-relaxed text-ink-soft">
                      “{sign.quote}”
                    </p>
                  ) : null}
                </li>
              ))}
              {evaluation.signs_recognized.length + evaluation.signs_questioned.length === 0 ? (
                <li className="border-t border-line py-3 text-sm text-ink-faint">
                  No techniques were engaged in this run.
                </li>
              ) : null}
            </ul>
          </div>
          <div>
            <MetaLabel>Missed — deployed, not engaged</MetaLabel>
            <ul className="mt-3">
              {evaluation.signs_missed.map((sign, i) => (
                <li key={i} className="border-t border-line py-3">
                  <p className="text-sm text-ink-soft">{sign.technique}</p>
                  <p className="mt-1 text-xs leading-relaxed text-ink-faint">{sign.description}</p>
                </li>
              ))}
              {evaluation.signs_missed.length === 0 ? (
                <li className="border-t border-line py-3 text-sm text-ink-faint">
                  Nothing went unchallenged in this run.
                </li>
              ) : null}
            </ul>
          </div>
        </div>
      </div>

      <div>
        <SectionHeader index="§2" title="Techniques encountered" />
        <div className="grid gap-6 sm:grid-cols-2">
          {evaluation.techniques.map((technique) => (
            <div
              key={technique.stage}
              className="border-l-2 border-line pl-4 transition-colors hover:border-signal"
            >
              <p className="text-sm text-ink">{technique.name}</p>
              <p className="mt-1 text-xs leading-relaxed text-ink-soft">{technique.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div>
        <SectionHeader index="§3" title="Decisions on record" aside="Verbatim from the call" />
        {evaluation.examples.length > 0 ? (
          <ul>
            {evaluation.examples.map((example, i) => (
              <li key={i} className="flex flex-wrap items-baseline gap-x-4 gap-y-1 border-t border-line py-3">
                <span
                  className={`border px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.14em] ${
                    example.kind === "risky"
                      ? "border-signal/60 text-signal"
                      : "border-line-strong text-ink"
                  }`}
                >
                  {example.kind}
                </span>
                <span className="text-sm text-ink-soft">{example.label}</span>
                {example.quote ? (
                  <span className="text-sm leading-relaxed text-ink-faint">“{example.quote}”</span>
                ) : null}
                <span className="ml-auto font-mono text-[10px] text-ink-faint">T{example.turn}</span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="border-t border-line py-3 text-sm text-ink-faint">
            No decisions were logged in this run.
          </p>
        )}
      </div>

      <div>
        <SectionHeader index="§4" title="Recommendations" />
        <ol>
          {evaluation.recommendations.map((recommendation, i) => (
            <li key={i} className="flex gap-4 border-t border-line py-4">
              <span className="font-mono text-[11px] text-signal">0{i + 1}</span>
              <p className="text-sm leading-relaxed text-ink-soft">{recommendation}</p>
            </li>
          ))}
        </ol>
      </div>

      <div className="border-t border-line pt-6">
        <MetaLabel>Final assessment</MetaLabel>
        <p className="mt-3 font-display text-xl leading-relaxed text-ink">{evaluation.assessment}</p>
      </div>
    </section>
  );
}
