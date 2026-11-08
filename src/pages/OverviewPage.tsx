import { featuredScenario, scenarios } from "../data/scenarios";
import { overviewStats, recentActivity } from "../data/demo";
import { GhostLink, PrimaryLink } from "../components/Cta";
import { MetaItem, MetaLabel } from "../components/Meta";
import { SectionHeader } from "../components/SectionHeader";
import { Stat } from "../components/Stat";

export function OverviewPage() {
  const featured = featuredScenario;

  return (
    <div className="space-y-16 lg:space-y-20">
      <section className="grid gap-10 lg:grid-cols-12 lg:items-end">
        <div className="lg:col-span-7">
          <p className="flex items-center gap-3 font-mono text-[11px] uppercase tracking-[0.24em] text-ink-faint">
            <span className="h-px w-8 bg-signal" />
            Field manual · Social engineering
          </p>
          <h1 className="mt-6 font-display text-5xl leading-[1.02] text-ink sm:text-6xl">
            Scams are patterns.
            <br />
            <span className="text-ink-soft">Patterns can be read.</span>
          </h1>
          <p className="mt-7 max-w-xl text-base leading-relaxed text-ink-soft">
            ScamSense runs controlled simulations of the social-engineering sequences most
            likely to reach you, then debriefs each attempt against the pattern. No real
            money, no real risk — only the sequence, and the skill to name it.
          </p>
        </div>
        <div className="lg:col-span-5">
          <div className="border border-line p-6 sm:p-8">
            <MetaLabel>Recommended entry point</MetaLabel>
            <p className="mt-4 font-display text-xl text-ink">Case {featured.code}</p>
            <p className="mt-1 text-sm text-ink-soft">{featured.title}</p>
            <div className="mt-6 flex flex-col gap-3">
              <PrimaryLink to={`/scenarios/${featured.id}`} large>
                Start training
              </PrimaryLink>
              <GhostLink to="/scenarios">Browse the library</GhostLink>
            </div>
            <p className="mt-5 font-mono text-[10px] uppercase tracking-[0.18em] text-ink-faint">
              {scenarios.length} cases loaded · Phase 1 build
            </p>
          </div>
        </div>
      </section>

      <section>
        <SectionHeader index="§1" title="Featured case" aside="Updated this cycle" />
        <article className="grid gap-8 border border-line bg-surface/50 p-6 sm:p-10 lg:grid-cols-12">
          <div className="lg:col-span-8">
            <div className="flex flex-wrap items-center gap-3">
              <MetaLabel>Case {featured.code}</MetaLabel>
              <span className="h-3 w-px bg-line-strong" />
              <MetaLabel>Featured</MetaLabel>
            </div>
            <h3 className="mt-4 font-display text-3xl text-ink sm:text-4xl">
              {featured.title}
            </h3>
            <p className="mt-4 max-w-2xl text-[15px] leading-relaxed text-ink-soft">
              {featured.description}
            </p>
          </div>
          <div className="flex flex-col justify-between gap-8 lg:col-span-4 lg:border-l lg:border-line lg:pl-8">
            <div className="space-y-4">
              <MetaItem label="Category" value={featured.category} />
              <MetaItem label="Difficulty" value={featured.difficulty} />
              <MetaItem label="Duration" value={`est. ${featured.durationMinutes} min`} />
            </div>
            <PrimaryLink to={`/scenarios/${featured.id}`}>Open briefing</PrimaryLink>
          </div>
        </article>
      </section>

      <section>
        <SectionHeader index="§2" title="Training snapshot" aside="Sample data" />
        <div className="grid grid-cols-2 gap-x-6 gap-y-10 lg:grid-cols-4">
          {overviewStats.map((stat) => (
            <Stat key={stat.label} label={stat.label} value={stat.value} note={stat.note} />
          ))}
        </div>
      </section>

      <section>
        <SectionHeader index="§3" title="Recent activity" aside="Sample data" />
        <div className="border-b border-line">
          {recentActivity.map((item) => (
            <div
              key={item.id}
              className="grid grid-cols-1 gap-2 border-t border-line py-5 sm:grid-cols-12 sm:items-baseline"
            >
              <span className="font-mono text-[11px] text-ink-faint sm:col-span-3">
                {item.at}
              </span>
              <div className="sm:col-span-6">
                <p className="text-sm text-ink">{item.title}</p>
                <p className="mt-1 text-xs text-ink-faint">{item.detail}</p>
              </div>
              <span className="sm:col-span-3 sm:text-right">
                <span className="inline-block border border-line px-2 py-1 font-mono text-[9px] uppercase tracking-[0.18em] text-ink-soft">
                  {item.tag}
                </span>
              </span>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
