"""ScamSense training API — Phase 2 (SS-101 only).

Run from this directory:
    uvicorn main:app --reload --port 8000
"""

import json
import os
import time
import uuid

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from ai_provider import ai_chat, ai_config, sanitize_ai_text
from evaluation import build_evaluation
from models import (
    DecisionEvent,
    EndResponse,
    Evaluation,
    HealthResponse,
    MessageRequest,
    MessageResponse,
    ReportSummary,
    Scores,
    StartRequest,
    StartResponse,
    StageInfo,
    TranscriptMessage,
)
import db
import store
from scenarios import get_scenario, primary_ids
from store import get, create

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def _load_env_file() -> None:
    if not os.path.exists(ENV_PATH):
        return
    with open(ENV_PATH, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

db.init_db()
store.hydrate()

app = FastAPI(title="ScamSense Training API", version="0.3.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:4173",
        "http://127.0.0.1:4173",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _now() -> int:
    return int(time.time())


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(
        status="ok",
        ai_configured=ai_config() is not None,
        scenario=", ".join(primary_ids()),
    )


@app.post("/api/simulations", response_model=StartResponse)
def start_simulation(req: StartRequest):
    scenario = get_scenario(req.scenario_id.strip().lower())
    if scenario is None:
        raise HTTPException(404, "Unknown scenario.")

    session = create(uuid.uuid4().hex[:12], scenario.id, scenario.title)
    opening = TranscriptMessage(
        role="caller",
        text=scenario.opening(),
        ts=_now(),
        stage=scenario.stage_key(0),
    )
    session.transcript.append(opening.model_dump())

    return StartResponse(
        simulation_id=session.id,
        scenario_id=scenario.id,
        scenario_title=scenario.title,
        ai_configured=ai_config() is not None,
        stage=StageInfo(**scenario.stage_info(0)),
        transcript=[opening],
        disclaimer=scenario.disclaimer(),
    )


@app.post("/api/simulations/{sid}/messages", response_model=MessageResponse)
def send_message(sid: str, req: MessageRequest):
    session = get(sid)
    if session is None:
        raise HTTPException(404, "Simulation not found.")
    if session.ended:
        raise HTTPException(409, "This simulation has already ended.")

    text = req.text.strip()
    if not text:
        raise HTTPException(422, "Message text is required.")

    scenario = get_scenario(session.scenario_id)
    session.turn += 1

    result = scenario.process(text, session.stage_index, session.turn, session.scenario_state)
    session.stage_index = result["stage_index"]
    stage_key = scenario.stage_key(session.stage_index)

    session.transcript.append(
        {"role": "user", "text": text, "ts": _now(), "stage": stage_key, "system_note": False, "warning": False}
    )

    ai_text = None
    cfg = ai_config()
    if cfg is not None and not session.ai_down:
        # The current user message was just appended to the transcript and is sent as the
        # final turn by ai_chat(); exclude it here so it is not duplicated.
        history = [
            {"role": "assistant" if m["role"] == "caller" else "user", "content": m["text"]}
            for m in session.transcript[:-1]
            if m["role"] in ("caller", "user")
        ]
        ai_text = ai_chat(
            cfg,
            scenario.ai_system_prompt(session.stage_index, session.transcript, text, result["dominant"]),
            text,
            history,
        )
        if ai_text is None:
            session.ai_failures += 1
            if session.ai_failures >= 2:
                session.ai_down = True
        else:
            session.ai_used = True

    line = sanitize_ai_text(ai_text) if ai_text else result["fallback"]
    reply = TranscriptMessage(role="caller", text=line, ts=_now(), stage=stage_key)
    session.transcript.append(reply.model_dump())

    system_notes = []
    for note in result["notes"]:
        note_msg = TranscriptMessage(
            role="system",
            text=note,
            ts=_now(),
            stage=stage_key,
            system_note=True,
            warning=note.startswith("TRAINING"),
        )
        session.transcript.append(note_msg.model_dump())
        system_notes.append(note_msg)

    events = [DecisionEvent(**e) for e in result["events"]]
    session.events.extend(result["events"])
    db.save_session(session)

    return MessageResponse(
        reply=reply,
        system_notes=system_notes,
        events=events,
        stage=StageInfo(**scenario.stage_info(session.stage_index)),
        turn=session.turn,
        ai_mode=ai_text is not None,
        ended=result["ended"],
    )


@app.post("/api/simulations/{sid}/end", response_model=EndResponse)
def end_simulation(sid: str):
    session = get(sid)
    if session is None:
        raise HTTPException(404, "Simulation not found.")
    if not session.ended:
        session.ended = True
        session.ended_at = _now()
        scenario = get_scenario(session.scenario_id)
        session.events.append(
            {
                "type": "interaction_stopped",
                "label": "Stopped the interaction",
                "pattern": None,
                "turn": session.turn,
                "excerpt": "",
                "stage": scenario.stage_key(session.stage_index) if scenario else "",
            }
        )
        session.evaluation = build_evaluation(session, scenario)
        db.save_session(session)

    return EndResponse(
        simulation_id=session.id,
        transcript=[TranscriptMessage(**m) for m in session.transcript],
        evaluation=Evaluation(**session.evaluation),
    )


@app.get("/api/reports", response_model=list[ReportSummary])
def list_reports():
    """Completed simulations, newest first. Survives backend restarts."""
    out: list[ReportSummary] = []
    for row in db.list_completed():
        evaluation = json.loads(row["evaluation"]) if row["evaluation"] else None
        if not evaluation:
            continue
        out.append(
            ReportSummary(
                simulation_id=row["id"],
                scenario_id=row["scenario_id"],
                ended_at=row["ended_at"],
                turn=row["turn"],
                overall=evaluation["scores"]["overall"],
                rating=evaluation["rating"],
            )
        )
    return out


@app.get("/api/simulations/{sid}/evaluation", response_model=Evaluation)
def fetch_evaluation(sid: str):
    session = get(sid)
    if session is None:
        raise HTTPException(404, "Simulation not found.")
    if session.evaluation is None:
        raise HTTPException(409, "Simulation has not been ended yet.")
    return Evaluation(**session.evaluation)


@app.get("/api/simulations/{sid}")
def fetch_transcript(sid: str):
    session = get(sid)
    if session is None:
        raise HTTPException(404, "Simulation not found.")
    return {
        "simulation_id": session.id,
        "ended": session.ended,
        "turn": session.turn,
        "stage": StageInfo(**get_scenario(session.scenario_id).stage_info(session.stage_index)),
        "transcript": [TranscriptMessage(**m) for m in session.transcript],
        "evaluation": Evaluation(**session.evaluation) if session.evaluation else None,
    }
