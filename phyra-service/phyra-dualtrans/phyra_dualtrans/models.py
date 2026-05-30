"""Shared pydantic request/response models for the web layer."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class BackendInput(BaseModel):
    """Backend selection as sent by the UI (merged with config/env later).

    `api_key`: a real key, or "" / "***" meaning "keep the saved/env key".
    """

    kind: Literal["openai", "ollama", "claude_cli"]
    model: str = ""
    base_url: str | None = None
    api_key: str | None = None
    extra_headers: dict[str, str] = Field(default_factory=dict)
    think: bool = False  # ollama: enable model thinking (default off)


class TranslateParams(BaseModel):
    lang_in: str = "en"
    lang_out: str = "zh-TW"
    qps: int = Field(2, ge=1, le=20)
    compat: bool = False
    compress: Literal["off", "lossless", "lossy"] = "lossy"
    dpi: int = Field(150, ge=36, le=600)
    preset: Literal["screen", "ebook", "printer"] = "ebook"
    mono: bool = False
    distill: bool = False  # one-shot context-distillation pre-pass


JobStatus = Literal["queued", "running", "succeeded", "failed", "canceled"]


class JobView(BaseModel):
    """Public (secret-free) view of a job."""

    id: str
    status: JobStatus
    stem: str
    params: dict
    backend: dict  # redacted (api_key → ***)
    progress: dict
    outputs: dict
    error: str | None = None
    compress_stats: dict | None = None
    archived: bool = False  # saved into the sibling phyra-archbase collection
    created_at: float
    started_at: float | None = None
    finished_at: float | None = None
