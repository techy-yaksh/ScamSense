import { NavLink } from "react-router-dom";

const items = [
  { to: "/", label: "Overview", index: "01", end: true },
  { to: "/scenarios", label: "Scenarios", index: "02", end: false },
  { to: "/progress", label: "Progress", index: "03", end: false },
];

function Brand() {
  return (
    <div className="flex items-center gap-3">
      <div className="relative h-9 w-9 shrink-0 border border-line-strong">
        <div className="absolute bottom-1.5 left-1.5 h-2 w-2 bg-signal" />
        <div className="absolute right-1.5 top-1.5 h-2 w-2 border border-ink-faint" />
      </div>
      <div>
        <p className="font-display text-lg leading-none text-ink">ScamSense</p>
        <p className="mt-1.5 font-mono text-[9px] uppercase tracking-[0.24em] text-ink-faint">
          SE / Awareness Sim
        </p>
      </div>
    </div>
  );
}

function DesktopNav() {
  return (
    <nav className="mt-12">
      <p className="mb-3 px-4 font-mono text-[10px] uppercase tracking-[0.22em] text-ink-faint">
        Index
      </p>
      <ul>
        {items.map((item) => (
          <li key={item.to}>
            <NavLink
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `flex items-baseline gap-4 border-l-2 px-4 py-3.5 transition-colors ${
                  isActive
                    ? "border-signal bg-surface text-ink"
                    : "border-transparent text-ink-soft hover:border-line-strong hover:text-ink"
                }`
              }
            >
              {({ isActive }) => (
                <>
                  <span
                    className={`font-mono text-[10px] ${
                      isActive ? "text-signal" : "text-ink-faint"
                    }`}
                  >
                    {item.index}
                  </span>
                  <span className="text-sm font-medium tracking-wide">{item.label}</span>
                </>
              )}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
}

function MetaFooter() {
  return (
    <div className="mt-auto border-t border-line pt-6">
      <dl className="space-y-2 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">
        <div className="flex justify-between">
          <dt>System</dt>
          <dd className="text-ink-soft">ScamSense</dd>
        </div>
        <div className="flex justify-between">
          <dt>Case files</dt>
          <dd className="text-ink-soft">03</dd>
        </div>
        <div className="flex justify-between">
          <dt>Mode</dt>
          <dd className="text-ink-soft">Interactive</dd>
        </div>
      </dl>
    </div>
  );
}

export function Sidebar() {
  return (
    <>
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 flex-col border-r border-line bg-bg px-6 py-8 lg:flex">
        <Brand />
        <DesktopNav />
        <MetaFooter />
      </aside>
      <header className="sticky top-0 z-40 border-b border-line bg-bg lg:hidden">
        <div className="flex items-center justify-between px-5 pb-1 pt-4">
          <Brand />
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-2 pt-2">
          {items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `whitespace-nowrap border-b-2 px-3 py-2 font-mono text-[11px] uppercase tracking-[0.14em] transition-colors ${
                  isActive
                    ? "border-signal text-ink"
                    : "border-transparent text-ink-faint hover:text-ink-soft"
                }`
              }
            >
              <span className="mr-1.5 text-ink-faint/70">{item.index}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>
      </header>
    </>
  );
}
