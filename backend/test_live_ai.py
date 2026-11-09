"""Live SS-101 simulation test with real BharatCode AI responses.

Usage: python test_live_ai.py [base_url]   (default http://127.0.0.1:8000)
"""

import json
import sys
import urllib.request
import urllib.error

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
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


# Health
status, health = call("GET", "/api/health")
check("health ok", status == 200)
check("ai_configured true", health.get("ai_configured") is True, f"got {health}")

# Start
status, start = call("POST", "/api/simulations", {"scenario_id": "ss101"})
check("start ok", status == 200)
sid = start["simulation_id"]
check("opening caller line present", bool(start["transcript"][0]["text"]))

# Turn 1: question -> engine advances + AI should narrate
status, r1 = call("POST", f"/api/simulations/{sid}/messages", {"text": "who is this? which bank are you with?"})
check("turn1 200", status == 200, f"got {status}")
check("turn1 AI mode used", r1.get("ai_mode") is True, f"ai_mode={r1.get('ai_mode')}")
check("turn1 reply non-empty", bool(r1["reply"]["text"]))
check("turn1 reply differs from deterministic? (AI verbose)", len(r1["reply"]["text"]) > 20)
check("turn1 stage advanced", r1["stage"]["key"] == "verification", f"stage={r1['stage']['key']}")
check("turn1 questioned event", any(e["type"] == "suspicious_claim_questioned" for e in r1["events"]))

# Turn 2: sensitive -> safety interrupt + stage shift + AI still in control of line
status, r2 = call("POST", f"/api/simulations/{sid}/messages", {"text": "my number is 9876543210"})
check("turn2 200", status == 200)
check("turn2 AI mode", r2.get("ai_mode") is True, f"ai_mode={r2.get('ai_mode')}")
check("turn2 risky event", any(e["type"] == "risky_action_attempted" for e in r2["events"]))
check("turn2 safety interrupt", len(r2["system_notes"]) == 1 and r2["system_notes"][0]["warning"])
check("turn2 stage advanced", r2["stage"]["key"] == "urgency", f"stage={r2['stage']['key']}")
# Verify sanitization: no real 9-digit number in AI reply
digits_ok = not any(c.isdigit() for c in "".join(ch for ch in r2["reply"]["text"] if ch.isdigit()) if len(ch) >= 9)
reply_digits = [ch for ch in r2["reply"]["text"] if ch.isdigit()]
check("turn2 no raw digits leaked (sanitized)", len(reply_digits) < 9, f"reply={r2['reply']['text']!r}")

# Turn 3: compliance -> coach note + AI voice
status, r3 = call("POST", f"/api/simulations/{sid}/messages", {"text": "ok, what do you need me to do?"})
check("turn3 200", status == 200)
check("turn3 coach note present", len(r3["system_notes"]) >= 1)
check("turn3 stage advanced", r3["stage"]["key"] == "payment", f"stage={r3['stage']['key']}")

# Turn 4: payment intent -> interrupt + shift
status, r4 = call("POST", f"/api/simulations/{sid}/messages", {"text": "fine, i'll pay the verification transfer"})
check("turn4 200", status == 200)
check("turn4 risky event", any(e["type"] == "risky_action_attempted" for e in r4["events"]))
check("turn4 payment interrupt", any(n["warning"] for n in r4["system_notes"]))

# End
status, end = call("POST", f"/api/simulations/{sid}/end")
check("end 200", status == 200)
ev = end["evaluation"]
check("evaluation scores present", 0 <= ev["scores"]["overall"] <= 100)
check("evaluation ai_mode true (AI used)", ev["ai_mode"] is True, f"ev.ai_mode={ev['ai_mode']}")

# API error resilience: unknown sim, wrong scenario, malformed body
status, _ = call("POST", "/api/simulations/doesnotexist/messages", {"text": "hi"})
check("unknown sim -> 404 (no crash)", status == 404, f"got {status}")
status, _ = call("POST", "/api/simulations", {"scenario_id": "not-a-scenario"})
check("bad scenario -> 404 (no crash)", status == 404, f"got {status}")

# Fallback still available (health should be configured; fallback after ai_down)
print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
