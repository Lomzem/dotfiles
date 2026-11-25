"""Per-instance atomic cache store and refresh lock serialization."""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
import fcntl
import json
import os
from pathlib import Path
import tempfile
from typing import Iterator

from .models import (
    ProviderError,
    UsageSnapshot,
    format_iso_utc,
    parse_iso_utc,
    snapshot_from_dict,
    snapshot_to_dict,
)


@dataclass(frozen=True)
class CachedEntry:
    snapshot: UsageSnapshot | None
    cooldown_until: datetime | None
    last_error: ProviderError | None


class InstanceCacheStore:
    """Stores one JSON file and one lock file per provider instance."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir

    def _entry_path(self, instance_id: str) -> Path:
        safe_id = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in instance_id)
        return self.cache_dir / f"{safe_id}.json"

    def _lock_path(self, instance_id: str) -> Path:
        safe_id = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in instance_id)
        return self.cache_dir / f"{safe_id}.lock"

    @contextmanager
    def lock(self, instance_id: str) -> Iterator[None]:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        lock_file = self._lock_path(instance_id)
        with lock_file.open("a+", encoding="utf-8") as fh:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(fh.fileno(), fcntl.LOCK_UN)

    def read(self, instance_id: str) -> CachedEntry:
        path = self._entry_path(instance_id)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return CachedEntry(snapshot=None, cooldown_until=None, last_error=None)
        if not isinstance(raw, dict):
            return CachedEntry(snapshot=None, cooldown_until=None, last_error=None)

        snap_raw = raw.get("snapshot")
        snap = snapshot_from_dict(instance_id, snap_raw) if isinstance(snap_raw, dict) else None
        if snap is not None and snap.source == "claude-probe":
            snap = UsageSnapshot(
                instance_id=snap.instance_id,
                source="tool-cache",
                checked_at=snap.checked_at,
                windows=snap.windows,
                reset_credits=snap.reset_credits,
            )

        cooldown_until = parse_iso_utc(raw.get("cooldownUntil"))
        err_raw = raw.get("lastError")
        last_error: ProviderError | None = None
        if isinstance(err_raw, dict) and isinstance(err_raw.get("code"), str):
            retry_after = err_raw.get("retryAfterSeconds")
            last_error = ProviderError(
                code=err_raw["code"],
                message=str(err_raw.get("message") or ""),
                retry_after_seconds=retry_after if isinstance(retry_after, int) else None,
            )
        return CachedEntry(snapshot=snap, cooldown_until=cooldown_until, last_error=last_error)

    def write(
        self,
        instance_id: str,
        snapshot: UsageSnapshot | None,
        cooldown_until: datetime | None = None,
        last_error: ProviderError | None = None,
    ) -> None:
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        payload = {
            "snapshot": snapshot_to_dict(snapshot) if snapshot is not None else None,
            "cooldownUntil": format_iso_utc(cooldown_until),
            "lastError": (
                {
                    "code": last_error.code,
                    "message": last_error.message,
                    "retryAfterSeconds": last_error.retry_after_seconds,
                }
                if last_error is not None
                else None
            ),
        }
        target = self._entry_path(instance_id)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", suffix=".tmp", dir=str(self.cache_dir))
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=2)
                fh.write("\n")
                fh.flush()
                os.fsync(fh.fileno())
            os.replace(tmp_name, target)
        except Exception:
            try:
                os.unlink(tmp_name)
            except OSError:
                pass
            raise

    def record_failure(
        self,
        instance_id: str,
        existing_snapshot: UsageSnapshot | None,
        error: ProviderError,
        now: datetime,
        cooldown_seconds: int,
    ) -> None:
        seconds = error.retry_after_seconds if error.retry_after_seconds else cooldown_seconds
        cooldown_until = now + timedelta(seconds=max(1, seconds))
        self.write(
            instance_id=instance_id,
            snapshot=existing_snapshot,
            cooldown_until=cooldown_until,
            last_error=error,
        )


def pick_newest_snapshot(
    t3_snapshot: UsageSnapshot | None,
    tool_snapshot: UsageSnapshot | None,
) -> UsageSnapshot | None:
    if t3_snapshot is None:
        return tool_snapshot
    if tool_snapshot is None:
        return t3_snapshot
    if tool_snapshot.checked_at > t3_snapshot.checked_at:
        if tool_snapshot.reset_credits is None and t3_snapshot.reset_credits is not None:
            return UsageSnapshot(
                instance_id=tool_snapshot.instance_id,
                source=tool_snapshot.source,
                checked_at=tool_snapshot.checked_at,
                windows=tool_snapshot.windows,
                reset_credits=t3_snapshot.reset_credits,
            )
        return tool_snapshot
    return t3_snapshot
