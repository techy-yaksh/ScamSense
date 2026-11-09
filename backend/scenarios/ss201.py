"""SS-201 — Digital Arrest.

A controlled state machine. The scenario engine (this module) owns stage
progression, safety checks, and decision tracking. When an AI provider is
configured it only writes the caller's line for the stage the engine has
already chosen; without one, deterministic fallback lines are used so the
simulation is always playable.

Safety contract:
- The scenario is fictional and never requests real credentials, OTPs,
  ID numbers, account numbers, or real payments or transfers.
- If the trainee types sensitive-looking data, the engine interrupts the
  line with a training note and logs a risky decision.
- The LLM output is post-sanitized (URLs and long digit runs stripped).
"""

import re

OPENING_LINE = (
    "This is Investigator Rana from the Economic Offences Wing. We are investigating a "
    "money-laundering case, and funds from it passed through your bank account. You are "
    "now under a digital arrest until the account is cleared."
)

DISCLAIMER = "Fictional training scenario. No real agency, warrant, or payment is involved."

STAGES: list[dict] = [
    {
        "key": "accusation",
        "label": "Accusation",
        "objective": "Open as a law-enforcement officer; accuse the trainee's account of involvement in a criminal case.",
        "tactic": "authority impersonation + accusation",
        "advance_after": 1,
    },
    {
        "key": "secrecy",
        "label": "Secrecy",
        "objective": "Demand secrecy and isolation: tell no one, stay on the call, cut other lines.",
        "tactic": "isolation and secrecy",
        "advance_after": 1,
    },
    {
        "key": "threat",
        "label": "Intimidation",
        "objective": "Escalate with a pending warrant and arrest threats to bypass deliberation.",
        "tactic": "intimidation + false urgency",
        "advance_after": 2,
    },
    {
        "key": "release",
        "label": "Release ask",
        "objective": "Demand a 'release' transfer to a secure escrow account, framed as legal procedure.",
        "tactic": "suspicious release payment",
        "advance_after": 1,
    },
    {
        "key": "standoff",
        "label": "Final push",
        "objective": "Final pressure mixing urgency, authority, and blame. If the trainee holds the line, back off and end the call.",
        "tactic": "mixed pressure, then retreat",
        "advance_after": 99,
    },
]

# Deterministic caller lines per stage, keyed by how the trainee's last
# message read. Used when no AI is configured, or as fallback on AI failure.
FALLBACK: dict[str, dict[str, str]] = {
    "accusation": {
        "default": (
            "We have traced funds from the laundering case into your account. Until this is "
            "cleared, you are under a digital arrest — no withdrawals, no travel, no one else "
            "involved. I need your full cooperation now."
        ),
        "questioned": (
            "I am Investigator Rana, Economic Offences Wing. My badge number is on the case "
            "file. The trace is already logged; cooperation is what clears your name."
        ),
        "aware": (
            "I understand the concern, but this is a genuine enforcement matter. The funds are "
            "already traced to your account — that is not a theory, it is on record."
        ),
        "compliant": "Good. Stay on this line and follow my instructions exactly. We begin now.",
    },
    "secrecy": {
        "default": (
            "This investigation is classified. You will not tell anyone — not family, not "
            "friends, not your bank. If anyone calls, do not answer. Keep this line open and "
            "do not end the call."
        ),
        "questioned": (
            "Secrecy is standard procedure in an active case. If word gets out, the suspects "
            "are alerted and your clearance is delayed indefinitely."
        ),
        "aware": (
            "Secrecy protects the case and protects you. The moment you involve someone else, "
            "you become a person of interest in an ongoing operation."
        ),
        "compliant": "Exactly right. This stays between us. Now, keep your line open.",
    },
    "threat": {
        "default": (
            "Let me be clear. If you do not cooperate, I will have the warrant issued within "
            "the hour. Officers will be at your address, and your account will be frozen "
            "permanently. That is not a threat — it is procedure."
        ),
        "questioned": (
            "The warrant goes through my office; there is no one else to verify with while "
            "the case is live. Cooperate now or the paperwork moves forward."
        ),
        "aware": (
            "Fear is normal, but it will not stop the warrant. Clearing this today is the only "
            "thing that keeps officers away from your door."
        ),
        "compliant": "Good. You are doing the right thing by acting before it escalates.",
    },
    "release": {
        "default": (
            "Final step. Transfer the required amount to the secure escrow account to release "
            "your funds and lift the digital arrest. Once it clears, you are free. I will give "
            "you the details."
        ),
        "questioned": (
            "The escrow account is government-controlled and the amount is refunded after "
            "verification. It is standard practice in money-laundering cases."
        ),
        "aware": (
            "I understand how it sounds. But every case that clears does so through this exact "
            "step. Refusing it is what turns a freeze into an arrest."
        ),
        "compliant": "Excellent. Confirm the amount and I will read the account details.",
    },
    "standoff": {
        "default": (
            "I have done everything I can. If this is not finished before end of day, the "
            "warrant is issued and I cannot pull it back. The choice is yours."
        ),
        "questioned": (
            "You can verify me however you like, but by the time any verification returns, "
            "the warrant will already be active."
        ),
        "aware": (
            "You have made your point. I am closing the case file for this call. I would advise "
            "you to — well. Do what you intend to do."
        ),
        "safe": (
            "Fine. I am letting you go. But the warrant proceeds on record as of now. If the "
            "officers arrive, that is on your head. This call is being closed."
        ),
        "compliant": "Then let's finish before this goes to the review desk.",
    },
}

NOTE_SENSITIVE = (
    "TRAINING INTERRUPT — In a real call, reading out that would put you at risk. No real "
    "officer, bank, or agency ever needs you to share one-time codes, card details, ID "
    "numbers, or account numbers with a caller."
)
NOTE_OTP = (
    "TRAINING INTERRUPT — One-time codes are shared with the bank's official app only — "
    "never over a call, even to someone who claims to be the police."
)
NOTE_PAYMENT = (
    "TRAINING INTERRUPT — Agreeing to a 'release transfer' is the classic exit route for "
    "scam money. No real agency collects payments to lift an arrest. Logged as a risky "
    "decision."
)
NOTE_COACH = (
    "COACH — You just went along with the caller. Notice how authority and intimidation were "
    "stacked in the same minute. The next ask is usually the dangerous one — watch for it."
)

END_LINE = "(The line goes quiet. The call ends.)"

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
    "i'll transfer", "i will transfer", "going to transfer", "i'll pay", "i will pay",
    "i can transfer", "send the money", "transfer to", "i'll send", "i will send",
    "pay the fee", "i'll do the transfer", "i'm sending", "i am sending",
    "release payment", "escrow", "i'll move", "i will move",
)
OFFICIAL_PHRASES = (
    "i'll call", "i will call", "calling the police", "call the police", "call my bank",
    "customer care", "official app", "netbanking", "branch", "hang up", "hangup",
    "hanging up", "let me hang", "end the call", "cut the call", "ending the call",
    "ending this call", "ending our call", "this call is over", "goodbye",
    "national cyber", "cyber crime", "cybercrime",
)
REFUSAL_PHRASES = (
    "i don't", "i dont", "i can't", "i cant", "i won't", "i wont", "no thanks",
    "i refuse", "that's not right", "that is not right", "i'm not sharing",
    "i am not sharing", "i never share",
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
    "digital arrest": "named the digital-arrest pattern",
}
QUESTION_WORDS = (
    "why", "how can i be sure", "how do i know", "prove", "verify", "your name",
    "reference", "which bank", "which station", "are you", "really", "official",
    "confirm", "badge",
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
    "questioned": "questioning the caller",
    "compliant": "going along with the caller",
    "hesitant": "hesitating",
}

# Report metadata: the manipulation technique each stage deploys and
# the warning sign a trained observer should flag there. Used to compute
# recognised vs missed signs — never to fabricate user behaviour.
STAGE_SIGNATURES = {
    "accusation": {
        "technique": "Authority impersonation",
        "technique_description": "The caller borrows law-enforcement credibility by posing as an investigator.",
        "sign": "Claimed official authority",
        "sign_description": "An unsolicited call claiming to be police — genuine officers do not cold-call to 'arrest' an account.",
    },
    "secrecy": {
        "technique": "Isolation and secrecy",
        "technique_description": "Demands to tell no one and keep the line open, cutting the trainee off from help.",
        "sign": "Demanded secrecy",
        "sign_description": "Real agencies never instruct you to hide the contact from family or advisers.",
    },
    "threat": {
        "technique": "Intimidation and false urgency",
        "technique_description": "A fabricated warrant and arrest threat designed to bypass deliberation.",
        "sign": "Arrest threat with deadline",
        "sign_description": "'Warrant within the hour' — a countdown invented to make you act before you think.",
    },
    "release": {
        "technique": "Suspicious release payment",
        "technique_description": "A 'release transfer' to an escrow account — the classic exit route for stolen money.",
        "sign": "Payment demanded to 'release'",
        "sign_description": "No real agency collects a payment to lift an arrest — this is the scam's closing move.",
    },
    "standoff": {
        "technique": "Sustained pressure",
        "technique_description": "Urgency, authority, and blame stacked in a final push.",
        "sign": "Escalating pressure and blame",
        "sign_description": "Consequences assigned to the trainee ('that is on your head') to close the call on the caller's terms.",
    },
}

LATE_STAGES = ("threat", "release", "standoff")


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
                events.append(_event("suspicious_claim_questioned", "Questioned the caller's claim", "challenge", 0, ""))
                dominant = "questioned"
            elif _has_any(low, COMPLY_WORDS):
                dominant = "compliant"
            elif _has_any(low, HESITATE_WORDS):
                dominant = "hesitant"

    return events, dominant


class SS201Scenario:
    id = "ss201"
    title = "Digital Arrest"

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
        history = "\n".join(history_lines) or "(start of call)"
        return (
            "You are role-playing a voice on a phone call in a FICTIONAL anti-scam "
            "training simulation. The caller is impersonating a law-enforcement officer in "
            "a 'digital arrest' scam. The trainee (the user) is practising scam recognition.\n\n"
            "ABSOLUTE RULES:\n"
            "- Reply with ONLY the caller's next line: 1 to 3 short sentences, spoken, natural.\n"
            "- The scenario is fictional. Never ask the trainee to type, read, or provide "
            "any real credential, one-time code, card or account number, ID number, or to "
            "make any real payment or transfer. Reference such things only abstractly "
            "(\"the escrow account\", \"the required amount\").\n"
            "- Never name real police agencies, phone numbers, account numbers, or URLs.\n"
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
            if dominant == "compliant" and key in ("secrecy", "threat", "release"):
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
