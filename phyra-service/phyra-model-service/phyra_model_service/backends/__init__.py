"""Backend registry."""

from __future__ import annotations

from .base import (
    BackendConfig,
    BackendError,
    BackendUnavailable,
    HardCallError,
    LLMClient,
    RateLimitSignal,
)
from .claude_cli import ClaudeCliClient
from .ollama import OllamaClient
from .ollama import list_models as list_ollama_models
from .openai_compatible import OpenAICompatibleClient

BACKEND_REGISTRY: dict[str, type] = {
    "openai": OpenAICompatibleClient,
    "ollama": OllamaClient,
    "claude_cli": ClaudeCliClient,
}

# Static description consumed by GET /api/backends and the UI.
BACKEND_INFO = [
    {
        "name": "openai",
        "kind": "openai",
        "label": "OpenAI-compatible",
        "needs": ["base_url", "api_key", "model"],
        "default_model": "",
        "hint": "OpenAI, DeepSeek, Together, Groq, OpenRouter, vLLM, LM Studio…",
    },
    {
        "name": "ollama",
        "kind": "ollama",
        "label": "Ollama (local)",
        "needs": ["base_url (optional)", "model"],
        "default_model": "",
        "hint": "Local models; click ↻ to list installed models.",
    },
    {
        "name": "claude_cli",
        "kind": "claude_cli",
        "label": "Claude CLI (headless)",
        "needs": ["claude CLI on host (no API key)"],
        "default_model": "sonnet",
        "hint": "Uses your existing Claude Code auth. Host-only.",
    },
]


def get_backend(cfg: BackendConfig) -> LLMClient:
    """Construct the LLMClient for `cfg`. May raise BackendUnavailable."""
    try:
        cls = BACKEND_REGISTRY[cfg.kind]
    except KeyError as e:
        raise BackendError(f"unknown backend kind: {cfg.kind!r}") from e
    return cls(cfg)


__all__ = [
    "BACKEND_REGISTRY",
    "BACKEND_INFO",
    "BackendConfig",
    "BackendError",
    "BackendUnavailable",
    "HardCallError",
    "LLMClient",
    "RateLimitSignal",
    "get_backend",
    "list_ollama_models",
]
