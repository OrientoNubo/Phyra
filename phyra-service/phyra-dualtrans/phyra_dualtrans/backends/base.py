"""Backend abstraction — re-exported from the shared phyra-model-service.

Real definitions live in `phyra_model_service.backends.base`. This facade
keeps `from ..backends.base import BackendConfig, ...` working unchanged.
"""

from __future__ import annotations

from phyra_model_service.backends.base import (  # noqa: F401
    DEFAULT_TIMEOUT_SEC,
    BackendConfig,
    BackendError,
    BackendUnavailable,
    HardCallError,
    LLMClient,
    RateLimitSignal,
)

__all__ = [
    "DEFAULT_TIMEOUT_SEC",
    "BackendConfig",
    "BackendError",
    "BackendUnavailable",
    "HardCallError",
    "LLMClient",
    "RateLimitSignal",
]
