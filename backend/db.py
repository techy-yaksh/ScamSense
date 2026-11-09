"""Lightweight SQLite persistence for simulations (stdlib only)."""

import json
import os
import sqlite3
import threading

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scamsense.db")
_lock = threading.Lock()


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _lock, _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS simulations (
                id TEXT PRIMARY KEY,
                scenario_id TEXT NOT NULL,
                started_at INTEGER NOT NULL,
                ended_at INTEGER,
                transcript TEXT NOT NULL DEFAULT '[]',
                events TEXT NOT NULL DEFAULT '[]',
                scenario_state TEXT NOT NULL DEFAULT '{}',
                stage_index INTEGER NOT NULL DEFAULT 0,
                turn INTEGER NOT NULL DEFAULT 0,
                ai_used INTEGER NOT NULL DEFAULT 0,
                evaluation TEXT
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_simulations_ended ON simulations(ended_at) WHERE ended_at IS NOT NULL"
        )


def save_session(session) -> None:
    with _lock, _connect() as conn:
        conn.execute(
            """
            INSERT INTO simulations (
                id, scenario_id, started_at, ended_at, transcript, events,
                scenario_state, stage_index, turn, ai_used, evaluation
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?)
            ON CONFLICT(id) DO UPDATE SET
                ended_at = excluded.ended_at,
                transcript = excluded.transcript,
                events = excluded.events,
                scenario_state = excluded.scenario_state,
                stage_index = excluded.stage_index,
                turn = excluded.turn,
                ai_used = excluded.ai_used,
                evaluation = excluded.evaluation
            """,
            (
                session.id,
                session.scenario_id,
                session.started_at,
                session.ended_at,
                json.dumps(session.transcript),
                json.dumps(session.events),
                json.dumps(session.scenario_state),
                session.stage_index,
                session.turn,
                int(session.ai_used),
                json.dumps(session.evaluation) if session.evaluation else None,
            ),
        )


def get_row(sid: str) -> dict | None:
    with _lock, _connect() as conn:
        row = conn.execute("SELECT * FROM simulations WHERE id = ?", (sid,)).fetchone()
    return dict(row) if row else None


def load_all() -> list[dict]:
    with _lock, _connect() as conn:
        rows = conn.execute("SELECT * FROM simulations").fetchall()
    return [dict(r) for r in rows]


def list_completed() -> list[dict]:
    with _lock, _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM simulations WHERE ended_at IS NOT NULL ORDER BY ended_at DESC"
        ).fetchall()
    return [dict(r) for r in rows]
