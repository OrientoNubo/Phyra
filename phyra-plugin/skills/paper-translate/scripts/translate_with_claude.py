"""
BabelDOC + Claude Code headless translator (BYO BaseTranslator).

For each chunk BabelDOC asks to translate, this spawns `claude -p` and uses
the user's existing CC auth — no API key needed.

Default model is **Sonnet** (passed as `--model sonnet` to the claude CLI).
Translation is a many-call workload (one `claude -p` per BabelDOC chunk;
~hundreds per paper) so the speed and cost profile of Sonnet matters more
than the deeper reasoning of Opus. Override with `--model` if needed.

Lives under `skills/paper-translate/` (v0.9.0); `_retry.py` is sourced from
the sibling `paper-read` skill so retry semantics stay in lockstep across
all paper-* commands.

Usage (run via uv with babeldoc + pymupdf):
  uv run --python 3.12 --with babeldoc==0.5.24 --with pymupdf python \\
      translate_with_claude.py <input.pdf> <output_dir> \\
      [--lang-out zh-TW] [--lang-in en] [--qps 2] [--compat] \\
      [--model sonnet]
"""

import argparse
import asyncio
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

from babeldoc.format.pdf.high_level import async_translate, init
from babeldoc.format.pdf.translation_config import (
    TranslationConfig,
    WatermarkOutputMode,
)
from babeldoc.translator.translator import BaseTranslator

# Rate-limit detector lives in the sibling paper-read skill (single source
# of truth across all paper-* commands).
_PHYRA_PR_SCRIPTS = (
    Path(os.environ["CLAUDE_PLUGIN_ROOT"]) / "skills/paper-read/scripts"
    if os.environ.get("CLAUDE_PLUGIN_ROOT")
    else Path(__file__).resolve().parents[2] / "paper-read/scripts"
)
sys.path.insert(0, str(_PHYRA_PR_SCRIPTS))
from _retry import is_rate_limit_response as _is_rate_limit  # noqa: E402

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("phyra-translate")

CALL_TIMEOUT_SEC = 180


# Per-language system prompts. The default zh-TW prompt enforces Taiwan
# terminology. Other languages get a generic "professional translator" prompt;
# customize via `--system-prompt-file` (future) if needed.
SYSTEM_PROMPTS = {
    "zh-TW": (
        "You are a professional Taiwan-localized scientific translator. "
        "Translate the user's English input to Traditional Chinese using "
        "Taiwan terminology (軟體 not 软件, 演算法 not 算法, 函式 not 函数, "
        "程式 not 程序, 介面 not 接口, 預設 not 默认). "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
    "zh-HK": (
        "You are a professional Hong Kong-localized scientific translator. "
        "Translate to Traditional Chinese (Hong Kong conventions). "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
    "zh-CN": (
        "You are a professional scientific translator. "
        "Translate the user's English input to Simplified Chinese using "
        "mainland China terminology. "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
    "ja": (
        "You are a professional Japanese scientific translator. "
        "Translate the user's English input to natural Japanese, using "
        "established academic terminology where it exists. "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
    "ko": (
        "You are a professional Korean scientific translator. "
        "Translate the user's English input to natural Korean. "
        "Preserve every placeholder token verbatim, including {v0} {v1} ... "
        "and <style id='0'>...</style> tags. "
        "Output ONLY the translation. No preamble, no notes, no quotes."
    ),
}


def system_prompt_for(lang_out: str) -> str:
    return SYSTEM_PROMPTS.get(
        lang_out,
        (
            "You are a professional scientific translator. "
            f"Translate the user's input to {lang_out}, output the translation only. "
            "Preserve every placeholder token verbatim, including {v0} {v1} ... "
            "and <style id='0'>...</style> tags. "
            "No preamble, no notes, no quotes."
        ),
    )


def _clean(s: str) -> str:
    s = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", s)  # strip ANSI
    return s.strip()


def claude_bin() -> str:
    p = shutil.which("claude")
    if not p:
        raise RuntimeError(
            "`claude` not found in PATH. Run preflight.py first."
        )
    return p


def _force_exit(code: int) -> None:
    sys.stdout.flush()
    sys.stderr.flush()
    os._exit(code)


class ClaudeHeadlessTranslator(BaseTranslator):
    name = "phyra-claude"  # ≤20 chars

    def __init__(self, lang_in="en", lang_out="zh-TW", ignore_cache=False,
                 cli_model="sonnet"):
        super().__init__(lang_in, lang_out, ignore_cache)
        # `self.model` is BabelDOC's logical model identifier (used in caches /
        # logs). `self._cli_model` is what we actually pass to `claude --model`.
        self.model = f"claude-headless-{cli_model}"
        self._cli_model = cli_model
        self._n = 0
        self._claude = claude_bin()
        self._sysprompt = system_prompt_for(lang_out)

    def _spawn_once(self, text: str, i: int) -> str | None:
        """One translation attempt. Returns None on rate-limit (caller retries),
        text on hard failure (caller falls back to source), translated string
        on success."""
        t0 = time.monotonic()
        prompt = f"Translate to {self.lang_out}. Output the translation only.\n\nINPUT:\n{text}"
        try:
            res = subprocess.run(
                [self._claude, "-p",
                 "--model", self._cli_model,
                 "--append-system-prompt", self._sysprompt],
                input=prompt,
                capture_output=True, text=True, timeout=CALL_TIMEOUT_SEC,
            )
        except subprocess.TimeoutExpired:
            log.warning("[chunk %d] timeout, returning source", i)
            return None  # treat as transient — caller may decide
        dt = time.monotonic() - t0
        out = _clean(res.stdout)
        combined = (res.stderr or "") + (res.stdout or "")
        if _is_rate_limit(combined):
            return "__RATE_LIMIT__"
        if res.returncode != 0 or not out:
            log.warning(
                "[chunk %d] claude rc=%s out_empty=%s; falling back to source",
                i, res.returncode, not out,
            )
            return None
        log.info("[chunk %d] %.1fs %d→%d chars", i, dt, len(text), len(out))
        return out

    def _spawn(self, text: str) -> str:
        self._n += 1
        i = self._n
        # 30 min × 50 retries on rate-limit; final fallback = source text.
        wait_seconds = 30 * 60
        max_attempts = 50
        for attempt in range(1, max_attempts + 1):
            result = self._spawn_once(text, i)
            if result == "__RATE_LIMIT__":
                log.warning(
                    "[chunk %d] rate-limit, attempt %d/%d, sleeping %ds",
                    i, attempt, max_attempts, wait_seconds,
                )
                if attempt >= max_attempts:
                    log.error("[chunk %d] rate-limit retries exhausted; "
                              "falling back to source", i)
                    return text
                time.sleep(wait_seconds)
                continue
            if result is None:
                return text  # hard failure: source-text fallback
            return result
        return text

    def do_translate(self, text, rate_limit_params=None):
        return self._spawn(text)

    def do_llm_translate(self, text, rate_limit_params=None):
        if text is None:
            return None
        return self._spawn(text)

    # Match OpenAITranslator's (string, regex) tuple shape
    def get_formular_placeholder(self, placeholder_id):
        return (
            "{v" + str(placeholder_id) + "}",
            r"\{\s*v\s*" + str(placeholder_id) + r"\s*\}",
        )

    def get_rich_text_left_placeholder(self, placeholder_id):
        return (
            f"<style id='{placeholder_id}'>",
            r"<\s*style\s*id\s*=\s*'\s*" + str(placeholder_id) + r"\s*'\s*>",
        )

    def get_rich_text_right_placeholder(self, placeholder_id):
        return ("</style>", r"<\s*/\s*style\s*>")


async def run(args: argparse.Namespace) -> None:
    init()
    cfg = TranslationConfig(
        translator=ClaudeHeadlessTranslator(
            lang_in=args.lang_in,
            lang_out=args.lang_out,
            cli_model=args.model,
        ),
        input_file=str(Path(args.input_pdf).resolve()),
        lang_in=args.lang_in,
        lang_out=args.lang_out,
        doc_layout_model=None,
        output_dir=str(Path(args.output_dir).resolve()),
        no_dual=False,
        no_mono=True,                       # paper-translate emits dual; mono is built later by build_dual.py
        watermark_output_mode=WatermarkOutputMode.NoWatermark,
        qps=args.qps,
        pool_max_workers=args.qps,
        skip_clean=False,
        auto_extract_glossary=False,
        enhance_compatibility=args.compat,
    )
    log.info(
        "translate %s → %s (lang_out=%s, qps=%d, compat=%s, model=%s)",
        args.input_pdf, args.output_dir, args.lang_out, args.qps, args.compat,
        args.model,
    )
    async for ev in async_translate(cfg):
        et = ev.get("type")
        if et == "progress_update":
            log.info(
                "[%s] stage %.0f%% / overall %.0f%%",
                ev.get("stage"),
                ev.get("stage_progress", 0),
                ev.get("overall_progress", 0),
            )
        elif et == "progress_end":
            log.info("[%s] stage done", ev.get("stage"))
        elif et == "finish":
            r = ev["translate_result"]
            log.info("FINISHED in %.1fs", r.total_seconds)
            log.info(
                "dual pdf: %s",
                r.no_watermark_dual_pdf_path or r.dual_pdf_path,
            )
            # BabelDOC 0.5.24 leaves non-daemon executor threads alive
            # after FINISH, so asyncio teardown stalls for ~20min. The
            # dual.pdf is already on disk here — force-exit is safe.
            _force_exit(0)
        elif et == "error":
            log.error("ERROR: %s", ev.get("error"))
            _force_exit(1)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_pdf")
    p.add_argument("output_dir")
    p.add_argument("--lang-in", default="en")
    p.add_argument("--lang-out", default="zh-TW")
    p.add_argument("--qps", type=int, default=2)
    p.add_argument("--compat", action="store_true",
                   help="Pass --enhance-compatibility to BabelDOC. "
                        "Off by default; rasterizes complex pages and breaks "
                        "selectability of the original column.")
    p.add_argument("--model", default="sonnet",
                   help="Claude model alias / id passed to `claude --model`. "
                        "Default 'sonnet' — translation is many-call, so we "
                        "favor Sonnet's speed/cost over Opus's reasoning. "
                        "Override with 'opus', 'haiku', or a full model id "
                        "(e.g. 'claude-sonnet-4-6').")
    return p.parse_args()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(2)
    asyncio.run(run(parse_args()))
