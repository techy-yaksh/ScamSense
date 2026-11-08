import type { ReactNode } from "react";
import type { Difficulty } from "../types";

export function MetaLabel({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  return (
    <span
      className={`font-mono text-[10px] uppercase tracking-[0.22em] text-ink-faint ${className}`}
    >
      {children}
    </span>
  );
}

const difficultyStyles: Record<Difficulty, string> = {
  Foundation: "border-line text-ink-soft",
  Intermediate: "border-line-strong text-ink",
  Advanced: "border-signal/60 text-signal",
};

export function DifficultyBadge({ level }: { level: Difficulty }) {
  return (
    <span
      className={`inline-flex items-center border px-2.5 py-1 font-mono text-[10px] uppercase tracking-[0.18em] ${difficultyStyles[level]}`}
    >
      {level}
    </span>
  );
}

export function MetaItem({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-baseline gap-4">
      <MetaLabel className="shrink-0">{label}</MetaLabel>
      <span className="font-mono text-xs text-ink-soft">{value}</span>
    </div>
  );
}
