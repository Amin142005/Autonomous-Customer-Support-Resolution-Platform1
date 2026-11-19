"""Structured JSON logging with automatic file rotation.

Every log line is a JSON object with at least:
- `level` — severity
- `time` — ISO-8601 timestamp with timezone
- `message` — human-readable text
- `logger` — logger name

Optional enrichment fields (added by middleware or agents):
- `request_id` — per-request UUID
- `event` — semantic event name (e.g. `ticket.created`)
- `duration_ms` — operation duration
- `error` — exception class name when an error occurs

In production the logger writes JSON. In development you can switch to
human-readable `console` format via `LOG_FORMAT=console`.

Log files are rotated at **10 MB** and kept for **3 backups** (configurable
via `LOG_MAX_BYTES` and `LOG_BACKUP_COUNT` settings).
"""

from __future__ import annotations

import logging
import sys
import time
from logging import handlers as logging_handlers
from pathlib import Path
from typing import Any, Dict

from .config import Settings, get_settings


class _JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line, without external dependencies."""

    def format(self, record: logging.LogRecord) -> str:
        import json  # local import to avoid top-level dependency on the stdlib json during module load

        level = getattr(record, "level", record.levelname)
        msg = record.getMessage()

        entry: Dict[str, Any] = {
            "level": level,
            "time": self.formatTime(record, self.datefmt),
            "message": msg,
            "logger": record.name,
        }

        # Enrichment fields (if set by middleware/agents)
        if hasattr(record, "request_id"):
            entry["request_id"] = record.request_id
        if hasattr(record, "event"):
            entry["event"] = record.event
        if hasattr(record, "duration_ms"):
            entry["duration_ms"] = record.duration_ms
        if hasattr(record, "user_id"):
            entry["user_id"] = record.user_id
        if hasattr(record, "ticket_id"):
            entry["ticket_id"] = record.ticket_id
        if hasattr(record, "category"):
            entry["category"] = record.category

        # Exception info
        if record.exc_info and record.exc_info[0] is not None:
            entry["error"] = record.exc_info[0].__name__
            entry["stack"] = self.formatException(record.exc_info)

        return json.dumps(entry, default=str)


class _ConsoleFormatter(logging.Formatter):
    """Human-readable coloured-style formatter for development."""

    def format(self, record: logging.LogRecord) -> str:
        level = record.levelname
        time_str = self.formatTime(record, self.datefmt)
        msg = record.getMessage()

        req_id = getattr(record, "request_id", "")
        event = getattr(record, "event", "")
        duration = getattr(record, "duration_ms", "")

        parts = [time_str, f"[{level}]", record.name]
        if req_id:
            parts.append(f"(req:{req_id})")
        if event:
            parts.append(f"event={event}")
        if duration:
            parts.append(f"{duration}ms")
        parts.append(msg)

        return " ".join(parts)


def setup_logging(settings: Settings | None = None) -> None:
    """Configure the root logger once at application startup.

    Creates the log directory, attaches a rotating file handler (JSON format)
    and a console handler (format depends on `LOG_FORMAT` setting).
    """
    if settings is None:
        settings = get_settings()

    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "app.log"

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG))

    # Remove any existing handlers (idempotent re-calls)
    root_logger.handlers.clear()

    # -- File handler: always JSON, with rotation --------------------------
    file_handler = logging_handlers.RotatingFileHandler(
        filename=log_file,
        maxBytes=settings.LOG_MAX_BYTES,
        backupCount=settings.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(_JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z"))
    root_logger.addHandler(file_handler)

    # -- Console handler: JSON or human-readable --------------------------
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.DEBUG))
    if settings.LOG_FORMAT.lower() == "json":
        console_handler.setFormatter(_JsonFormatter(datefmt="%Y-%m-%dT%H:%M:%S%z"))
    else:
        console_handler.setFormatter(_ConsoleFormatter(datefmt="%Y-%m-%d %H:%M:%S"))
    root_logger.addHandler(console_handler)

    # Silence noisy third-party loggers in development
    for noisy in ("uvicorn.error", "uvicorn.access", "watchfiles", "httpcore", "httpx"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    root_logger.info(
        "Logging initialised",
        extra={
            "event": "logging.initialised",
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
        },
    )


# ── Convenience helpers used throughout the codebase ────────────────────────

def enrich(record: logging.LogRecord, **kwargs: Any) -> None:
    """Attach extra fields to a LogRecord so the JSON formatter picks them up.

    Typical use:
        logger.info("ticket resolved", extra={"event": "ticket.resolved", "ticket_id": tid})

    The `extra` dict keys become top-level JSON keys on the log line.
    """
    for key, value in kwargs.items():
        setattr(record, key, value)


def get_logger(name: str = __name__) -> logging.LoggerAdapter:
    """Return a LoggerAdapter that auto-attaches the caller's module name."""
    return logging.getLogger(name)
