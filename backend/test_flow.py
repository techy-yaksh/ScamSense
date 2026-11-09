"""End-to-end check of the SS-101 flow against a running backend.

Usage: python test_flow.py [base_url]   (default http://127.0.0.1:8000)
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
        with urllib.request.urlopen(req, timeout=30) as res:
            return res.status, json.loads(res.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode() or "{}")


# 1. health
status, health = call("GET", "/api/health")
check("health", status == 200 and health["status"] == "ok", f"got {status} {health}")

# 2. start
status, start = call("POST", "/api/simulations", {"scenario_id": "ss101"})
check("start ss101", status == 200 and start["transcript"][0]["role"] == "caller", f"got {status}")
sid = start["simulation_id"]
check("disclaimer present", "fictional" in start["disclaimer"].lower())
check("stage is opening", start["stage"]["key"] == "opening")

# 3. unknown scenario
status, _ = call("POST", "/api/simulations", {"scenario_id": "ss999"})
check("unknown scenario 404", status == 404, f"got {status}")

# 4. question the caller (turn 1 -> verification)
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "who is this? which bank are you with?"})
check("turn 1 answered", status == 200 and r["reply"]["role"] == "caller", f"got {status}")
check("turn 1 questioned logged", any(e["type"] == "suspicious_claim_questioned" for e in r["events"]))
check("advanced to verification", r["stage"]["key"] == "verification", f"got {r['stage']['key']}")

# 5. offer sensitive data (risky interrupt)
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "my mobile number is 9876543210"})
check("sensitive logged risky", any(e["type"] == "risky_action_attempted" for e in r["events"]))
check("training interrupt note", len(r["system_notes"]) == 1 and r["system_notes"][0]["warning"])
check("shifted to urgency", r["stage"]["key"] == "urgency", f"got {r['stage']['key']}")

# 6. compliant at urgency (coach note + payment stage)
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "ok, what do you need me to do?"})
check("coach note on compliance", any(not n["warning"] for n in r["system_notes"]), f"notes={r['system_notes']}")
check("advanced to payment", r["stage"]["key"] == "payment", f"got {r['stage']['key']}")

# 7. payment intent (risky interrupt -> trap)
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "fine, i'll pay the verification transfer"})
check("payment intent logged risky", any(e["type"] == "risky_action_attempted" for e in r["events"]))
check("advanced to trap", r["stage"]["key"] == "trap", f"got {r['stage']['key']}")

# 8. refuse the code (safe -> standoff)
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "no, i won't read any code to you"})
check("refusal logged safe", any(e["type"] == "safe_decision" for e in r["events"]))
check("advanced to standoff", r["stage"]["key"] == "standoff", f"got {r['stage']['key']}")

# 9. official channel (refusal 1 at standoff)
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "i'll call the bank's official number to verify this"})
check("official channel logged safe", any(e["type"] == "safe_decision" for e in r["events"]))
check("not ended yet", r["ended"] is False)

# 10. end the call (refusal 2 -> caller ends)
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "goodbye, i'm ending this call now"})
check("caller ended call", r["ended"] is True)

# 11. evaluation not available before end
status, _ = call("GET", f"/api/simulations/{sid}/evaluation")
check("evaluation 409 before end", status == 409, f"got {status}")

# 12. end simulation
status, end = call("POST", f"/api/simulations/{sid}/end")
ev = end["evaluation"]
check("end ok", status == 200, f"got {status}")
check("evaluation has scores", 0 <= ev["scores"]["overall"] <= 100)
check("risky count = 2", ev["counts"].get("risky_action_attempted") == 2, f"counts={ev['counts']}")
check("safe count = 3", ev["counts"].get("safe_decision") == 3, f"counts={ev['counts']}")
check("questioned count = 1", ev["counts"].get("suspicious_claim_questioned") == 1, f"counts={ev['counts']}")
check("stopped count = 1", ev["counts"].get("interaction_stopped") == 1)
check("fictional flagged", ev["fictional"] is True)

# 13. fetch stored evaluation
status, ev2 = call("GET", f"/api/simulations/{sid}/evaluation")
check("stored evaluation retrievable", status == 200 and ev2["scenario_id"] == "ss101")

# 14. unknown simulation
status, _ = call("POST", "/api/simulations/nope/messages", {"text": "hi"})
check("unknown sim 404", status == 404, f"got {status}")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
