import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";

export function PrimaryLink({
  to,
  children,
  large = false,
}: {
  to: string;
  children: ReactNode;
  large?: boolean;
}) {
  return (
    <Link
      to={to}
      className={`group inline-flex items-center justify-center gap-3 bg-signal font-mono uppercase tracking-[0.2em] text-bg transition-colors hover:bg-ink ${
        large ? "px-8 py-5 text-sm" : "px-6 py-3.5 text-xs"
      }`}
    >
      <span>{children}</span>
      <ArrowRight
        size={large ? 18 : 15}
        className="transition-transform group-hover:translate-x-1"
      />
    </Link>
  );
}

export function GhostLink({ to, children }: { to: string; children: ReactNode }) {
  return (
    <Link
      to={to}
      className="inline-flex items-center justify-center gap-2 border border-line-strong px-6 py-3.5 font-mono text-xs uppercase tracking-[0.2em] text-ink-soft transition-colors hover:border-signal hover:text-signal"
    >
      {children}
    </Link>
  );
}
