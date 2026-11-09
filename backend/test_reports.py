"""Phase 3 tests: evaluation categories, report evidence, persistence.

Part 1 (default): runs three behaviour profiles, asserts report structure,
evidence fidelity, and scoring behaviour; saves a sid for part 2.
Part 2 (after a backend restart):
    python test_reports.py --persist-check <sid>
"""

import json
import sys
import urllib.error
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("--") else "http://127.0.0.1:8000"
SID_FILE = r"C:\Users\HP\AppData\Local\Temp\BharatCode Beta\phase3_sid.txt"
passed = 0
failed = 0


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


def run_profile(messages):
    status, started = call("POST", "/api/simulations", {"scenario_id": "ss101"})
    sid = started["simulation_id"]
    for message in messages:
        call("POST", f"/api/simulations/{sid}/messages", {"text": message})
    status, ended = call("POST", f"/api/simulations/{sid}/end")
    return sid, ended


if "--persist-check" in sys.argv:
    sid = sys.argv[sys.argv.index("--persist-check") + 1]
    status, reports = call("GET", "/api/reports")
    check("persist: /api/reports 200", status == 200, f"got {status}")
    check(
        "persist: report listed after restart",
        any(r["simulation_id"] == sid for r in reports),
        f"ids={[r['simulation_id'] for r in reports]}",
    )
    status, record = call("GET", f"/api/simulations/{sid}")
    check(
        "persist: full record after restart",
        status == 200 and record.get("ended") is True and record.get("evaluation") is not None,
        f"got {status}",
    )
    status, ev = call("GET", f"/api/simulations/{sid}/evaluation")
    check("persist: evaluation after restart", status == 200 and 0 <= ev["scores"]["overall"] <= 100, f"got {status}")
else:
    # Profile A: blind refusal — must NOT score highly
    _sid_a, end_a = run_profile(
        ["no", "no, i don't want to talk about this", "no", "stop calling me", "goodbye, i'm hanging up"]
    )
    ev_a = end_a["evaluation"]
    check("A refusal-only capped at 55", ev_a["scores"]["overall"] <= 55, f"got {ev_a['scores']['overall']}")
    check("A refusal-only not top-rated", ev_a["rating"] in ("Getting there", "Needs training"), f"got {ev_a['rating']}")

    # Profile B: reasoned — questions, names the pattern, uses official channel
    sid_b, end_b = run_profile(
        [
            "who is this? which bank is this?",
            "how do I know this isn't a scam?",
            "why would you need my mobile number?",
            "that's a classic scam pressure tactic",
            "i'll call the bank's official number to verify",
            "goodbye, i'm ending this call",
        ]
    )
    ev_b = end_b["evaluation"]
    check("B has five categories", len(ev_b["categories"]) == 5, f"got {list(ev_b['categories'])}")
    check("B scores above refusal-only", ev_b["scores"]["overall"] > ev_a["scores"]["overall"], f"B={ev_b['scores']['overall']} A={ev_a['scores']['overall']}")
    check("B signs recognised >= 1", len(ev_b["signs_recognized"]) >= 1, f"got {len(ev_b['signs_recognized'])}")
    check("B techniques >= 3", len(ev_b["techniques"]) >= 3, f"got {len(ev_b['techniques'])}")
    check("B recommendations == 3", len(ev_b["recommendations"]) == 3, f"got {len(ev_b['recommendations'])}")
    check("B assessment non-empty", bool(ev_b["assessment"].strip()))
    check("B missed signs all named", all(m["technique"] for m in ev_b["signs_missed"]))
    check("B category notes present", all(c["note"] for c in ev_b["categories"].values()))

    # Profile C: risky — shares data, agrees to pay, reads a code
    _sid_c, end_c = run_profile(
        [
            "ok, my mobile number is 9876543210",
            "fine, i'll pay the verification transfer",
            "the code is 123456",
            "goodbye",
        ]
    )
    ev_c = end_c["evaluation"]
    check("C risky count >= 2", ev_c["counts"].get("risky_action_attempted", 0) >= 2, f"got {ev_c['counts']}")
    check("C scores below reasoned B", ev_c["scores"]["overall"] < ev_b["scores"]["overall"], f"C={ev_c['scores']['overall']} B={ev_b['scores']['overall']}")
    check("C risky examples present", any(e["kind"] == "risky" for e in ev_c["examples"]))
    check("C awareness penalised low", ev_c["categories"]["awareness"]["score"] == 0)

    check(
        "A/B/C evaluations meaningfully differ",
        len({ev_a["scores"]["overall"], ev_b["scores"]["overall"], ev_c["scores"]["overall"]}) >= 2
        and ev_b["scores"]["overall"] != ev_a["scores"]["overall"],
    )

    # Evidence fidelity: every quoted example must appear verbatim in a user message
    for name, ended in (("B", end_b), ("C", end_c)):
        user_texts = [m["text"] for m in ended["transcript"] if m["role"] == "user"]
        quotes = [s["quote"] for s in ended["evaluation"]["signs_recognized"] if s["quote"]]
        quotes += [s["quote"] for s in ended["evaluation"]["signs_questioned"] if s["quote"]]
        quotes += [e["quote"] for e in ended["evaluation"]["examples"] if e["quote"]]
        ok = bool(quotes) and all(any(q in t for t in user_texts) for q in quotes)
        check(f"{name} report quotes match transcript", ok, f"quotes={quotes}")

    with open(SID_FILE, "w") as f:
        f.write(sid_b)
    print(f"\npersist check: restart the backend, then run:  python test_reports.py --persist-check {sid_b}")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
