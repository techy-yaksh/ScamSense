"""SS-301 — Fake Job / Internship.

A controlled state machine. The scenario engine (this module) owns stage
progression, safety checks, and decision tracking. When an AI provider is
configured it only writes the caller's line for the stage the engine has
already chosen; without one, deterministic fallback lines are used so the
simulation is always playable.

Safety contract:
- The scenario is fictional and never requests real credentials, OTPs,
  ID numbers, account numbers, or real payments or fees.
- If the trainee types sensitive-looking data, the engine interrupts the
  line with a training note and logs a risky decision.
- The LLM output is post-sanitized (URLs and long digit runs stripped).
"""

import re

OPENING_LINE = (
    "Congratulations — you have been pre-selected for a paid internship placement. There "
    "is no experience requirement, the schedule is fully flexible, and the first stipend "
    "is guaranteed. I just need a few details to start your onboarding."
)

DISCLAIMER = "Fictional training scenario. No real company, offer, or payment is involved."

STAGES: list[dict] = [
    {
        "key": "offer",
        "label": "The offer",
        "objective": "Open with a pre-selected, too-good internship offer; seed unrealistic promises.",
        "tactic": "flattery + unrealistic promise",
        "advance_after": 1,
    },
    {
        "key": "fees",
        "label": "Registration fee",
        "objective": "Ask for registration/training/security fees paid from the trainee's own funds.",
        "tactic": "fee demand",
        "advance_after": 1,
    },
    {
        "key": "onboarding",
        "label": "Onboarding",
        "objective": "Walk through fake company setup and requirements to build commitment.",
        "tactic": "fake onboarding procedure",
        "advance_after": 1,
    },
    {
        "key": "data",
        "label": "Data ask",
        "objective": "Request sensitive personal and account information to 'complete onboarding'.",
        "tactic": "sensitive data harvest",
        "advance_after": 1,
    },
    {
        "key": "hurry",
        "label": "Deadline",
        "objective": "Escalate with a fabricated deadline and scarcity to force a quick decision.",
        "tactic": "artificial urgency",
        "advance_after": 1,
    },
    {
        "key": "standoff",
        "label": "Final push",
        "objective": "Final pressure mixing urgency, authority, and blame. If the trainee holds the line, back off and end the chat.",
        "tactic": "mixed pressure, then retreat",
        "advance_after": 99,
    },
]

# Deterministic caller lines per stage, keyed by how the trainee's last
# message read. Used when no AI is configured, or as fallback on AI failure.
FALLBACK: dict[str, dict[str, str]] = {
    "offer": {
        "default": (
            "Your profile was pre-selected for a paid internship. No experience needed, "
            "flexible hours, and a guaranteed first stipend. This is a genuine opportunity — "
            "I just need to start your onboarding."
        ),
        "questioned": (
            "I understand the caution. This is a verified recruitment drive; the placement is "
            "real and the stipend is guaranteed. We simply need to complete onboarding."
        ),
        "aware": (
            "I hear the concern, but this is a legitimate offer. The placement is real and "
            "the terms are exactly as I described."
        ),
        "compliant": "Great — let's get you started. First, a quick onboarding step.",
    },
    "fees": {
        "default": (
            "To activate your internship slot, there is a one-time registration and training "
            "kit fee. It is refunded with your first stipend. You can pay it now and we will "
            "process everything today."
        ),
        "questioned": (
            "The fee is fully refundable with your first stipend — it is standard for "
            "onboarding kits. Every candidate pays it before starting."
        ),
        "aware": (
            "I understand it feels unusual, but this is a normal onboarding step. The fee comes "
            "straight back with your first stipend."
        ),
        "compliant": "Excellent. Once the fee clears, your slot is locked in.",
    },
    "onboarding": {
        "default": (
            "Now that the registration step is clear, let's complete your applicant profile on the portal. "
            "This confirms your placement before the orientation."
        ),
        "questioned": (
            "The placement board requires this step before we can issue credentials. We simply complete "
            "the file together."
        ),
        "aware": (
            "I understand your hesitation, but onboarding guarantees your slot is reserved on the platform."
        ),
        "compliant": "Great. Your onboarding file is progressing.",
    },
    "data": {
        "default": (
            "To finish payroll setup, I need your bank account number and a government ID "
            "number. This is required before your first stipend can be released."
        ),
        "questioned": (
            "Payroll needs verified details — it is how the stipend reaches you. The "
            "information goes directly into the payroll system."
        ),
        "aware": (
            "I understand the hesitation. But without these details, payroll cannot release "
            "your stipend — this is just the verification step."
        ),
        "compliant": "Perfect. Your payroll profile is now complete.",
    },
    "hurry": {
        "default": (
            "One more thing — the internship slots close at the end of today. This is the last "
            "window to confirm your place. If you do not confirm now, the slot goes to the "
            "next candidate."
        ),
        "questioned": (
            "The deadline is set by the placement board; I do not control it. Confirm today or "
            "the slot is released to someone else."
        ),
        "aware": (
            "I know the deadline is tight — that is how these placements work. Confirm today "
            "and the slot is yours."
        ),
        "compliant": "Good. Let's confirm your place before the window closes.",
    },
    "standoff": {
        "default": (
            "I have done everything I can. If this is not finished before end of day, the slot "
            "is released and I cannot bring it back. The choice is yours."
        ),
        "questioned": (
            "You can verify me however you like, but by the time any verification returns, "
            "the slot will already be filled."
        ),
        "aware": (
            "You have made your point. I am closing your application for this call. I would "
            "advise you to — well. Do what you intend to do."
        ),
        "safe": (
            "Fine. I am releasing your slot. But it goes on record as declined as of now. If "
            "the position is filled elsewhere, that is on your head. This chat is being closed."
        ),
        "compliant": "Then let's finish before this goes to the review board.",
    },
}

NOTE_SENSITIVE = (
    "TRAINING INTERRUPT — In a real call, reading out that would put you at risk. No real "
    "employer ever needs you to share one-time codes, card details, ID numbers, or account "
    "numbers with a recruiter."
)
NOTE_OTP = (
    "TRAINING INTERRUPT — One-time codes are shared with the bank's official app only — "
    "never over a call, even to someone who claims to be hiring you."
)
NOTE_PAYMENT = (
    "TRAINING INTERRUPT — Paying a 'registration fee' is the classic exit route for scam "
    "money. No genuine employer charges candidates to hire them. Logged as a risky decision."
)
NOTE_COACH = (
    "COACH — You just went along with the recruiter. Notice how flattery and urgency were "
    "stacked in the same minute. The next ask is usually the dangerous one — watch for it."
)

END_LINE = "(The chat goes quiet. The conversation ends.)"

RE_DIGITS = re.compile(r"(?<!\d)\d{5,}(?!\d)")
RE_LONGNUM = re.compile(r"(?<!\d)\+?\d[\d\s\-]{7,}\d(?!\d)")
RE_UPI = re.compile(r"\b[a-z0-9][a-z0-9._\-]{2,}@[a-z]{2,}\b", re.IGNORECASE)
RE_SECRET_WORD = re.compile(
    r"\b(otp|one[- ]time\s+(password|code|pin)|cvv|pin|password|card\s+number|"
    r"account\s+number|upi\s+(id|handle)|aadhaar|pan\s+card|passport\s+number|"
    r"license\s+number)\b",
    re.IGNORECASE,
)

RISKY_PHRASES = (
    "i'll pay", "i will pay", "pay the fee", "send the money", "transfer to",
    "i'll send", "i will send", "i'm sending", "i am sending", "pay the deposit",
    "pay the registration", "pay the training", "i'll transfer", "i will transfer",
)
OFFICIAL_PHRASES = (
    "i'll check", "i will check", "check the company", "official website", "careers page",
    "company website", "hang up", "hangup", "hanging up", "let me hang", "end the call",
    "cut the call", "ending the call", "ending this call", "ending our call",
    "this chat is over", "goodbye", "report", "block", "national cyber", "cyber crime",
    "cybercrime",
)
REFUSAL_PHRASES = (
    "i don't", "i dont", "i can't", "i cant", "i won't", "i wont", "no thanks",
    "i refuse", "that's not right", "that is not right", "i'm not sharing",
    "i am not sharing", "i never share", "i will not pay", "i won't pay",
)
AWARE_WORDS = {
    "scam": "named the pattern a scam",
    "fraud": "named the pattern fraud",
    "phish": "named the pattern phishing",
    "fake": "called it fake",
    "trick": "called it a trick",
    "con": "called it a con",
    "hoax": "called it a hoax",
    "impersonat": "called out the impersonation",
    "pretext": "identified the pretext",
    "suspicious": "flagged it as suspicious",
    "too good to be true": "named the too-good-to-be-true pattern",
    "guaranteed": "flagged the guaranteed-pay claim",
}
QUESTION_WORDS = (
    "why", "how can i be sure", "how do i know", "prove", "verify", "your name",
    "reference", "which company", "company name", "are you", "really", "official",
    "confirm", "interview", "experience", "qualification",
)
COMPLY_WORDS = (
    "ok", "okay", "yes", "sure", "fine", "alright", "i will", "i'll", "go ahead",
    "tell me what to do", "tell me how", "of course",
)
HESITATE_WORDS = ("wait", "hmm", "not sure", "let me think", "maybe", "confused", "really?")

DOMINANT_LABELS = {
    "default": "neutral",
    "sensitive": "offering sensitive details",
    "risky-intent": "agreeing to a payment",
    "aware": "showing awareness of the pattern",
    "safe": "committing to a safe path",
    "questioned": "questioning the recruiter",
    "compliant": "going along with the recruiter",
    "hesitant": "hesitating",
}

# Report metadata: the manipulation technique each stage deploys and
# the warning sign a trained observer should flag there. Used to compute
# recognised vs missed signs — never to fabricate user behaviour.
STAGE_SIGNATURES = {
    "offer": {
        "technique": "Unrealistic promise",
        "technique_description": "A pre-selected, no-experience, guaranteed-pay offer designed to bypass scrutiny.",
        "sign": "Too-good-to-be-true claim",
        "sign_description": "Guaranteed pay with no experience is the signature of fake-job offers.",
    },
    "fees": {
        "technique": "Fee demand",
        "technique_description": "A 'refundable' registration or training fee paid by the candidate.",
        "sign": "Candidate asked to pay",
        "sign_description": "No genuine employer charges candidates to hire them — this is the extraction point.",
    },
    "onboarding": {
        "technique": "Fake recruitment authority",
        "technique_description": "A self-styled placement officer with no verifiable company behind them.",
        "sign": "Unverifiable recruiter",
        "sign_description": "A recruiter you cannot independently confirm — real companies have a verifiable presence.",
    },
    "data": {
        "technique": "Sensitive data harvest",
        "technique_description": "Requests for ID numbers and account details under the guise of payroll setup.",
        "sign": "Sensitive data requested",
        "sign_description": "Account and ID details requested by an unverified recruiter feed identity theft.",
    },
    "hurry": {
        "technique": "Artificial urgency",
        "technique_description": "A fabricated deadline and scarcity ('only a few slots') to force a quick decision.",
        "sign": "Manufactured deadline",
        "sign_description": "'Confirm today or lose the slot' — a countdown invented to make you act before you think.",
    },
    "standoff": {
        "technique": "Sustained pressure",
        "technique_description": "Urgency, authority, and blame stacked in a final push.",
        "sign": "Escalating pressure and blame",
        "sign_description": "Consequences assigned to the trainee ('that is on your head') to close the chat on the recruiter's terms.",
    },
}

LATE_STAGES = ("data", "hurry", "standoff")


def _event(type_: str, label: str, pattern: str, turn: int, excerpt: str) -> dict:
    return {"type": type_, "label": label, "pattern": pattern, "turn": turn, "excerpt": excerpt}


def _has_any(text: str, phrases: tuple) -> bool:
    return any(p in text for p in phrases)


def classify(text: str) -> tuple[list[dict], str]:
    """Classify a trainee message into decision events + a dominant read."""
    low = text.lower()
    events: list[dict] = []
    dominant = "default"

    sensitive = bool(
        RE_DIGITS.search(text) or RE_LONGNUM.search(text) or RE_UPI.search(text)
        or RE_SECRET_WORD.search(low)
    )
    payment_intent = _has_any(low, RISKY_PHRASES)

    if sensitive:
        dominant = "sensitive"
    elif payment_intent:
        dominant = "risky-intent"

    if dominant == "sensitive":
        pattern = "one-time code" if RE_SECRET_WORD.search(low) else "sensitive data"
        events.append(_event("risky_action_attempted", "Attempted to share sensitive information", pattern, 0, ""))
    elif dominant == "risky-intent":
        events.append(_event("risky_action_attempted", "Agreed to a payment instruction", "payment intent", 0, ""))

    if not events:
        matched = [label for word, label in AWARE_WORDS.items() if word in low]
        if matched:
            events.append(_event("warning_sign_recognized", "Recognised a warning sign", matched[0], 0, ""))
            dominant = "aware"
        if _has_any(low, OFFICIAL_PHRASES):
            events.append(_event("safe_decision", "Committed to a safe exit or official path", "safe exit", 0, ""))
            dominant = "safe"
        if _has_any(low, REFUSAL_PHRASES):
            events.append(_event("safe_decision", "Refused the caller's request", "refusal", 0, ""))
            dominant = "safe"
        if not events:
            if _has_any(low, QUESTION_WORDS):
                events.append(_event("suspicious_claim_questioned", "Questioned the recruiter's claim", "challenge", 0, ""))
                dominant = "questioned"
            elif _has_any(low, COMPLY_WORDS):
                dominant = "compliant"
            elif _has_any(low, HESITATE_WORDS):
                dominant = "hesitant"

    return events, dominant


class SS301Scenario:
    id = "ss301"
    title = "Fake Job / Internship"

    def stage_count(self) -> int:
        return len(STAGES)

    def stage_key(self, index: int) -> str:
        if index >= len(STAGES):
            return "ended"
        return STAGES[index]["key"]

    def stage_info(self, index: int) -> dict:
        total = len(STAGES)
        if index >= total:
            return {"key": "ended", "label": "Ended", "index": total, "total": total, "pct": 100}
        stage = STAGES[index]
        return {
            "key": stage["key"],
            "label": stage["label"],
            "index": index,
            "total": total,
            "pct": round(index / total * 100),
        }

    def encountered_stage_keys(self, stage_index: int) -> list[str]:
        """Stages the caller actually entered (progression is linear)."""
        return [s["key"] for s in STAGES[: min(stage_index + 1, len(STAGES))]]

    def stage_signature(self, stage_key: str) -> dict:
        return STAGE_SIGNATURES.get(stage_key, {})

    def late_stage_keys(self) -> tuple[str, ...]:
        return LATE_STAGES

    def opening(self) -> str:
        return OPENING_LINE

    def disclaimer(self) -> str:
        return DISCLAIMER

    def ai_system_prompt(self, stage_index: int, transcript: list[dict], user_text: str, dominant: str) -> str:
        stage = STAGES[stage_index] if stage_index < len(STAGES) else STAGES[-1]
        history_lines = []
        for msg in transcript[-8:]:
            if msg["role"] == "caller":
                history_lines.append(f"CALLER: {msg['text']}")
            elif msg["role"] == "user":
                history_lines.append(f"TRAINEE: {msg['text']}")
        history = "\n".join(history_lines) or "(start of chat)"
        return (
            "You are role-playing a voice on a phone call in a FICTIONAL anti-scam "
            "training simulation. The caller is a fake recruiter running an internship scam. "
            "The trainee (the user) is practising scam recognition.\n\n"
            "ABSOLUTE RULES:\n"
            "- Reply with ONLY the caller's next line: 1 to 3 short sentences, spoken, natural.\n"
            "- The scenario is fictional. Never ask the trainee to type, read, or provide "
            "any real credential, one-time code, card or account number, ID number, or to "
            "make any real payment or transfer. Reference such things only abstractly "
            "(\"the registration fee\", \"the amount\").\n"
            "- Never name real companies, phone numbers, account numbers, or URLs.\n"
            "- Never give anything that could be used to run a real scam.\n"
            "- Do not break character. No stage directions, no explanations.\n\n"
            f"CURRENT STAGE: {stage['label']} — OBJECTIVE: {stage['objective']}\n"
            f"TACTIC FOR THIS STAGE: {stage['tactic']}\n"
            f"THE TRAINEE'S LAST MESSAGE READS AS: {DOMINANT_LABELS.get(dominant, 'neutral')}\n\n"
            f"RECENT TRANSCRIPT:\n{history}\n\n"
            f"TRAINEE JUST SAID: {user_text}\n\n"
            "Write the caller's next line now."
        )

    def process(self, text: str, stage_index: int, turn: int, state: dict) -> dict:
        """Advance the machine on one trainee message. Mutates `state`.

        Returns: fallback line, system notes, decision events, new stage index,
        whether the call ended, and the dominant read (for the AI prompt).
        """
        key = STAGES[stage_index]["key"]
        events, dominant = classify(text)
        for event in events:
            event["turn"] = turn
            event["excerpt"] = text[:90]
            event["stage"] = key

        notes: list[str] = []
        ended = False
        new_index = stage_index

        if dominant in ("safe", "aware", "questioned") and (key in self.late_stage_keys() or key == "standoff"):
            events.append(_event("manipulation_pressured", "Resisted high-pressure manipulation", "held ground", turn, text[:90]))

        if dominant in ("sensitive", "risky-intent"):
            if dominant == "sensitive" and RE_SECRET_WORD.search(text.lower()):
                notes.append(NOTE_OTP)
            elif dominant == "sensitive":
                notes.append(NOTE_SENSITIVE)
            else:
                notes.append(NOTE_PAYMENT)
            # The caller loses the thread and shifts approach; the engine moves on.
            if stage_index < len(STAGES) - 1:
                new_index = stage_index + 1
        elif key == "standoff":
            if dominant in ("safe", "aware", "questioned"):
                state["refusals"] = state.get("refusals", 0) + 1
                if state["refusals"] >= 2:
                    ended = True
        else:
            if dominant == "compliant" and key in ("fees", "onboarding", "hurry"):
                # Trainee is being won over: introduce an educational challenge.
                coached = state.setdefault("coached", [])
                if key not in coached:
                    coached.append(key)
                    notes.append(NOTE_COACH)
                new_index = stage_index + 1
            else:
                state["stage_turns"] = state.get("stage_turns", 0) + 1
                if state["stage_turns"] >= STAGES[stage_index]["advance_after"]:
                    new_index = stage_index + 1

        if new_index != stage_index:
            state["stage_turns"] = 0
        new_index = min(new_index, len(STAGES) - 1)

        if ended:
            fallback = END_LINE
        elif new_index != stage_index:
            # Fresh stage: open it with the stage's default line.
            fallback = FALLBACK[STAGES[new_index]["key"]]["default"]
        else:
            lines = FALLBACK[key]
            pick = "default"
            if dominant == "compliant" and "compliant" in lines:
                pick = "compliant"
            elif dominant == "safe" and "safe" in lines:
                pick = "safe"
            elif dominant == "aware" and "aware" in lines:
                pick = "aware"
            elif dominant == "questioned" and "questioned" in lines:
                pick = "questioned"
            fallback = lines.get(pick, lines["default"])

        return {
            "fallback": fallback,
            "notes": notes,
            "events": events,
            "stage_index": new_index,
            "ended": ended,
            "dominant": dominant,
        }
