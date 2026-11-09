"""Focused launch test: start the UPI scenario using the frontend slug.

Usage: python test_launch_upi.py [base_url]   (default http://127.0.0.1:8000)
"""

import json
import sys
import urllib.error
import urllib.request

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
check("health ok", status == 200, f"got {status}")

# Frontend slug must launch the same simulation as ss101
status, slug = call("POST", "/api/simulations", {"scenario_id": "upi-banking-fraud"})
check("start via frontend slug 200", status == 200, f"got {status}")
check("slug resolves to ss101", slug.get("scenario_id") == "ss101", f"got {slug.get('scenario_id')}")
check("slug start has opening line", bool(slug.get("transcript")) and slug["transcript"][0]["role"] == "caller")
check("slug start stage is opening", slug.get("stage", {}).get("key") == "opening")

status, direct = call("POST", "/api/simulations", {"scenario_id": "ss101"})
check("start via ss101 200", status == 200, f"got {status}")

status, _ = call("POST", "/api/simulations", {"scenario_id": "digital-arrest"})
check("unsupported scenario 404", status == 404, f"got {status}")

# The slug-started session must be fully playable
sid = slug["simulation_id"]
status, r = call("POST", f"/api/simulations/{sid}/messages", {"text": "who is this? which bank are you with?"})
check("slug session accepts a message", status == 200 and r["reply"]["role"] == "caller", f"got {status}")
status, end = call("POST", f"/api/simulations/{sid}/end")
check("slug session can be ended", status == 200 and end["evaluation"]["scenario_id"] == "ss101", f"got {status}")

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
