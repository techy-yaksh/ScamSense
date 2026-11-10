import { useState, type FormEvent } from "react";
import { CornerDownLeft } from "lucide-react";

export function Composer({
  onSend,
  disabled,
  endedByCaller,
}: {
  onSend: (text: string) => void;
  disabled: boolean;
  endedByCaller: boolean;
}) {
  const [draft, setDraft] = useState("");

  function handleSubmit(e: FormEvent) {
    e.preventDefault();
    const text = draft.trim();
    if (!text || disabled || endedByCaller) return;
    setDraft("");
    onSend(text);
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 border border-line bg-surface/50">
      <div className="flex items-center justify-between border-b border-line/60 px-4 py-2 bg-surface/30">
        <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">
          Your Response
        </span>
        <span className="font-mono text-[10px] text-ink-faint">
          {draft.length > 0 ? `${draft.length}/600 chars` : "Press Enter to send"}
        </span>
      </div>

      <div className="flex flex-col gap-3 p-3 sm:flex-row sm:items-center sm:gap-2">
        <div className="flex min-w-0 flex-1 items-center gap-2.5 px-2">
          <span className="font-mono text-sm text-signal select-none">&gt;</span>
          <input
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            placeholder={
              endedByCaller
                ? "Call ended by caller. Click End Simulation to proceed to debrief."
                : "Type your response to the caller (verify, challenge, refuse, or exit)…"
            }
            maxLength={600}
            disabled={disabled || endedByCaller}
            className="min-w-0 flex-1 bg-transparent py-2 text-sm text-ink placeholder:text-ink-faint/70 focus:outline-none disabled:opacity-40"
          />
        </div>

        <button
          type="submit"
          disabled={disabled || endedByCaller || !draft.trim()}
          className="inline-flex shrink-0 items-center justify-center gap-2 border border-signal bg-signal/90 px-5 py-2.5 font-mono text-[11px] uppercase tracking-[0.2em] text-bg font-medium transition-colors hover:bg-signal disabled:border-line disabled:bg-surface disabled:text-ink-faint disabled:opacity-40"
        >
          {disabled ? "Sending…" : "Transmit"}
          <CornerDownLeft size={13} />
        </button>
      </div>

      {endedByCaller ? (
        <div className="border-t border-signal/40 bg-signal/10 px-4 py-2.5">
          <p className="font-mono text-[10px] uppercase tracking-[0.18em] text-signal">
            [Channel terminated] Caller has closed the connection. End the simulation to generate your intelligence debrief.
          </p>
        </div>
      ) : null}
    </form>
  );
}
