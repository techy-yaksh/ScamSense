"""Pydantic schemas for the ScamSense training API."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

Role = Literal["caller", "user", "system"]


class TranscriptMessage(BaseModel):
    role: Role
    text: str
    ts: int
    stage: str
    system_note: bool = False
    warning: bool = False


class StageInfo(BaseModel):
    key: str
    label: str
    index: int
    total: int
    pct: int


class DecisionEvent(BaseModel):
    type: str
    label: str
    pattern: Optional[str] = None
    turn: int
    excerpt: str = ""
    stage: str = ""


class StartRequest(BaseModel):
    scenario_id: str = "ss101"


class StartResponse(BaseModel):
    simulation_id: str
    scenario_id: str
    scenario_title: str
    ai_configured: bool
    stage: StageInfo
    transcript: list[TranscriptMessage]
    disclaimer: str


class MessageRequest(BaseModel):
    text: str = Field(min_length=1, max_length=600)


class MessageResponse(BaseModel):
    reply: TranscriptMessage
    system_notes: list[TranscriptMessage]
    events: list[DecisionEvent]
    stage: StageInfo
    turn: int
    ai_mode: bool
    ended: bool


class Scores(BaseModel):
    overall: int
    caution: int
    awareness: int


class CategoryScore(BaseModel):
    score: int
    note: str


class SignItem(BaseModel):
    stage: str
    technique: str
    description: str
    turn: int = 0
    quote: str = ""


class TechniqueItem(BaseModel):
    stage: str
    name: str
    description: str


class ExampleItem(BaseModel):
    turn: int
    kind: str
    label: str
    quote: str
    stage: str = ""


class Evaluation(BaseModel):
    scenario_id: str
    ended_at: int
    turns: int
    duration_seconds: int
    final_stage: str
    decision_events: list[DecisionEvent]
    counts: dict[str, int]
    scores: Scores
    rating: str
    summary: str
    ai_mode: bool
    fictional: bool = True
    categories: dict[str, CategoryScore] = {}
    signs_recognized: list[SignItem] = []
    signs_questioned: list[SignItem] = []
    signs_missed: list[SignItem] = []
    techniques: list[TechniqueItem] = []
    examples: list[ExampleItem] = []
    recommendations: list[str] = []
    assessment: str = ""


class ReportSummary(BaseModel):
    simulation_id: str
    scenario_id: str
    ended_at: int
    turn: int
    overall: int
    rating: str


class EndResponse(BaseModel):
    simulation_id: str
    transcript: list[TranscriptMessage]
    evaluation: Evaluation


class HealthResponse(BaseModel):
    status: str
    ai_configured: bool
    scenario: str
