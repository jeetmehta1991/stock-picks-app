"""Batch 374 DEC-230: structured-JSON logger helper.

Source (per CHECKLIST #77): owner directive Pass 52 turn 85 RESOLVED-DECIDED:
"Logging audit + standard. Structured JSON (machine-parseable). Daily log
rotation. Standardized levels (DEBUG/INFO/WARNING/ERROR/CRITICAL). Common
context fields (timestamp, module, function, ticker, strategy, regime)."
Joint with DEC-231 bare-except audit.

This module provides the helper - it does NOT refactor every caller in
the codebase (multi-day invasive change). Callers that opt in get
structured JSON logs to a separate rotating file alongside the existing
plaintext logger. New code should use this; legacy logging.getLogger(...)
calls keep working.

Activation:
  from backtest.util.structured_logger import get_json_logger
  log = get_json_logger("my.module")
  log.info("trade_fired", extra={"ticker": "AAPL", "strategy": "rsi_oversold"})

Output: ./logs/structured_<DATE>.jsonl one line per event:
  {"ts": "2026-05-26T12:34:56Z", "level": "INFO", "logger": "my.module",
   "msg": "trade_fired", "ticker": "AAPL", "strategy": "rsi_oversold"}

Why JSON-lines (not nested JSON): grep/jq/Splunk-friendly + each line is
self-contained. Rotation by date keeps file sizes manageable for a 10h
Phase 1A-beta run (~100k events / ~50 MB).

Falls back to plain-text formatter when python-json-logger is unavailable
(dev environment without the package). The helper signature is stable so
opt-in callers don't break.
"""
from __future__ import annotations

import json
import logging
import logging.handlers
from datetime import datetime, timezone
from pathlib import Path

# DEC-230 common context fields the JSON formatter promotes to top-level keys
DEC_230_CONTEXT_FIELDS = (
    "ticker", "strategy", "regime", "as_of", "phase", "batch",
    "exit_method", "direction", "sector", "tier",
)


class _JsonFormatter(logging.Formatter):
    """Minimal JSON formatter - no python-json-logger dep required."""

    def format(self, record: logging.LogRecord) -> str:
        out = {
            "ts":     datetime.fromtimestamp(record.created, tz=timezone.utc)
                          .isoformat(timespec="milliseconds")
                          .replace("+00:00", "Z"),
            "level":  record.levelname,
            "logger": record.name,
            "msg":    record.getMessage(),
        }
        # Promote DEC-230 context fields from extra= kwarg
        for field in DEC_230_CONTEXT_FIELDS:
            if hasattr(record, field):
                out[field] = getattr(record, field)
        if record.exc_info:
            out["exc"] = self.formatException(record.exc_info)
        return json.dumps(out, default=str)


_json_loggers: dict[str, logging.Logger] = {}


def get_json_logger(name: str,
                    log_dir: Path | None = None,
                    level: int = logging.INFO) -> logging.Logger:
    """Get-or-create a JSON-lines logger writing to logs/structured_<DATE>.jsonl.

    Idempotent: repeated calls with the same name return the same logger
    instance (handlers not duplicated).

    Args:
        name: logger name (typically __name__)
        log_dir: output directory; defaults to repo-root/logs/
        level: minimum level (per DEC-230 standardized levels)

    Returns:
        Configured logger; .info / .warning / .error / .critical work
        normally. Pass DEC_230_CONTEXT_FIELDS via `extra={"ticker": "X", ...}`
        to enrich each log line with structured fields.
    """
    if name in _json_loggers:
        return _json_loggers[name]

    logger = logging.getLogger(f"structured.{name}")
    logger.setLevel(level)
    logger.propagate = False  # don't double-log to root

    repo_root = Path(__file__).resolve().parents[2]
    log_dir = log_dir or (repo_root / "logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = log_dir / f"structured_{today}.jsonl"

    handler = logging.handlers.TimedRotatingFileHandler(
        log_path, when="midnight", backupCount=14, encoding="utf-8",
    )
    handler.setFormatter(_JsonFormatter())
    logger.addHandler(handler)

    _json_loggers[name] = logger
    return logger


def reset_json_loggers() -> None:
    """Test-only: clear the cache + close handlers. Called by pytest tearDown."""
    for logger in _json_loggers.values():
        for h in list(logger.handlers):
            try:
                h.close()
            except Exception:
                pass
            logger.removeHandler(h)
    _json_loggers.clear()
