"""Simulation session store: in-memory cache backed by SQLite (Phase 3)."""

import json
import threading
import time

import db


class SimulationSession:
    def __init__(self, sid: str, scenario_id: str, scenario_title: str):
        self.id = sid
        self.scenario_id = scenario_id
        self.scenario_title = scenario_title
        self.started_at = int(time.time())
        self.ended = False
        self.ended_at: int | None = None
        self.transcript: list[dict] = []
        self.events: list[dict] = []
        self.stage_index = 0
        self.turn = 0
        self.evaluation: dict | None = None
        self.ai_down = False
        self.ai_failures = 0
        self.ai_used = False
        self.scenario_state: dict = {}


_sessions: dict[str, SimulationSession] = {}
_lock = threading.Lock()


def create(sid: str, scenario_id: str, scenario_title: str) -> SimulationSession:
    session = SimulationSession(sid, scenario_id, scenario_title)
    with _lock:
        _sessions[sid] = session
    db.save_session(session)
    return session


def get(sid: str) -> SimulationSession | None:
    with _lock:
        return _sessions.get(sid)


def hydrate() -> None:
    """Load every persisted simulation (in-flight and completed) into memory."""
    for row in db.load_all():
        session = SimulationSession(row["id"], row["scenario_id"], "")
        session.started_at = row["started_at"]
        session.ended_at = row["ended_at"]
        session.ended = row["ended_at"] is not None
        session.transcript = json.loads(row["transcript"] or "[]")
        session.events = json.loads(row["events"] or "[]")
        session.scenario_state = json.loads(row["scenario_state"] or "{}")
        session.stage_index = row["stage_index"]
        session.turn = row["turn"]
        session.ai_used = bool(row["ai_used"])
        session.evaluation = json.loads(row["evaluation"]) if row["evaluation"] else None
        with _lock:
            _sessions[session.id] = session
