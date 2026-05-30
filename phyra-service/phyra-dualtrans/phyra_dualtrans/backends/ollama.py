"""Ollama backend — re-exported from the shared phyra-model-service.

Real definitions live in `phyra_model_service.backends.ollama`. This
facade keeps `from ..backends.ollama import list_models, normalize_host,
OllamaClient` working unchanged (used by preflight + runtime status).
"""

from __future__ import annotations

from phyra_model_service.backends.ollama import (  # noqa: F401
    DEFAULT_OLLAMA_HOST,
    OllamaClient,
    list_models,
    normalize_host,
)

__all__ = [
    "DEFAULT_OLLAMA_HOST",
    "OllamaClient",
    "list_models",
    "normalize_host",
]
