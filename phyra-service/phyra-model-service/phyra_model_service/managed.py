"""
Managed Ollama lifecycle.

A Phyra service can own Ollama: starting the service starts a
correctly-configured Ollama; stopping the service stops it. We run a
DEDICATED instance on its own loopback port (default 11500) so it never
collides with — or kills — a system Ollama (:11434) or the user's own
manual instance (:18763). If something is already serving Ollama on our
port we reuse it (and never kill it on shutdown).

This is the single, shared spawn/supervise/teardown implementation used by
both the standalone phyra-model-service and any sibling service
(phyra-dualtrans) that wants a managed Ollama when run on its own. When
the model-service is already up on the shared port, the sibling's
ManagedOllama detects it via the reuse path and never double-spawns.

Model choice (delegated to us): a translation-tuned variant of
`qwen3:14b` ("phyra-trans"). On a 32 GB GPU a 14B Q4 (~9 GB) leaves
ample headroom for real OLLAMA_NUM_PARALLEL concurrency and is ~2–3×
faster than 32B while keeping zh-TW academic quality. The Modelfile
mirrors the user's qwen3-32b-trans recipe (num_ctx 8192 — per-paragraph
translation never needs more; temp 0.3 / top_p 0.9 / repeat_penalty
1.05). Override the base with PHYRA_MODEL_OLLAMA_BASE_MODEL.

Everything is best-effort: any failure here is logged and the caller
still starts. This module only manages a subprocess; it never imports a
translation engine, so any isolation boundary upstream is untouched.
"""

from __future__ import annotations

import logging
import os
import shutil
import signal
import socket
import subprocess
import tempfile
import threading
import time
from pathlib import Path

import httpx

from .settings import DEFAULT_KEEP_ALIVE, ModelSettings

log = logging.getLogger("phyra-model-service.ollama")

_MODELFILE = (
    "FROM {base}\n"
    "PARAMETER num_ctx 8192\n"
    "PARAMETER temperature 0.3\n"
    "PARAMETER top_p 0.9\n"
    "PARAMETER repeat_penalty 1.05\n"
)


def _port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def _is_ollama(base_url: str, timeout: float = 1.5) -> bool:
    try:
        r = httpx.get(base_url + "/api/tags", timeout=timeout)
        return r.status_code == 200 and "models" in r.json()
    except Exception:  # noqa: BLE001
        return False


class ManagedOllama:
    """Spawns + supervises a dedicated Ollama, ensures the tuned model
    exists, and tears it down with the owning service."""

    def __init__(
        self,
        *,
        port: int,
        model: str,
        base_model: str,
        num_parallel: int,
        models_dir: str | None = None,
        keep_alive: str = DEFAULT_KEEP_ALIVE,
    ) -> None:
        self.port = port
        self.model = model
        self.base_model = base_model
        self.num_parallel = max(1, num_parallel)
        self.models_dir = models_dir
        self.keep_alive = keep_alive
        self.host = f"http://127.0.0.1:{port}"
        self._proc: subprocess.Popen | None = None
        self._owned = False           # did WE spawn it? (only then kill)
        self._ready_evt = threading.Event()
        self.model_status = "pending"  # pending|preparing|ready|error|off
        self._bin = shutil.which("ollama")

    @classmethod
    def from_settings(cls, settings: ModelSettings | None = None) -> "ManagedOllama":
        """Build from the unified ModelSettings (the canonical defaults +
        env). The single constructor both the model-service and a
        standalone sibling should use."""
        s = settings or ModelSettings()
        return cls(
            port=s.ollama_port,
            model=s.model,
            base_model=s.base_model,
            num_parallel=s.num_parallel,
            models_dir=s.models_dir,
            keep_alive=s.keep_alive,
        )

    # ---- lifecycle ----------------------------------------------------

    def start(self) -> None:
        """Spawn (or reuse) Ollama, wait for the HTTP API, then ensure
        the model in a background thread (a first-time pull is GBs — must
        not block readiness). Never raises."""
        try:
            if _is_ollama(self.host):
                log.info("reusing the Ollama already serving on %s "
                         "(not managed by us)", self.host)
            elif _port_open("127.0.0.1", self.port):
                log.warning("port %d busy but not Ollama; managed Ollama "
                            "disabled (set PHYRA_MODEL_OLLAMA_PORT)",
                            self.port)
                self.model_status = "error"
                return
            elif not self._bin:
                log.warning("`ollama` binary not found on PATH; managed "
                            "Ollama disabled (install Ollama, or set "
                            "PHYRA_MODEL_MANAGE_OLLAMA=0 and point the "
                            "ollama backend Base URL at your own server)")
                self.model_status = "error"
                return
            else:
                self._spawn()

            if not self._wait_ready(timeout=40):
                log.error("Ollama did not become ready on %s", self.host)
                self.model_status = "error"
                return
            self._ready_evt.set()
            threading.Thread(
                target=self._ensure_model_safe, daemon=True,
                name="ollama-ensure-model",
            ).start()
        except Exception as e:  # noqa: BLE001 — caller must still start
            log.exception("managed Ollama start failed: %s", e)
            self.model_status = "error"

    def _spawn(self) -> None:
        env = dict(os.environ)
        env.update(
            OLLAMA_HOST=f"127.0.0.1:{self.port}",
            # Server-wide default idle-unload window. Per-request chat
            # calls also send keep_alive (resets while a job streams), so
            # the VRAM frees ~this long after translation goes idle.
            OLLAMA_KEEP_ALIVE=self.keep_alive,
            OLLAMA_NUM_PARALLEL=str(self.num_parallel),
        )
        if self.models_dir:
            env["OLLAMA_MODELS"] = self.models_dir
        log.info("starting managed Ollama: %s serve  (port=%d "
                 "NUM_PARALLEL=%d)", self._bin, self.port,
                 self.num_parallel)
        # own session/process-group so stop() can kill the whole tree
        self._proc = subprocess.Popen(
            [self._bin, "serve"],
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        self._owned = True

    def _wait_ready(self, timeout: float) -> bool:
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self._owned and self._proc and self._proc.poll() is not None:
                log.error("managed Ollama exited rc=%s during startup",
                          self._proc.returncode)
                return False
            if _is_ollama(self.host):
                log.info("Ollama ready on %s", self.host)
                return True
            time.sleep(0.5)
        return False

    def stop(self) -> None:
        """Terminate the managed Ollama (only if we spawned it) so
        closing the owning service closes Ollama. Never raises."""
        if not (self._owned and self._proc):
            return
        log.info("stopping managed Ollama (pid=%s)", self._proc.pid)
        try:
            os.killpg(os.getpgid(self._proc.pid), signal.SIGTERM)
        except (ProcessLookupError, PermissionError):
            try:
                self._proc.terminate()
            except Exception:  # noqa: BLE001
                pass
        try:
            self._proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(os.getpgid(self._proc.pid), signal.SIGKILL)
            except Exception:  # noqa: BLE001
                self._proc.kill()
        self._proc = None

    # ---- model provisioning ------------------------------------------

    def _tags(self) -> list[str]:
        try:
            r = httpx.get(self.host + "/api/tags", timeout=5)
            return [m.get("name", "") for m in r.json().get("models", [])]
        except Exception:  # noqa: BLE001
            return []

    @staticmethod
    def _has(names: list[str], want: str) -> bool:
        want_b = want.split(":")[0]
        return any(n == want or n.split(":")[0] == want_b
                   or n == f"{want}:latest" for n in names)

    def _ollama(self, *args: str, timeout: int) -> bool:
        env = dict(os.environ, OLLAMA_HOST=f"127.0.0.1:{self.port}")
        try:
            p = subprocess.run(
                [self._bin, *args], env=env, timeout=timeout,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True,
            )
            if p.returncode != 0:
                log.warning("`ollama %s` rc=%d: %s", " ".join(args),
                            p.returncode, (p.stdout or "")[-300:])
            return p.returncode == 0
        except (subprocess.TimeoutExpired, OSError) as e:
            log.warning("`ollama %s` failed: %s", " ".join(args), e)
            return False

    def _ensure_model_safe(self) -> None:
        try:
            self._ensure_model()
        except Exception as e:  # noqa: BLE001
            log.exception("ensure_model failed: %s", e)
            self.model_status = "error"

    def _ensure_model(self) -> None:
        names = self._tags()
        if self._has(names, self.model):
            log.info("model %s already present", self.model)
            self.model_status = "ready"
            return
        if not self._bin:
            self.model_status = "error"
            return
        self.model_status = "preparing"
        if not self._has(names, self.base_model):
            log.info("pulling base model %s (one-time, may be several "
                     "GB)…", self.base_model)
            if not self._ollama("pull", self.base_model, timeout=3600):
                log.error("could not pull %s; managed model unavailable",
                          self.base_model)
                self.model_status = "error"
                return
        with tempfile.NamedTemporaryFile(
            "w", suffix=".Modelfile", delete=False, encoding="utf-8"
        ) as fh:
            fh.write(_MODELFILE.format(base=self.base_model))
            mf = fh.name
        try:
            log.info("creating tuned model %s from %s", self.model,
                     self.base_model)
            ok = self._ollama("create", self.model, "-f", mf, timeout=600)
        finally:
            Path(mf).unlink(missing_ok=True)
        if ok and self._has(self._tags(), self.model):
            log.info("managed model %s ready on %s", self.model,
                     self.host)
            self.model_status = "ready"
        else:
            self.model_status = "error"

    # ---- status ------------------------------------------------------

    def status(self) -> dict:
        return {
            "host": self.host,
            "model": self.model,
            "owned": self._owned,
            "model_status": self.model_status,
            "ready": self._ready_evt.is_set(),
        }
