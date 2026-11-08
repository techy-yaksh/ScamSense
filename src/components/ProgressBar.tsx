export function ProgressBar({ pct, className = "" }: { pct: number; className?: string }) {
  const width = Math.min(100, Math.max(0, pct));
  return (
    <div className={`h-1 w-full bg-raised ${className}`} role="progressbar" aria-valuenow={width} aria-valuemin={0} aria-valuemax={100}>
      <div className="h-full bg-signal" style={{ width: `${width}%` }} />
    </div>
  );
}
