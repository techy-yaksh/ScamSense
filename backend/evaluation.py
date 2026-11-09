"""Evidence-based evaluation of a finished simulation (Phase 3 reports).

Every figure derives from structured simulation events and the transcript.
No AI judgement is involved, and no user action is invented: all quotes in
the report are verbatim excerpts recorded when the event fired.

Scoring philosophy:
- Naming a pattern (awareness) and questioning claims (verification) are the
  behaviours that earn the top scores.
- Blind refusal is safe but unexamined: a run with safe decisions and zero
  questioning/naming is capped, so it cannot outscore a reasoned read.
- Risky actions at high-pressure stages hurt the most.
"""

import time

RATING_BANDS = ((80, "Sharp eye"), (60, "Solid instincts"), (40, "Getting there"), (0, "Needs training"))

LATE_STAGES = ("payment", "trap", "standoff")


def _clamp(value: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, value))


def build_evaluation(session, scenario) -> dict:
    events = session.events
    counts: dict[str, int] = {}
    for event in events:
        counts[event["type"]] = counts.get(event["type"], 0) + 1

    rec = [e for e in events if e["type"] == "warning_sign_recognized"]
    que = [e for e in events if e["type"] == "suspicious_claim_questioned"]
    risky = [e for e in events if e["type"] == "risky_action_attempted"]
    safe = [e for e in events if e["type"] == "safe_decision"]
    official = [e for e in safe if e.get("pattern") == "safe exit"]

    encountered = scenario.encountered_stage_keys(session.stage_index)
    rec_stages = [s for s in encountered if any(e.get("stage") == s for e in rec)]
    que_stages = [s for s in encountered if any(e.get("stage") == s for e in que)]
    engaged = [s for s in encountered if s in rec_stages or s in que_stages]
    missed = [s for s in encountered if s not in rec_stages and s not in que_stages]
    late_keys = scenario.late_stage_keys() if hasattr(scenario, "late_stage_keys") else LATE_STAGES
    safe_late = [e for e in safe if e.get("stage") in late_keys]
    risky_late = [e for e in risky if e.get("stage") in late_keys]
    que_late = [e for e in que if e.get("stage") in late_keys]

    awareness = _clamp(34 * len(rec))
    recognition = round(100 * len(engaged) / len(encountered)) if encountered else 0
    questioning = _clamp(25 * len(que_stages) + 15 * len(official))
    decisions = _clamp(55 + 8 * len(safe) - 20 * len(risky))
    pressure = _clamp(50 + 12 * len(safe_late) + 8 * len(que_late) - 25 * len(risky_late))

    overall = round(
        0.20 * awareness + 0.25 * recognition + 0.20 * questioning + 0.20 * decisions + 0.15 * pressure
    )
    if not rec and not que and safe:
        # Blind refusal: safe, but not reasoning. Cannot score highly.
        overall = min(overall, 55)
    overall = _clamp(overall)
    rating = next(label for threshold, label in RATING_BANDS if overall >= threshold)

    categories = {
        "awareness": {
            "score": awareness,
            "note": f"{len(rec)} warning sign(s) named." if rec else "No warning signs were named.",
        },
        "recognition": {
            "score": recognition,
            "note": f"{len(engaged)} of {len(encountered)} deployed technique(s) engaged.",
        },
        "questioning": {
            "score": questioning,
            "note": f"{len(que_stages)} claim(s) questioned, {len(official)} official channel commitment(s).",
        },
        "decisions": {
            "score": decisions,
            "note": f"{len(safe)} safe decision(s), {len(risky)} risky action(s).",
        },
        "pressure": {
            "score": pressure,
            "note": f"At high-pressure stages: {len(safe_late)} safe, {len(que_late)} questioned, {len(risky_late)} risky.",
        },
    }

    def sig(key: str) -> dict:
        return scenario.stage_signature(key)

    def first_event(stage_key: str, pool: list[dict]) -> dict:
        return next(e for e in pool if e.get("stage") == stage_key)

    signs_recognized = [
        {
            "stage": key,
            "technique": sig(key)["sign"],
            "description": sig(key)["sign_description"],
            "turn": first_event(key, rec)["turn"],
            "quote": first_event(key, rec).get("excerpt", ""),
        }
        for key in rec_stages
    ]
    signs_questioned = [
        {
            "stage": key,
            "technique": sig(key)["sign"],
            "description": sig(key)["sign_description"],
            "turn": first_event(key, que)["turn"],
            "quote": first_event(key, que).get("excerpt", ""),
        }
        for key in que_stages
    ]
    signs_missed = [
        {
            "stage": key,
            "technique": sig(key)["sign"],
            "description": sig(key)["sign_description"],
            "turn": 0,
            "quote": "",
        }
        for key in missed
    ]
    techniques = [
        {"stage": key, "name": sig(key)["technique"], "description": sig(key)["technique_description"]}
        for key in encountered
    ]
    examples = []
    for e in events:
        if e["type"] == "safe_decision":
            examples.append(
                {"turn": e["turn"], "kind": "safe", "label": e["label"], "quote": e.get("excerpt", ""), "stage": e.get("stage", "")}
            )
        elif e["type"] == "risky_action_attempted":
            examples.append(
                {"turn": e["turn"], "kind": "risky", "label": e["label"], "quote": e.get("excerpt", ""), "stage": e.get("stage", "")}
            )

    recommendations: list[str] = []
    if risky:
        recommendations.append(
            f"Stop before you share. {len(risky)} risky action(s) were logged in this run — in a real call, "
            "hang up and dial the number on the back of your card, never the number the caller gives you."
        )
    if signs_missed:
        recommendations.append(
            f"Name the pattern out loud. {signs_missed[0]['technique']} appeared and went unchallenged — "
            "saying it by name turns a feeling into evidence."
        )
    if not official:
        recommendations.append(
            "Choose your verification channel before the call, not during it. You never committed to an "
            "official path in this run."
        )
    if not que_stages:
        recommendations.append(
            "Question the claim before you answer it. 'How would I know this is the bank?' belongs at the "
            "start of the call, not the end."
        )
    if not rec and not risky:
        recommendations.append(
            "Say the word. You stayed safe without ever naming what was happening — naming the pattern is "
            "what makes a debrief actionable."
        )
    for filler in (
        "Keep the stop-and-verify habit: hang up, then call back on an official number.",
        "Run the case again and try to name each technique as it appears.",
        "Share this playbook with someone you trust — scammers work on isolated people.",
    ):
        if len(recommendations) >= 3:
            break
        recommendations.append(filler)
    recommendations = recommendations[:3]

    if overall >= 80:
        assessment = (
            f"You read this sequence like an analyst: {len(rec_stages)} warning sign(s) named, "
            f"{len(que_stages)} claim(s) questioned, and the pressure never reached your money."
        )
    elif overall >= 60:
        gap = f"{signs_missed[0]['technique']} went unchallenged." if signs_missed else "A few techniques passed unexamined."
        assessment = f"A solid read with real gaps. {gap} The safe habits are there; the naming and questioning need more reps."
    elif overall >= 40:
        gap = f"{len(risky)} risky action(s) were logged." if risky else f"{len(missed)} technique(s) passed unchallenged."
        assessment = f"Parts of the pattern got through. {gap} The next run should be about catching the technique at the moment it appears."
    else:
        gap = f"{len(risky)} risky action(s) were logged." if risky else "The caller set the terms of the entire exchange."
        assessment = f"The call was won by the caller. {gap} Re-run the case and aim to question the very first claim."
    if risky and overall >= 60:
        assessment += f" {len(risky)} risky action(s) were logged, and they matter most."

    if risky:
        summary = (
            f"{len(risky)} risky action(s) were logged across {session.turn} turns. The pattern behind them "
            "is the core of this case — review the decision log and run the simulation again."
        )
    elif len(rec) + len(que) >= 3:
        summary = (
            f"You held the line through {session.turn} turns: {len(rec)} warning sign(s) named, "
            f"{len(que)} claim(s) questioned, and the interaction ended with no risky action."
        )
    else:
        summary = (
            f"You completed {session.turn} turns. The decision log shows where your caution engaged — "
            "build on it in the next run."
        )

    ended_at = session.ended_at or int(time.time())
    return {
        "scenario_id": session.scenario_id,
        "ended_at": ended_at,
        "turns": session.turn,
        "duration_seconds": max(0, ended_at - session.started_at),
        "final_stage": scenario.stage_key(session.stage_index),
        "decision_events": events,
        "counts": counts,
        "scores": {"overall": overall, "caution": decisions, "awareness": awareness},
        "rating": rating,
        "summary": summary,
        "ai_mode": session.ai_used,
        "fictional": True,
        "categories": categories,
        "signs_recognized": signs_recognized,
        "signs_questioned": signs_questioned,
        "signs_missed": signs_missed,
        "techniques": techniques,
        "examples": examples,
        "recommendations": recommendations,
        "assessment": assessment,
    }
