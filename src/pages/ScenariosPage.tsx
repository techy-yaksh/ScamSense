import { scenarios } from "../data/scenarios";
import { PageHeader } from "../components/PageHeader";
import { ScenarioRow } from "../components/ScenarioRow";

export function ScenariosPage() {
  return (
    <div>
      <PageHeader
        index="02"
        kicker="Scenario library"
        title="Three cases. Three pressure points."
        description="Every scenario is a documented social-engineering sequence, stripped of the real victim. Read the briefing, work the objectives, then run the simulation once the Phase 2 runtime lands."
      />
      <div className="border-b border-line">
        {scenarios.map((scenario) => (
          <ScenarioRow key={scenario.id} scenario={scenario} />
        ))}
      </div>
      <p className="mt-6 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">
        Library · {scenarios.length} of {scenarios.length} cases · Phase 1
      </p>
    </div>
  );
}
