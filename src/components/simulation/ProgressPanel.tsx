import type { DecisionEvent, StageInfo } from "../../lib/api";
import { MetaLabel } from "../Meta";
import { ProgressBar } from "../ProgressBar";

export const eventMeta: Record<string, { label: string; className: string }> = {
  warning_sign_recognized: { label: "Pattern named", className: "border-line-strong text-ink" },
  suspicious_claim_questioned: { label: "Claim questioned", className: "border-line-strong text-ink" },
  safe_decision: { label: "Safe move", className: "border-line-strong text-ink" },
  risky_action_attempted: { label: "Risk logged", className: "border-signal/60 text-signal" },
  interaction_stopped: { label: "Interaction ended", className: "border-line text-ink-faint" },
};

export function ProgressPanel({
  stage,
  turn,
  events,
  onEnd,
  ending,
}: {
  stage: StageInfo | null;
  turn: number;
  events: DecisionEvent[];
  onEnd: () => void;
  ending: boolean;
}) {
  return (
    <aside className="flex flex-col border border-line p-5">
      <div className="flex items-baseline justify-between">
        <MetaLabel>Scenario progress</MetaLabel>
        <span className="font-mono text-[10px] text-ink-faint">
          {stage ? `${stage.index + 1} / ${stage.total}` : "—"}
        </span>
      </div>
      <p className="mt-3 font-display text-xl text-ink">{stage?.label ?? "—"}</p>
      <ProgressBar pct={stage?.pct ?? 0} className="mt-4" />
      <p className="mt-4 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">
        Turns · {turn}
      </p>

      <div className="mt-5 border-t border-line pt-4">
        <MetaLabel>Decision log</MetaLabel>
        <div className="mt-2 max-h-44 overflow-y-auto">
          {events.length === 0 ? (
            <p className="py-2 text-xs text-ink-faint">No decisions logged yet.</p>
          ) : (
            events.map((event, i) => (
              <div
                key={`${event.turn}-${i}`}
                className="flex items-center justify-between gap-3 border-t border-line py-2.5 first:border-t-0"
              >
                <span
                  className={`border px-2 py-0.5 font-mono text-[9px] uppercase tracking-[0.14em] ${
                    eventMeta[event.type]?.className ?? "border-line text-ink-faint"
                  }`}
                >
                  {eventMeta[event.type]?.label ?? event.type}
                </span>
                <span className="text-right font-mono text-[10px] text-ink-faint">T{event.turn}</span>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="mt-auto pt-6">
        <button
          onClick={onEnd}
          disabled={ending}
          className="w-full border border-line-strong px-6 py-3.5 font-mono text-xs uppercase tracking-[0.2em] text-ink-soft transition-colors hover:border-signal hover:text-signal disabled:opacity-40"
        >
          {ending ? "Closing…" : "End simulation"}
        </button>
      </div>
    </aside>
  );
}
