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
        description="Every scenario is a documented social-engineering sequence, stripped of the real victim. Read the briefing, work the objectives, and enter the live interactive simulation."
      />
      <div className="border-b border-line">
        {scenarios.map((scenario) => (
          <ScenarioRow key={scenario.id} scenario={scenario} />
        ))}
      </div>
      <p className="mt-6 font-mono text-[10px] uppercase tracking-[0.2em] text-ink-faint">
        Library · {scenarios.length} of {scenarios.length} cases · Interactive runtime
      </p>
    </div>
  );
}
