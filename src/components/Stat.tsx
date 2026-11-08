import { MetaLabel } from "./Meta";

export function Stat({ label, value, note }: { label: string; value: string; note?: string }) {
  return (
    <div className="border-l border-line pl-5">
      <MetaLabel>{label}</MetaLabel>
      <p className="mt-3 font-display text-4xl leading-none text-ink sm:text-5xl">{value}</p>
      {note ? (
        <p className="mt-3 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">
          {note}
        </p>
      ) : null}
    </div>
  );
}
