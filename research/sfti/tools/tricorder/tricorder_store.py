"""Crash-aware append-only JSONL observation store for TRICORDER/SENTINEL.

Single-writer local store. Each line is a checksummed envelope with a
monotonically increasing sequence number. A torn, non-newline-terminated tail
is discarded on recovery; complete corruption fails closed.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import threading
from pathlib import Path
from typing import Any

from tricorder import validate_observation


class StoreCorruptionError(RuntimeError):
    """Raised when a complete stored record fails integrity or sequence checks."""


def _canonical_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


class ObservationStore:
    """Append-only store with fsync and deterministic recovery; one writer only."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._sequence = 0
        self._recover()

    @property
    def last_sequence(self) -> int:
        return self._sequence

    def _recover(self) -> None:
        if not self.path.exists():
            self.path.touch()
        raw = self.path.read_bytes()
        if raw and not raw.endswith(b"\n"):
            last_newline = raw.rfind(b"\n")
            safe_end = last_newline + 1
            with self.path.open("r+b") as stream:
                stream.truncate(safe_end)
                stream.flush()
                os.fsync(stream.fileno())
            raw = raw[:safe_end]

        expected = 1
        for line_number, line in enumerate(raw.splitlines(), start=1):
            try:
                envelope = json.loads(line)
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise StoreCorruptionError(f"line {line_number}: invalid complete JSON record") from exc
            if not isinstance(envelope, dict) or set(envelope) != {"sequence", "observation", "sha256"}:
                raise StoreCorruptionError(f"line {line_number}: invalid envelope shape")
            sequence = envelope["sequence"]
            observation = envelope["observation"]
            digest = envelope["sha256"]
            if sequence != expected:
                raise StoreCorruptionError(f"line {line_number}: expected sequence {expected}, got {sequence}")
            if not isinstance(observation, dict) or not isinstance(digest, str):
                raise StoreCorruptionError(f"line {line_number}: invalid observation or digest type")
            errors = validate_observation(observation)
            if errors:
                raise StoreCorruptionError(f"line {line_number}: invalid observation: {'; '.join(errors)}")
            payload = {"sequence": sequence, "observation": observation}
            actual = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
            if not hmac.compare_digest(actual, digest):
                raise StoreCorruptionError(f"line {line_number}: checksum mismatch")
            expected += 1
        self._sequence = expected - 1

    def append(self, observation: dict[str, Any]) -> int:
        errors = validate_observation(observation)
        if errors:
            raise ValueError("observation rejected: " + "; ".join(errors))
        with self._lock:
            sequence = self._sequence + 1
            payload = {"sequence": sequence, "observation": observation}
            envelope = dict(payload)
            envelope["sha256"] = hashlib.sha256(_canonical_bytes(payload)).hexdigest()
            encoded = _canonical_bytes(envelope) + b"\n"
            fd = os.open(self.path, os.O_WRONLY | os.O_APPEND)
            try:
                view = memoryview(encoded)
                while view:
                    written = os.write(fd, view)
                    if written <= 0:
                        raise OSError("append made no forward progress")
                    view = view[written:]
                os.fsync(fd)
            finally:
                os.close(fd)
            self._sequence = sequence
            return sequence

    def iter_records(self):
        """Yield (sequence, observation) pairs after a fresh integrity check."""
        self._recover()
        with self.path.open("r", encoding="utf-8") as stream:
            for line in stream:
                envelope = json.loads(line)
                yield envelope["sequence"], envelope["observation"]
