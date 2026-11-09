"""Check that a misconfigured/unreachable AI degrades to deterministic lines.

Run with the server started with:
    AI_BASE_URL=http://127.0.0.1:9 AI_API_KEY=test AI_MODEL=test uvicorn main:app
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


status, health = call("GET", "/api/health")
check("health ok", status == 200)
check("ai reported configured", health.get("ai_configured") is True, f"got {health}")

status, start = call("POST", "/api/simulations", {"scenario_id": "ss101"})
check("start ok", status == 200, f"got {status}")
sid = start["simulation_id"]
check("start reports ai configured", start["ai_configured"] is True)

# AI endpoint is unreachable -> first message falls back deterministically
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "hello, who is this?"})
check("message answered", status == 200 and r["reply"]["text"], f"got {status}")
check("fell back to deterministic line", r["ai_mode"] is False, f"ai_mode={r['ai_mode']}")

# Second message: provider marked down, still answered
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "ok, continue"})
check("second message answered", status == 200 and r["reply"]["text"], f"got {status}")
check("still deterministic", r["ai_mode"] is False)

status, end = call("POST", f"/api/simulations/{sid}/end")
check("end ok", status == 200)
check("evaluation ai_mode false", end["evaluation"]["ai_mode"] is False)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
