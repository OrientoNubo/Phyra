"""
phyra-model-service — shared model layer for the Phyra service suite.

Two things live here, both reusable by any Phyra service or future plugin:

  • a Python library: managed-Ollama lifecycle (`ManagedOllama`), GPU/VRAM
    runtime status (`runtime.collect`), a pluggable LLM backend abstraction
    (`backends`), and the unified `ModelSettings` defaults; and
  • a standalone control-plane service (`service.app`) that keeps the
    managed Ollama up and answers status queries on its own HTTP port.

A sibling service (e.g. phyra-dualtrans) imports the library directly and
talks to Ollama in-process on the hot path — no extra HTTP hop — while the
control-plane gives every service one shared, consistently-configured
Ollama (one idle-unload window, one model, one set of defaults).
"""

from __future__ import annotations

__version__ = "0.1.0"

from .backends import BackendConfig, get_backend  # noqa: E402
from .managed import ManagedOllama  # noqa: E402
from .settings import ModelSettings  # noqa: E402

__all__ = [
    "__version__",
    "BackendConfig",
    "get_backend",
    "ManagedOllama",
    "ModelSettings",
]
