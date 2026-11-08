import type { ReactNode } from "react";
import { MetaLabel } from "./Meta";

export function PageHeader({
  index,
  kicker,
  title,
  description,
  aside,
}: {
  index: string;
  kicker: string;
  title: string;
  description?: string;
  aside?: ReactNode;
}) {
  return (
    <header className="mb-12">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="font-mono text-[11px] text-signal">{index}</span>
          <MetaLabel>{kicker}</MetaLabel>
        </div>
        {aside}
      </div>
      <h1 className="mt-5 max-w-3xl font-display text-4xl leading-[1.05] text-ink sm:text-5xl">
        {title}
      </h1>
      {description ? (
        <p className="mt-5 max-w-2xl text-[15px] leading-relaxed text-ink-soft">{description}</p>
      ) : null}
    </header>
  );
}
