import { Navigate, Route, Routes } from "react-router-dom";
import { AppShell } from "./components/AppShell";
import { BriefingPage } from "./pages/BriefingPage";
import { OverviewPage } from "./pages/OverviewPage";
import { ProgressPage } from "./pages/ProgressPage";
import { ReportPage } from "./pages/ReportPage";
import { ScenariosPage } from "./pages/ScenariosPage";
import { SimulationPage } from "./pages/SimulationPage";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<OverviewPage />} />
        <Route path="scenarios" element={<ScenariosPage />} />
        <Route path="scenarios/:id" element={<BriefingPage />} />
        <Route path="scenarios/:id/simulation" element={<SimulationPage />} />
        <Route path="progress" element={<ProgressPage />} />
        <Route path="reports/:simulationId" element={<ReportPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
