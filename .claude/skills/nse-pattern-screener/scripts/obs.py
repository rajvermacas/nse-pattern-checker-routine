"""Shared observability for the screener scripts.

One log format, and a drop tally that refuses to stay quiet: every stage that
discards items must call Drops.add(reason, item) as it drops them and
Drops.report(kept, total) at the end. report() logs at WARNING whenever
anything was lost and returns a JSON-serialisable dict, so a coverage gap or a
swallowed exception shows up in the transcript AND in an archivable file --
instead of a symbol quietly vanishing from the count.

Log level is INFO by default; export SCREENER_LOG=DEBUG for per-drop examples.
Logs go to STDOUT to stay ordered with the scripts' existing progress prints in
the routine transcript.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import traceback


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter(
            "%(asctime)s %(levelname)-7s %(name)s | %(message)s", "%H:%M:%S"))
        logger.addHandler(h)
        logger.propagate = False
    level = os.environ.get("SCREENER_LOG", "INFO").upper()
    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger


def exc_line(e: BaseException) -> str:
    """Compact one-line exception label: 'KeyError: RELIANCE.NS'."""
    msg = str(e).replace("\n", " ").strip()
    return f"{type(e).__name__}: {msg}" if msg else type(e).__name__


def log_exception(logger: logging.Logger, context: str, e: BaseException) -> None:
    """WARNING with the compact label; full traceback only at DEBUG."""
    logger.warning("%s -> %s", context, exc_line(e))
    logger.debug("traceback for %s:\n%s", context, traceback.format_exc())


class Drops:
    """Counts why items were discarded and forces a summary that warns on loss."""

    def __init__(self, logger: logging.Logger, stage: str):
        self.log = logger
        self.stage = stage
        self.reasons: dict[str, int] = {}
        self.examples: dict[str, str] = {}

    def add(self, reason: str, item: object | None = None) -> None:
        self.reasons[reason] = self.reasons.get(reason, 0) + 1
        if item is not None and reason not in self.examples:
            self.examples[reason] = str(item)

    @property
    def total(self) -> int:
        return sum(self.reasons.values())

    def report(self, kept: int, total: int) -> dict:
        parts = ", ".join(f"{r}={n}" for r, n in sorted(self.reasons.items()))
        line = (f"{self.stage}: kept {kept}/{total}, dropped {self.total}"
                + (f" [{parts}]" if parts else ""))
        # A drop is expected (some symbols legitimately lack data); a drop the
        # code cannot name is not. Warn on any loss, escalate on unnamed loss.
        if self.reasons.get("exception") or self.reasons.get("parse_error"):
            self.log.error(line)
        elif self.total:
            self.log.warning(line)
        else:
            self.log.info(line)
        for r, ex in self.examples.items():
            self.log.debug("  %s e.g. %s", r, ex)
        return {"stage": self.stage, "kept": kept, "total": total,
                "dropped": self.total, "reasons": dict(self.reasons)}


def write_report(path: str, payload: dict) -> None:
    """Best-effort machine-readable stage report; never let it break the run."""
    try:
        with open(path, "w") as f:
            json.dump(payload, f, indent=2, default=str)
    except OSError as e:
        logging.getLogger("obs").warning("could not write %s -> %s", path, exc_line(e))
