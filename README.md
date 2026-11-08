# ScamSense

> **A realistic, interactive fraud awareness and scenario simulation platform.**

ScamSense is an open-source training and simulation environment designed to expose the psychological levers and tactical sequences behind modern cyber scams. Rather than lecturing users on generic safety advice, ScamSense deconstructs real-world attacks—allowing individuals to analyze, experience, and recognize red flags in controlled, interactive scenarios.

---

## 🎯 Purpose & Philosophy

Modern scams do not succeed by exploiting software flaws; they succeed by exploiting human psychology—urgency, authority, social isolation, and financial anxiety. 

ScamSense provides an immersive, briefing-first framework that breaks down:
- **Manipulation Levers:** How threat actors manufacture artificial urgency and leverage authority.
- **De-escalation Habits:** Practical cognitive checkpoints to pause, verify, and dismantle fraudulent sequences.
- **Actionable Debriefs:** High-resolution post-session analysis measuring pattern recognition and cognitive resilience.

---

## 🚀 Key Features

- **📑 Case Briefings (`/scenarios/:id`):** Thorough dossiers on attack vectors, tactics, timelines, and specific objectives before stepping into simulation.
- **⚡ Interactive Simulation Bay (`/scenarios/:id/simulation`):** Realistic runtime environment simulating chat feeds, interactive phone sequences, payment traps, and social engineering arcs.
- **📊 Progress & Performance Dashboard (`/progress`):** Track completed simulations, recognition accuracy scores, active streaks, and recent case activity.
- **🧭 Scenario Library (`/scenarios`):** Categorized by domain (Financial, Law Enforcement Impersonation, Employment) and difficulty level (*Foundation*, *Intermediate*, *Advanced*).
- **🎨 Minimalist, Editorial UI:** Engineered with custom typography, clean telemetry styling, high contrast, and dark mode ergonomics.

---

## 🛡️ Current Scenarios

| Code | Title | Category | Difficulty | Est. Time | Focus Area |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SS-101** | **UPI / Banking Fraud** | Financial | `Intermediate` | 12 min | Payment-link pressure sequences, fake support fee waivers, account freeze threats. |
| **SS-201** | **Digital Arrest** | Law Enforcement Impersonation | `Advanced` | 10 min | Video call intimidation, fake warrants, demands for secrecy, fabricated bail transfers. |
| **SS-301** | **Fake Job / Internship** | Employment | `Foundation` | 8 min | Task-scam mechanics, "pre-selected" offers, out-of-pocket activation and review fees. |

---

## 🛠️ Tech Stack

- **Framework:** [React 19](https://react.dev/)
- **Build Tool:** [Vite 6](https://vite.dev/)
- **Language:** [TypeScript](https://www.typescriptlang.org/)
- **Styling:** [Tailwind CSS v4](https://tailwindcss.com/) via `@tailwindcss/vite`
- **Routing:** [React Router v7](https://reactrouter.com/)
- **Icons:** [Lucide React](https://lucide.dev/)

---

## 📁 Project Structure

```text
ScamSense/
├── public/                 # Static assets
├── src/
│   ├── components/         # Reusable UI components
│   │   ├── AppShell.tsx    # Global layout shell with navigation
│   │   ├── Cta.tsx         # Action buttons and links
│   │   ├── Meta.tsx        # Telemetry and metadata badges
│   │   ├── PageHeader.tsx  # Consistent page headers
│   │   ├── ProgressBar.tsx # Visual completion bar
│   │   ├── ScenarioRow.tsx # Scenario list row item
│   │   ├── SectionHeader.tsx# Section heading divider
│   │   ├── Sidebar.tsx     # Responsive navigation sidebar
│   │   └── Stat.tsx        # Metrics display tile
│   ├── data/               # Scenario definitions and mock progress data
│   │   ├── demo.ts         # User statistics and activity history
│   │   └── scenarios.ts    # Comprehensive scenario repository
│   ├── pages/              # Application route views
│   │   ├── BriefingPage.tsx    # Case overview & tactical breakdown
│   │   ├── OverviewPage.tsx    # User dashboard and featured case
│   │   ├── ProgressPage.tsx    # Completion logs & metrics
│   │   ├── ScenariosPage.tsx   # All scenario listings
│   │   └── SimulationPage.tsx  # Runtime simulation bay
│   ├── App.tsx             # Route declarations
│   ├── index.css           # Tailwind v4 configuration & theme variables
│   ├── main.tsx            # Application entry point
│   └── types.ts            # Core TypeScript interfaces & types
├── index.html              # HTML shell
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite build configuration
```

---

## 🚦 Getting Started

### Prerequisites

Ensure you have **Node.js (v18+)** and **npm** installed.

```bash
node -v
npm -v
```

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/techy-yaksh/ScamSense.git
   cd ScamSense
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the local development server:
   ```bash
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:5173`.

---

## 📜 Available Scripts

- `npm run dev` — Starts the Vite development server with Hot Module Replacement (HMR).
- `npm run build` — Runs the TypeScript type-checker (`tsc --noEmit`) and compiles the production bundle.
- `npm run preview` — Locally previews the built production output.

---

## 🗺️ Roadmap

- [x] **Phase 1: Foundation (Current)**
  - Core routing and responsive editorial UI architecture.
  - Case metadata schema and initial scenario briefings (UPI, Digital Arrest, Fake Job).
  - Telemetry and progress tracking views.
- [ ] **Phase 2: Simulation Engine**
  - Branching decision trees with realistic dynamic chat/SMS/call interfaces.
  - Time-pressured prompt mechanics and deceptive audio/visual cues.
  - Granular post-scenario cognitive debriefing and scoring.
- [ ] **Phase 3: Community & Custom Cases**
  - Schema for user-contributed scam transcripts.
  - Multilingual support for localized scam scripts.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
