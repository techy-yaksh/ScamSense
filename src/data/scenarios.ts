import type { Scenario } from "../types";

export const scenarios: Scenario[] = [
  {
    id: "upi-banking-fraud",
    code: "SS-101",
    title: "UPI / Banking Fraud",
    category: "Financial",
    difficulty: "Intermediate",
    durationMinutes: 12,
    description:
      "A payment-link pressure sequence: a calm 'support agent', a fabricated fee waiver, and a countdown to move money before your account is 'frozen'.",
    intro: [
      "It starts the way most banking scams start — with an outgoing call, a calm voice, and a problem you didn't know you had. The case walks through a full payment-verification sequence built to move your money while you are still trying to understand the question being asked.",
      "Nothing here is random. Each step in the sequence leans on a specific trust lever: urgency, authority, and the fear of losing access to your own money. Your job is to name them before they work.",
    ],
    objectives: [
      "Recognise the fee-waiver and payment-link pattern used in UPI phishing sequences.",
      "Identify urgency devices — countdowns, freeze threats — as manipulation rather than procedure.",
      "Separate verifiable bank channels from lookalike verification flows.",
      "Articulate, in the debrief, which single message carried the highest leverage.",
    ],
    featured: true,
  },
  {
    id: "digital-arrest",
    code: "SS-201",
    title: "Digital Arrest",
    category: "Law Enforcement Impersonation",
    difficulty: "Advanced",
    durationMinutes: 10,
    description:
      "A fake enforcement officer 'digitally arrests' you for moving funds through your account, then negotiates a 'release' in exchange for a transfer.",
    intro: [
      "No warrant. No court. A video call with a man in uniform, a case number you cannot verify, and a quiet instruction: transfer the money, or the paperwork will follow you home. Digital arrest is among the most psychologically aggressive scams in circulation — it works by removing your ability to think calmly.",
      "This case runs the full arc: accusation, isolation, negotiation, and the offer that feels like relief. You are expected to feel the pressure. The objective is to notice that you are feeling it.",
    ],
    objectives: [
      "Recognise impersonation of law enforcement and 'digital arrest' framing.",
      "Notice isolation tactics — demands for secrecy, instructions to end other calls.",
      "Identify the 'release payment' as the scam's closing move, not a legal procedure.",
      "Hold a verification habit under sustained emotional pressure.",
    ],
  },
  {
    id: "fake-job-internship",
    code: "SS-301",
    title: "Fake Job / Internship",
    category: "Employment",
    difficulty: "Foundation",
    durationMinutes: 8,
    description:
      "An offer that is too clean: an unpaid 'internship' that pays you to 'verify inventory' by funding small activation fees from your own account.",
    intro: [
      "The offer arrives as a compliment. You have been 'pre-selected'. The role needs no experience, the hours are flexible, and the first task is to top up a batch of product links so the company can verify your reliability.",
      "This is the task-scam family — fake jobs, fake internships, fake courier verifications. It targets hope before it targets caution, and it is where many longer sequences begin. This is the shortest case in the library and a good one to start on.",
    ],
    objectives: [
      "Recognise the 'pre-selected, no experience needed' pattern in fake offers.",
      "Identify out-of-pocket 'task fees' as the core extraction mechanic.",
      "Detect the escalation curve: small asks that grow after the first payment.",
      "Practise a stop-and-verify response to an offer that flatters you personally.",
    ],
  },
];

export const featuredScenario: Scenario =
  scenarios.find((s) => s.featured) ?? scenarios[0];

export function getScenario(id: string | undefined): Scenario | undefined {
  return scenarios.find((s) => s.id === id);
}
