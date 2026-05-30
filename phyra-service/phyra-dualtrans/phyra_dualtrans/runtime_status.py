"""Runtime / hardware status — re-exported from phyra-model-service.

Real implementation lives in `phyra_model_service.runtime`. This facade
keeps `from ..runtime_status import collect` (routes_meta) and the
`phyra_dualtrans.runtime_status` test imports working unchanged.
"""

from __future__ import annotations

from phyra_model_service.runtime import (  # noqa: F401
    _int,
    _placement,
    _worst_placement,
    collect,
    probe_nvidia,
    probe_ollama_ps,
)

__all__ = [
    "collect",
    "probe_nvidia",
    "probe_ollama_ps",
    "_placement",
    "_worst_placement",
]
