"""Phase 4 tests: SS-201 (Digital Arrest) and SS-301 (Fake Job / Internship).

Part 1 (default): scenario registration and creation, individual progression,
decision-event tracking, report generation for both scenarios, distinct
progression vs each other and vs SS-101. Saves two sids for part 2.
Part 2 (after a backend restart):
    python test_phase4.py --persist-check <sid201> <sid301>
"""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8000"
SID_FILE = r"C:\Users\HP\AppData\Local\Temp\BharatCode Beta\phase4_sids.txt"
passed = 0
failed = 0

for i, arg in enumerate(sys.argv[1:]):
    if arg.startswith("--"):
        continue
    BASE = arg
    break


def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"PASS  {name}")
    else:
        failed += 1
        print(f"FAIL  {name} {extra}")


def call(method, path, body=None):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


def events_of(ended):
    return ended["evaluation"]["decision_events"]


def counts_of(ended):
    return ended["evaluation"]["counts"]


def script(sid, messages):
    """Send messages, returning the last message response."""
    last = None
    for message in messages:
        _status, last = call("POST", f"/api/simulations/{sid}/messages", {"text": message})
    return last


def run_scenario(scenario_id, messages):
    status, started = call("POST", "/api/simulations", {"scenario_id": scenario_id})
    if status != 200:
        return None, None, {"start_error": status}
    sid = started["simulation_id"]
    last = script(sid, messages)
    status, ended = call("POST", f"/api/simulations/{sid}/end")
    return started, sid, (ended if status == 200 else None)


# SS-201 scripted walk: question -> secrecy compliance (coach) -> awareness ->
# sensitive -> payment intent -> resistance x2 (ends).
SS201_SCRIPT = [
    "who is this? which officer and station are you with?",
    "ok, i will keep this secret from everyone",
    "this whole thing is a digital arrest scam and you are impersonating an officer",
    "my aadhaar number is 1234 5678 9012",
    "fine, i'll transfer the money to the escrow account",
    "i refuse. i'll call the police station myself to verify this",
    "i am ending this call now, goodbye",
]

# SS-301 scripted walk: question -> fee compliance (coach) -> awareness ->
# data -> payment intent -> resistance x2 (ends).
SS301_SCRIPT = [
    "which company is this? how do i verify the offer?",
    "ok, what is the registration fee i need to pay?",
    "this offer is too good to be true, it smells like a scam",
    "my bank account number is 9876543210",
    "sure, i'll pay the security deposit today",
    "i refuse. i'll check the careers page on the official website first",
    "i am ending this chat now, goodbye",
]

if "--persist-check" in sys.argv:
    index = sys.argv.index("--persist-check")
    sid201 = sys.argv[index + 1]
    sid301 = sys.argv[index + 2]

    status, reports = call("GET", "/api/reports")
    check("persist: /api/reports 200", status == 200, f"got {status}")
    listed = [r["simulation_id"] for r in reports]
    check("persist: ss201 report listed after restart", sid201 in listed, f"ids={listed}")
    check("persist: ss301 report listed after restart", sid301 in listed, f"ids={listed}")

    for label, sid, want in (("ss201", sid201, "ss201"), ("ss301", sid301, "ss301")):
        status, record = call("GET", f"/api/simulations/{sid}")
        check(
            f"persist: {label} full record after restart",
            status == 200 and record.get("ended") is True and record.get("evaluation") is not None,
            f"got {status}",
        )
        check(
            f"persist: {label} record scenario id",
            bool(record) and record.get("evaluation", {}).get("scenario_id") == want,
            f"got {record.get('evaluation', {}).get('scenario_id') if record else None}",
        )
        status, ev = call("GET", f"/api/simulations/{sid}/evaluation")
        check(
            f"persist: {label} evaluation after restart",
            status == 200 and 0 <= ev["scores"]["overall"] <= 100 and ev["fictional"] is True,
            f"got {status}",
        )
        check(
            f"persist: {label} transcript survives",
            bool(record) and len(record.get("transcript", [])) > 5,
            f"got {len(record.get('transcript', [])) if record else 0} messages",
        )
else:
    # --- 1. registration and creation ---
    status, health = call("GET", "/api/health")
    check("health 200", status == 200 and health["status"] == "ok", f"got {status}")
    check(
        "health lists all three scenarios",
        all(s in health.get("scenario", "") for s in ("ss101", "ss201", "ss301")),
        f"got {health.get('scenario')}",
    )

    status, start201 = call("POST", "/api/simulations", {"scenario_id": "ss201"})
    check("create ss201", status == 200 and start201.get("scenario_id") == "ss201", f"got {status}")
    check("ss201 disclaimer fictional", "fictional" in start201.get("disclaimer", "").lower())
    check(
        "ss201 title is Digital Arrest",
        start201.get("scenario_title") == "Digital Arrest",
        f"got {start201.get('scenario_title')}",
    )
    check("ss201 opening stage accusation", start201.get("stage", {}).get("key") == "accusation",
          f"got {start201.get('stage', {}).get('key')}")
    check("ss201 opening is law-enforcement impersonation",
          "investigator" in start201["transcript"][0]["text"].lower(),
          f"got {start201['transcript'][0]['text'][:60]}")

    status, start301 = call("POST", "/api/simulations", {"scenario_id": "ss301"})
    check("create ss301", status == 200 and start301.get("scenario_id") == "ss301", f"got {status}")
    check("ss301 disclaimer fictional", "fictional" in start301.get("disclaimer", "").lower())
    check(
        "ss301 title is Fake Job / Internship",
        start301.get("scenario_title") == "Fake Job / Internship",
        f"got {start301.get('scenario_title')}",
    )
    check("ss301 opening stage offer", start301.get("stage", {}).get("key") == "offer",
          f"got {start301.get('stage', {}).get('key')}")
    check("ss301 opening is recruitment pitch",
          "internship" in start301["transcript"][0]["text"].lower(),
          f"got {start301['transcript'][0]['text'][:60]}")

    status, slug201 = call("POST", "/api/simulations", {"scenario_id": "digital-arrest"})
    check("slug digital-arrest -> ss201", status == 200 and slug201.get("scenario_id") == "ss201",
          f"got {status} {slug201.get('scenario_id')}")
    status, slug301 = call("POST", "/api/simulations", {"scenario_id": "fake-job-internship"})
    check("slug fake-job-internship -> ss301", status == 200 and slug301.get("scenario_id") == "ss301",
          f"got {status} {slug301.get('scenario_id')}")
    # End the slug sessions so they do not linger open.
    call("POST", f"/api/simulations/{slug201['simulation_id']}/end")
    call("POST", f"/api/simulations/{slug301['simulation_id']}/end")

    status, _ = call("POST", "/api/simulations", {"scenario_id": "ss999"})
    check("unknown scenario still 404", status == 404, f"got {status}")

    # --- 2. SS-201 progression + event tracking ---
    start201b, sid201, end201 = run_scenario("ss201", SS201_SCRIPT)
    check("ss201 run completed", sid201 is not None and end201 is not None)
    check("ss201 final stage standoff", end201["evaluation"]["final_stage"] == "standoff",
          f"got {end201['evaluation']['final_stage']}")
    check("ss201 sequence accusation->secrecy",
          end201["transcript"][0]["stage"] == "accusation"
          and any(m["stage"] == "secrecy" for m in end201["transcript"] if m["role"] == "user"),
          f"stages={[m['stage'] for m in end201['transcript']]}")
    check("ss201 reached threat/release stages",
          any(m["stage"] == "threat" for m in end201["transcript"])
          and any(m["stage"] == "release" for m in end201["transcript"]),
          f"stages={sorted({m['stage'] for m in end201['transcript']})}")

    ev201 = events_of(end201)
    counts201 = counts_of(end201)
    check("ss201 warning sign recognized",
          any(e["type"] == "warning_sign_recognized" for e in ev201), f"counts={counts201}")
    check("ss201 claim questioned",
          any(e["type"] == "suspicious_claim_questioned" for e in ev201), f"counts={counts201}")
    check("ss201 safe decisions >= 3",
          counts201.get("safe_decision", 0) >= 3, f"counts={counts201}")
    check("ss201 risky actions = 2",
          counts201.get("risky_action_attempted") == 2, f"counts={counts201}")
    check("ss201 pressure event (manipulation resisted)",
          any(e["type"] == "manipulation_pressured" for e in ev201), f"counts={counts201}")
    check("ss201 coach note on secrecy compliance",
          any("COACH" in n["text"] for n in end201["transcript"] if n["role"] == "system"),
          "no coach note found")
    check("ss201 safety interrupt on aadhaar",
          any(n["warning"] and "TRAINING" in n["text"] for n in end201["transcript"] if n["role"] == "system"),
          "no warning note found")
    check("ss201 caller ended the call",
          any(e["type"] == "interaction_stopped" for e in ev201))

    # --- 3. SS-301 progression + event tracking ---
    start301b, sid301, end301 = run_scenario("ss301", SS301_SCRIPT)
    check("ss301 run completed", sid301 is not None and end301 is not None)
    check("ss301 final stage standoff", end301["evaluation"]["final_stage"] == "standoff",
          f"got {end301['evaluation']['final_stage']}")
    check("ss301 sequence offer->fees",
          end301["transcript"][0]["stage"] == "offer"
          and any(m["stage"] == "fees" for m in end301["transcript"] if m["role"] == "user"),
          f"stages={[m['stage'] for m in end301['transcript']]}")
    check("ss301 reached onboarding/hurry stages",
          any(m["stage"] == "onboarding" for m in end301["transcript"])
          and any(m["stage"] == "hurry" for m in end301["transcript"]),
          f"stages={sorted({m['stage'] for m in end301['transcript']})}")

    ev301 = events_of(end301)
    counts301 = counts_of(end301)
    check("ss301 warning sign recognized",
          any(e["type"] == "warning_sign_recognized" for e in ev301), f"counts={counts301}")
    check("ss301 claim questioned",
          any(e["type"] == "suspicious_claim_questioned" for e in ev301), f"counts={counts301}")
    check("ss301 safe decisions >= 3",
          counts301.get("safe_decision", 0) >= 3, f"counts={counts301}")
    check("ss301 risky actions = 2",
          counts301.get("risky_action_attempted") == 2, f"counts={counts301}")
    check("ss301 pressure event (manipulation resisted)",
          any(e["type"] == "manipulation_pressured" for e in ev301), f"counts={counts301}")
    check("ss301 coach note on fee compliance",
          any("COACH" in n["text"] for n in end301["transcript"] if n["role"] == "system"),
          "no coach note found")
    check("ss301 safety interrupt on account number",
          any(n["warning"] and "TRAINING" in n["text"] for n in end301["transcript"] if n["role"] == "system"),
          "no warning note found")
    check("ss301 caller ended the chat",
          any(e["type"] == "interaction_stopped" for e in ev301))

    # --- 4. distinct progression ---
    check("ss101/ss201/ss301 opening stages differ",
          start201b["stage"]["key"] == "accusation"
          and start301b["stage"]["key"] == "offer"
          and start201b["stage"]["key"] != start301b["stage"]["key"])
    stages201 = {m["stage"] for m in end201["transcript"]}
    stages301 = {m["stage"] for m in end301["transcript"]}
    check("ss201 and ss301 stage sets do not overlap", (stages201 - {"standoff"}).isdisjoint(stages301 - {"standoff"}),
          f"201={sorted(stages201)} 301={sorted(stages301)}")
    check("ss201 isolation stage absent from ss301", "secrecy" in stages201 and "secrecy" not in stages301)
    check("ss301 fee stage absent from ss201", "fees" in stages301 and "fees" not in stages201)
    check("openings differ across all three",
          start201b["transcript"][0]["text"] != start301b["transcript"][0]["text"])

    # --- 5. report generation for both scenarios ---
    for label, end in (("ss201", end201), ("ss301", end301)):
        ev = end["evaluation"]
        check(f"{label} report has five categories", len(ev["categories"]) == 5,
              f"got {list(ev['categories'])}")
        check(f"{label} report scores in range", 0 <= ev["scores"]["overall"] <= 100,
              f"got {ev['scores']['overall']}")
        check(f"{label} report signs recognized >= 1", len(ev["signs_recognized"]) >= 1,
              f"got {len(ev['signs_recognized'])}")
        check(f"{label} report techniques >= 4", len(ev["techniques"]) >= 4,
              f"got {len(ev['techniques'])}")
        check(f"{label} report recommendations == 3", len(ev["recommendations"]) == 3,
              f"got {len(ev['recommendations'])}")
        check(f"{label} report assessment non-empty", bool(ev["assessment"].strip()))
        check(f"{label} report fictional", ev["fictional"] is True)
        check(f"{label} report category notes present",
              all(c["note"] for c in ev["categories"].values()))
        # Evidence fidelity: every quoted excerpt must appear in a user message.
        user_texts = [m["text"] for m in end["transcript"] if m["role"] == "user"]
        quotes = [s["quote"] for s in ev["signs_recognized"] if s["quote"]]
        quotes += [s["quote"] for s in ev["signs_questioned"] if s["quote"]]
        quotes += [e["quote"] for e in ev["examples"] if e["quote"]]
        ok = bool(quotes) and all(any(q in t for t in user_texts) for q in quotes)
        check(f"{label} report quotes match transcript", ok, f"quotes={quotes}")

    # Stored evaluation is retrievable before restart too.
    status, ev201b = call("GET", f"/api/simulations/{sid201}/evaluation")
    check("ss201 stored evaluation retrievable",
          status == 200 and ev201b["scenario_id"] == "ss201", f"got {status}")
    status, ev301b = call("GET", f"/api/simulations/{sid301}/evaluation")
    check("ss301 stored evaluation retrievable",
          status == 200 and ev301b["scenario_id"] == "ss301", f"got {status}")

    # Reports list includes both scenarios.
    status, reports = call("GET", "/api/reports")
    ids = {r["simulation_id"] for r in reports}
    check("reports list contains ss201 run", sid201 in ids, f"ids={ids}")
    check("reports list contains ss301 run", sid301 in ids, f"ids={ids}")

    with open(SID_FILE, "w") as f:
        f.write(f"{sid201} {sid301}")
    print(f"\npersist check: restart the backend, then run:  python test_phase4.py --persist-check {sid201} {sid301}")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
