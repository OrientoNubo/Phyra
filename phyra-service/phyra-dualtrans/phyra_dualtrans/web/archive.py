"""Save a finished job's PDFs into a sibling phyra-archbase collection.

A successful translation produces an original + a bilingual dual PDF in
the job workdir. "Archiving" copies both into phyra-archbase's
``collection/`` under its filename convention (``{YYMM}_{Title}.pdf`` and
``{YYMM}_{Title}_bilingual.<lang>.dual.pdf``) and re-runs its
``generate_index.py`` so the new paper shows up in the browse page.

The copy + index-regeneration logic lives here (pure, dependency-injected
paths) so it is unit-testable without a real archbase or running server;
the route in ``routes_jobs.py`` resolves the paths from config and calls
``archive_files``.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from ..vendor.resolve_input import build_stem

_YYMM_RE = re.compile(r"^\d{4}$")


class ArchiveError(Exception):
    """Raised for caller-fixable problems (bad input, missing source).

    Carries an HTTP status so the route can map it directly.
    """

    def __init__(self, status: int, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


def suggest_name(stem: str) -> dict:
    """Best-guess {yymm, title} for prefilling the archive dialog.

    arXiv stems are already ``<YYMM>_<title>`` (e.g. ``2402_NetLLM_...``);
    split them. An upload stem with no 4-digit prefix has no date, so the
    yymm is left blank (the UI fills today's) and the whole stem becomes
    the title. The de-tokenization mirrors archbase's filename_to_display
    (``__`` → ``: ``, ``_`` → space)."""
    m = re.match(r"^(\d{4})_(.*)$", stem or "")
    if m:
        yymm, rest = m.group(1), m.group(2)
    else:
        yymm, rest = "", (stem or "")
    title = rest.replace("__", ": ").replace("_", " ").strip()
    return {"yymm": yymm, "title": title}


def archive_files(
    *,
    original: Path,
    dual: Path,
    yymm: str,
    title: str,
    lang_out: str,
    collection_dir: Path,
    generate_script: Path,
) -> dict:
    """Copy original + dual into ``collection_dir`` under the archbase
    naming convention, then regenerate the index. Returns
    ``{"stem", "files", "index_ok"}``. Raises ArchiveError on bad input
    or a missing source PDF."""
    yymm = (yymm or "").strip()
    if not _YYMM_RE.match(yymm):
        raise ArchiveError(400, "yymm must be 4 digits (e.g. 2402)")
    if not (title or "").strip():
        raise ArchiveError(400, "title is required")
    if not original.exists():
        raise ArchiveError(409, "original PDF missing — cannot archive")
    if not dual.exists():
        raise ArchiveError(409, "dual PDF missing — cannot archive")

    stem = build_stem(yymm, title)
    collection_dir.mkdir(parents=True, exist_ok=True)

    # archbase recognizes the bilingual artifact by the literal suffix
    # ``_bilingual.<lang>.dual.pdf``; keep the job's lang_out so the
    # convention round-trips (its index keys off this exact string).
    dest_original = collection_dir / f"{stem}.pdf"
    dest_dual = collection_dir / f"{stem}_bilingual.{lang_out}.dual.pdf"
    shutil.copy2(original, dest_original)
    shutil.copy2(dual, dest_dual)

    index_ok = _regenerate_index(generate_script)
    return {
        "stem": stem,
        "files": [dest_original.name, dest_dual.name],
        "index_ok": index_ok,
    }


def _regenerate_index(generate_script: Path) -> bool:
    """Re-run archbase's generate_index.py (pure-stdlib; safe to run with
    our own interpreter). Best-effort: a failure leaves the files in
    place (they appear on the next manual regen) rather than failing the
    archive."""
    try:
        r = subprocess.run(
            [sys.executable, str(generate_script)],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return r.returncode == 0
    except Exception:  # noqa: BLE001 — index refresh is best-effort
        return False
