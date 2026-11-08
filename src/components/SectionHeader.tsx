export function SectionHeader({
  index,
  title,
  aside,
}: {
  index: string;
  title: string;
  aside?: string;
}) {
  return (
    <div className="mb-7 flex items-end justify-between gap-4 border-b border-line pb-4">
      <div className="flex items-baseline gap-4">
        <span className="font-mono text-[11px] text-ink-faint">{index}</span>
        <h2 className="font-display text-xl text-ink sm:text-2xl">{title}</h2>
      </div>
      {aside ? (
        <span className="hidden font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint sm:block">
          {aside}
        </span>
      ) : null}
    </div>
  );
}
