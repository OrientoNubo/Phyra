"""
Output PDF compression.

  - off       : do nothing.
  - lossless  : no-op — build_dual already saves with
                garbage=4 / deflate / clean / use_objstms, so the dual is
                already losslessly optimized; no Ghostscript needed.
  - lossy     : Ghostscript image downsampling at a chosen DPI / preset.

Fail-safe: if Ghostscript is missing, errors, or the result is not smaller
than the input, the original file is left untouched and the job continues
(compression must never fail a translation).
"""

from __future__ import annotations

import logging
import shutil
import subprocess
from pathlib import Path

log = logging.getLogger("phyra-dualtrans.compress")

PRESET_MAP = {
    "screen": "/screen",
    "ebook": "/ebook",
    "printer": "/printer",
}
VALID_MODES = ("off", "lossless", "lossy")


def compress_pdf(
    pdf: Path,
    mode: str,
    *,
    dpi: int = 150,
    preset: str = "ebook",
) -> dict:
    """Compress `pdf` in place per `mode`. Returns a stats dict; never raises
    for a compression failure (returns applied=False with a note instead)."""
    pdf = Path(pdf)
    orig = pdf.stat().st_size
    base = {"mode": mode, "original_bytes": orig, "final_bytes": orig,
            "applied": False}

    if mode not in VALID_MODES:
        raise ValueError(f"invalid compress mode {mode!r} (use {VALID_MODES})")

    if mode == "off":
        return {**base, "note": "compression disabled"}

    if mode == "lossless":
        return {
            **base,
            "note": "build_dual already deflated (garbage=4); no Ghostscript",
        }

    # mode == "lossy"
    gs = shutil.which("gs")
    if not gs:
        return {**base, "note": "Ghostscript (gs) not found; left uncompressed"}

    tmp = pdf.with_name(pdf.stem + ".gs-tmp.pdf")
    mono_res = max(dpi * 2, 300)
    cmd = [
        gs,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.5",
        f"-dPDFSETTINGS={PRESET_MAP.get(preset, '/ebook')}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        "-dDetectDuplicateImages=true",
        "-dDownsampleColorImages=true",
        f"-dColorImageResolution={dpi}",
        "-dDownsampleGrayImages=true",
        f"-dGrayImageResolution={dpi}",
        "-dDownsampleMonoImages=true",
        f"-dMonoImageResolution={mono_res}",
        f"-sOutputFile={tmp}",
        str(pdf),
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except Exception as e:  # noqa: BLE001 — fail-safe, keep original
        tmp.unlink(missing_ok=True)
        return {**base, "note": f"Ghostscript invocation failed: {e}"}

    if res.returncode != 0 or not tmp.exists() or tmp.stat().st_size == 0:
        tmp.unlink(missing_ok=True)
        return {
            **base,
            "note": f"Ghostscript rc={res.returncode}: "
                    f"{(res.stderr or '').strip()[:200]}",
        }

    new = tmp.stat().st_size
    if new >= orig:
        tmp.unlink(missing_ok=True)
        return {
            **base,
            "note": f"compressed size {new} ≥ original {orig}; kept original",
        }

    tmp.replace(pdf)
    log.info("compressed %s: %d → %d bytes (%.1f%%)",
             pdf.name, orig, new, 100.0 * new / orig)
    return {
        "mode": "lossy",
        "original_bytes": orig,
        "final_bytes": new,
        "applied": True,
        "ratio": round(new / orig, 3),
        "dpi": dpi,
        "preset": preset,
    }
