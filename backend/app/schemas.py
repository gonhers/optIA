from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .generator import (
    DEFAULT_CANDIDATE_COUNT,
    MAX_CANDIDATE_COUNT,
    MIN_CANDIDATE_COUNT,
    normalize_candidate_count,
)
from .translator import (
    LanguageCode,
    SUPPORTED_LANGUAGE_CODES_TEXT,
    validate_target_language,
)


class OptimizeRequest(BaseModel):
    prompt: str = Field(..., min_length=1, description="Prompt to optimize")
    target_language: LanguageCode | None = Field(
        default=None,
        description=(
            "Optional language code for translating the best response. "
            f"Supported codes: {SUPPORTED_LANGUAGE_CODES_TEXT}."
        ),
    )
    candidate_count: int = Field(
        default=DEFAULT_CANDIDATE_COUNT,
        description=(
            "Number of simulated candidates to generate. "
            f"Allowed range: {MIN_CANDIDATE_COUNT}-{MAX_CANDIDATE_COUNT}."
        ),
    )

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        prompt = value.strip()
        if not prompt:
            raise ValueError("El prompt no puede estar vacio.")
        return prompt

    @field_validator("target_language", mode="before")
    @classmethod
    def normalize_target_language(cls, value: object) -> LanguageCode | None:
        return validate_target_language(value)

    @field_validator("candidate_count", mode="before")
    @classmethod
    def validate_candidate_count(cls, value: object) -> int:
        return normalize_candidate_count(value)


class CandidateResponse(BaseModel):
    text: str
    score: float


class OptimizeResponse(BaseModel):
    best_response: str
    candidates: list[CandidateResponse]


class AppConfigResponse(BaseModel):
    mode: str
    live_ready: bool


DashboardAudience = Literal["internal", "client"]
DashboardTone = Literal["teal", "cyan", "sky", "amber", "coral"]


class DashboardStat(BaseModel):
    label: str
    value: str
    delta: str
    meta: str
    tone: DashboardTone


class DashboardSpotlight(BaseModel):
    eyebrow: str
    title: str
    description: str
    bullets: list[str]


class DashboardBoardItem(BaseModel):
    title: str
    meta: str
    status: str
    tone: DashboardTone


class DashboardBoard(BaseModel):
    eyebrow: str
    title: str
    items: list[DashboardBoardItem]


class DashboardRecord(BaseModel):
    name: str
    tier: str
    owner: str
    usage: str
    status: str


class DashboardRecords(BaseModel):
    eyebrow: str
    title: str
    rows: list[DashboardRecord]


class DashboardActivityItem(BaseModel):
    title: str
    meta: str


class DashboardActivity(BaseModel):
    eyebrow: str
    title: str
    items: list[DashboardActivityItem]


class DashboardView(BaseModel):
    badge: str
    eyebrow: str
    title: str
    description: str
    stats: list[DashboardStat]
    spotlight: DashboardSpotlight
    board: DashboardBoard
    records: DashboardRecords
    activity: DashboardActivity


class DashboardResponse(BaseModel):
    internal: DashboardView
    client: DashboardView
