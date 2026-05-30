"""Backend registry — re-exported from the shared phyra-model-service.

The real backend implementations moved to `phyra_model_service.backends`
(see phyra-service/phyra-model-service). This module stays as a thin
facade so dualtrans's own imports (`from ..backends import get_backend`,
etc.) and the translation subprocess keep working unchanged, talking to
the model in-process with no extra HTTP hop.
"""

from __future__ import annotations

from phyra_model_service.backends import (  # noqa: F401
    BACKEND_INFO,
    BACKEND_REGISTRY,
    BackendConfig,
    BackendError,
    BackendUnavailable,
    HardCallError,
    LLMClient,
    RateLimitSignal,
    get_backend,
    list_ollama_models,
)

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
