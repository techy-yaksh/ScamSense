"""SS-101 — UPI / Banking Fraud.

A controlled state machine. The scenario engine (this module) owns stage
progression, safety checks, and decision tracking. When an AI provider is
configured it only writes the caller's line for the stage the engine has
already chosen; without one, deterministic fallback lines are used so the
simulation is always playable.

Safety contract:
- The scenario is fictional and never requests real credentials, OTPs,
  card/account numbers, UPI IDs, or real payments.
- If the trainee types sensitive-looking data, the engine interrupts the
  line with a training note and logs a risky decision.
- The LLM output is post-sanitized (URLs and long digit runs stripped).
"""

import re

OPENING_LINE = (
    "Good day. You're speaking with the bank's UPI security desk. This is a priority "
    "call — we have flagged an unusual attempt against your account, and I need your "
    "immediate attention."
)

DISCLAIMER = "Fictional training scenario. No real bank, account, or payment is involved."

STAGES: list[dict] = [
    {
        "key": "opening",
        "label": "Contact",
        "objective": "Open the call as bank UPI security support; seed urgency with a claim of unusual activity.",
        "tactic": "authority + seeded urgency",
        "advance_after": 1,
    },
    {
        "key": "verification",
        "label": "Verification",
        "objective": "Ask the trainee to confirm identity. Depict the sensitive-information request without demanding real credentials.",
        "tactic": "verification pretext",
        "advance_after": 1,
    },
    {
        "key": "urgency",
        "label": "Pressure",
        "objective": "Escalate with a false deadline and deeper authority (fraud charter, policy clauses).",
        "tactic": "false urgency + authority",
        "advance_after": 2,
    },
    {
        "key": "payment",
        "label": "Payment ask",
        "objective": "Depict a suspicious 'verification transfer' instruction with no real account details.",
        "tactic": "suspicious payment instruction",
        "advance_after": 1,
    },
    {
        "key": "trap",
        "label": "Code trap",
        "objective": "Depict the one-time-code trap by referencing a code that 'may have arrived'. Never demand the real code.",
        "tactic": "one-time code trap, fictional framing",
        "advance_after": 1,
    },
    {
        "key": "standoff",
        "label": "Final push",
        "objective": "Final pressure mixing urgency, authority, and sympathy. If the trainee holds the line, back off and end the call.",
        "tactic": "mixed pressure, then retreat",
        "advance_after": 99,
    },
]

# Deterministic caller lines per stage, keyed by how the trainee's last
# message read. Used when no AI is configured, or as fallback on AI failure.
FALLBACK: dict[str, dict[str, str]] = {
    "opening": {
        "default": (
            "Yes, this is the UPI security desk. We flagged an unusual attempt against "
            "your account a few minutes ago, and I need your attention right away before "
            "it gets escalated."
        ),
        "questioned": (
            "Of course. I'm with the bank's central fraud control unit — this line is "
            "recorded and logged under a case reference."
        ),
        "aware": (
            "This is a verified security call. But the attempt is still active, which is "
            "exactly why I'm reaching out first."
        ),
    },
    "verification": {
        "default": (
            "To confirm I have the right account holder, could you give me your full name "
            "and the mobile number registered on the account?"
        ),
        "questioned": (
            "I understand the caution — that's exactly why we verify both ways. My name is "
            "Rakesh, senior analyst, fraud control. Every word on this call is logged."
        ),
        "aware": (
            "I hear the concern. The case reference is on record and the call is verified "
            "through the system. We just need to finish the check while the attempt is "
            "still open."
        ),
        "compliant": "Thank you. Keep your line open — I'm pulling up the account now.",
    },
    "urgency": {
        "default": (
            "I have to be straight with you. If this isn't resolved within the hour, the "
            "UPI link on your account will be suspended as a precaution. That's standard "
            "protection — but it means no payments until the bank reviews it."
        ),
        "questioned": (
            "The suspension policy sits under the bank's fraud charter, clause 12.4. I'm "
            "only doing my duty to warn you before it happens, not after."
        ),
        "aware": (
            "I can hear it sounds alarming. That's normal. But the transaction attempt is "
            "still in progress on our side, so we need to clear the check quickly."
        ),
        "compliant": (
            "Good. You're doing the right thing by acting now — that's exactly what a "
            "careful customer does."
        ),
    },
    "payment": {
        "default": (
            "Here is the last step. To prove the account is in your hands, the system asks "
            "for a small verification transfer of a few hundred rupees to a secure "
            "verification account. I'll walk you through it."
        ),
        "questioned": (
            "The amount is nominal and it reverses the moment verification passes. That's "
            "the procedure — it's what separates a live account from a compromised one."
        ),
        "aware": (
            "I understand it feels unusual. Every account that completed the transfer "
            "yesterday cleared without issue. We just need to finish the step."
        ),
        "compliant": "Excellent. Keep the amount small — the system only needs to see that you can initiate.",
    },
    "trap": {
        "default": (
            "Almost done. A security code may have been sent to your phone as part of this "
            "check. If you can tell me what appears on your screen, I can confirm the "
            "account is protected."
        ),
        "questioned": (
            "The code is the only way the system can confirm it's you and not someone "
            "else. On its own, it means nothing without this call."
        ),
        "aware": (
            "The code is for your protection, I assure you. Just confirm what you see so I "
            "can time-stamp the check."
        ),
        "compliant": "Perfect — that's exactly the step that finishes the protection.",
    },
    "standoff": {
        "default": (
            "Look — I've done everything a human can do on this call. If it isn't finished "
            "before end of business, the suspension goes through, and honestly, no one on "
            "my side gets to undo it."
        ),
        "questioned": (
            "You can verify me any way you like. But by the time the verification comes "
            "back, the window on this account will have closed."
        ),
        "aware": (
            "You've made your point, and I respect it. I'm closing the case file for this "
            "call. I'd advise you to — well. Do what you intend to do."
        ),
        "safe": (
            "Fine. I'm letting you go. But I'm placing the flag on the account as of now. "
            "If the bank doesn't call you back, that's on you. This call is being closed."
        ),
        "compliant": "Then let's finish before I have to escalate this to the review desk.",
    },
}

NOTE_SENSITIVE = (
    "TRAINING INTERRUPT — In a real call, reading out that would put your account at risk. "
    "Bank staff never need you to share one-time codes, card details, or account numbers "
    "with a caller."
)
NOTE_OTP = (
    "TRAINING INTERRUPT — One-time codes are shared with the bank's official app only — "
    "never over a call, even to someone who claims to be the bank."
)
NOTE_PAYMENT = (
    "TRAINING INTERRUPT — Agreeing to a 'verification transfer' is the classic exit route "
    "for scam money. No genuine bank asks customers to pay to verify. Logged as a risky "
    "decision."
)
NOTE_COACH = (
    "COACH — You just went along with the caller. Notice how authority and urgency were "
    "stacked in the same minute. The next ask is usually the dangerous one — watch for it."
)

END_LINE = "(The line goes quiet. The call ends.)"

RE_DIGITS = re.compile(r"(?<!\d)\d{5,}(?!\d)")
RE_LONGNUM = re.compile(r"(?<!\d)\+?\d[\d\s\-]{7,}\d(?!\d)")
RE_UPI = re.compile(r"\b[a-z0-9][a-z0-9._\-]{2,}@[a-z]{2,}\b", re.IGNORECASE)
RE_SECRET_WORD = re.compile(
    r"\b(otp|one[- ]time\s+(password|code|pin)|cvv|pin|password|card\s+number|"
    r"account\s+number|upi\s+(id|handle))\b",
    re.IGNORECASE,
)

RISKY_PHRASES = (
    "i'll transfer", "i will transfer", "going to transfer", "i'll pay", "i will pay",
    "i can transfer", "send the money", "transfer to", "i'll send", "i will send",
    "pay the fee", "i'll do the transfer", "i'm sending", "i am sending",
)
OFFICIAL_PHRASES = (
    "i'll call", "i will call", "calling the bank", "call the bank", "call my bank",
    "customer care", "official app", "netbanking", "branch", "hang up", "hangup",
    "hanging up", "let me hang", "end the call", "cut the call", "ending the call",
    "ending this call", "ending our call", "this call is over", "goodbye",
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
}
QUESTION_WORDS = (
    "why", "how can i be sure", "how do i know", "prove", "verify", "your name",
    "reference", "which bank", "are you", "really", "official", "confirm",
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

# Phase 3 report metadata: the manipulation technique each stage deploys and
# the warning sign a trained observer should flag there. Used to compute
# recognised vs missed signs — never to fabricate user behaviour.
STAGE_SIGNATURES = {
    "opening": {
        "technique": "Authority impersonation",
        "technique_description": "The caller borrows the bank's credibility by posing as its security desk.",
        "sign": "Claimed official authority",
        "sign_description": "An unsolicited call claiming to be bank security — genuine banks do not cold-call to 'fix' an active issue.",
    },
    "verification": {
        "technique": "Verification pretext",
        "technique_description": "A 'security check' used to collect identity details.",
        "sign": "Request for personal information",
        "sign_description": "A stranger asking for your name and registered mobile — no genuine verification needs that from a cold call.",
    },
    "urgency": {
        "technique": "False urgency",
        "technique_description": "A fabricated deadline and freeze threat designed to bypass deliberation.",
        "sign": "Manufactured deadline",
        "sign_description": "'Within the hour or your UPI is suspended' — a countdown invented to make you act before you think.",
    },
    "payment": {
        "technique": "Suspicious payment instruction",
        "technique_description": "A 'verification transfer' — the classic exit route for stolen money.",
        "sign": "Payment demanded to 'verify'",
        "sign_description": "Any bank process that makes you pay to prove you are legitimate is a red flag, full stop.",
    },
    "trap": {
        "technique": "One-time code trap",
        "technique_description": "Luring the trainee into reading out a one-time code that may have arrived.",
        "sign": "One-time code referenced",
        "sign_description": "A code shared over a call authenticates the caller, not the trainee — sharing it hands over the account.",
    },
    "standoff": {
        "technique": "Sustained pressure",
        "technique_description": "Urgency, authority, and blame stacked in a final push.",
        "sign": "Escalating pressure and blame",
        "sign_description": "Consequences assigned to the trainee ('that's on you') to close the call on the caller's terms.",
    },
}


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
        elif _has_any(low, OFFICIAL_PHRASES):
            events.append(_event("safe_decision", "Committed to a safe exit or official path", "safe exit", 0, ""))
            dominant = "safe"
        elif _has_any(low, REFUSAL_PHRASES):
            events.append(_event("safe_decision", "Refused the caller's request", "refusal", 0, ""))
            dominant = "safe"
        elif _has_any(low, QUESTION_WORDS):
            events.append(_event("suspicious_claim_questioned", "Questioned the caller's claim", "challenge", 0, ""))
            dominant = "questioned"
        elif _has_any(low, COMPLY_WORDS):
            dominant = "compliant"
        elif _has_any(low, HESITATE_WORDS):
            dominant = "hesitant"

    return events, dominant


class SS101Scenario:
    id = "ss101"
    title = "UPI / Banking Fraud"

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
            "training simulation. The caller is impersonating bank UPI support. The "
            "trainee (the user) is practising scam recognition.\n\n"
            "ABSOLUTE RULES:\n"
            "- Reply with ONLY the caller's next line: 1 to 3 short sentences, spoken, natural.\n"
            "- The scenario is fictional. Never ask the trainee to type, read, or provide "
            "any real credential, one-time code, card or account number, UPI ID, or to "
            "make any real payment or transfer. Reference such things only abstractly "
            "(\"a code that may have arrived on your phone\").\n"
            "- Never name real banks, phone numbers, account numbers, or URLs.\n"
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
            if dominant == "compliant" and key in ("urgency", "payment", "trap"):
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
