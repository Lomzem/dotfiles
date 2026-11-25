"""Typed domain models and boundary parsers for T3 Code provider usage."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
DEFAULT_TTL_SECONDS = 300
ERROR_COOLDOWN_SECONDS = 60
THROTTLE_COOLDOWN_SECONDS = 300
FIVE_HOUR_FLOOR_PERCENT = 15.0
WEEKLY_FLOOR_PERCENT = 10.0

CLAUDE_DRIVER = "claudeAgent"


def parse_iso_utc(raw: Any) -> datetime | None:
    if not isinstance(raw, str) or not raw.strip():
        return None
    text = raw.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def format_iso_utc(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def format_duration(seconds: float) -> str:
    total = int(max(0, round(seconds)))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)
    if days > 0:
        return f"{days}d{hours:02d}h"
    if hours > 0:
        return f"{hours}h{minutes:02d}m"
    if minutes > 0:
        return f"{minutes}m"
    return f"{secs}s"


def _clamp_remaining(used_percent: Any) -> float | None:
    if isinstance(used_percent, bool) or not isinstance(used_percent, (int, float)):
        return None
    remaining = 100.0 - float(used_percent)
    clamped = max(0.0, min(100.0, remaining))
    rounded = round(clamped, 2)
    return int(rounded) if rounded.is_integer() else rounded


def _clean_number(value: Any) -> float | int | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    rounded = round(float(value), 2)
    return int(rounded) if rounded.is_integer() else rounded


@dataclass(frozen=True)
class ProviderSpec:
    instance_id: str
    driver: str
    display_name: str
    enabled: bool
    binary_path: str | None = None
    home_path: str | None = None
    model: str | None = None


@dataclass(frozen=True)
class UsageWindow:
    id: str
    kind: str
    label: str
    remaining_percent: float | int
    resets_at: datetime | None = None
    window_duration_mins: int | None = None
    model_scope: str | None = None


@dataclass(frozen=True)
class ResetCredits:
    available_count: int
    next_expires_at: datetime | None = None


@dataclass(frozen=True)
class ProviderError:
    code: str
    message: str
    retry_after_seconds: int | None = None


@dataclass(frozen=True)
class UsageSnapshot:
    instance_id: str
    source: str
    checked_at: datetime
    windows: tuple[UsageWindow, ...]
    reset_credits: ResetCredits | None = None


@dataclass(frozen=True)
class ProviderReport:
    spec: ProviderSpec
    snapshot: UsageSnapshot | None
    status: str
    freshness: str
    age_seconds: int | None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    error: ProviderError | None = None


@dataclass(frozen=True)
class Recommendation:
    provider_instance_id: str
    display_name: str
    model: str | None
    low_headroom: bool
    reason: str


def _read_json_file(path: Path) -> dict[str, Any] | None:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return raw if isinstance(raw, dict) else None


def _pick_model_slug(cache_data: dict[str, Any] | None, driver: str) -> str | None:
    if not cache_data:
        return None
    models = cache_data.get("models")
    if not isinstance(models, list):
        return None
    default_slug: str | None = None
    first_slug: str | None = None
    for entry in models:
        if not isinstance(entry, dict):
            continue
        slug = entry.get("slug") or entry.get("id")
        if not isinstance(slug, str) or not slug.strip():
            continue
        slug = slug.strip()
        if first_slug is None:
            first_slug = slug
        if entry.get("isDefault") is True and default_slug is None:
            default_slug = slug
        if driver == CLAUDE_DRIVER and "opus" in slug.lower():
            return slug
    return default_slug or first_slug


def _parse_reset_credits(raw: Any) -> ResetCredits | None:
    if not isinstance(raw, dict):
        return None
    count = raw.get("availableCount")
    if isinstance(count, bool) or not isinstance(count, int):
        return None
    return ResetCredits(
        available_count=count,
        next_expires_at=parse_iso_utc(raw.get("nextExpiresAt")),
    )


def _window_label(win_id: str, kind: str, raw_label: Any) -> str:
    if isinstance(raw_label, str) and raw_label.strip():
        return raw_label.strip()
    defaults = {
        "five_hour": "Session (5h)",
        "seven_day": "Weekly (7d)",
        "seven_day_opus": "Opus weekly (7d)",
    }
    return defaults.get(win_id, kind or win_id)


def parse_t3_cache_snapshot(instance_id: str, cache_path: Path) -> UsageSnapshot | None:
    data = _read_json_file(cache_path)
    if not data:
        return None
    limits = data.get("usageLimits")
    if not isinstance(limits, dict):
        return None
    checked_at = parse_iso_utc(limits.get("checkedAt"))
    if checked_at is None:
        return None
    raw_windows = limits.get("windows")
    windows: list[UsageWindow] = []
    if isinstance(raw_windows, list):
        for item in raw_windows:
            if not isinstance(item, dict):
                continue
            win_id = item.get("id")
            if not isinstance(win_id, str) or not win_id.strip():
                continue
            rem = _clamp_remaining(item.get("usedPercent"))
            if rem is None:
                continue
            kind = str(item.get("kind") or "")
            duration = item.get("windowDurationMins")
            duration_mins = duration if isinstance(duration, int) and not isinstance(duration, bool) else None
            scope = item.get("modelScope")
            windows.append(
                UsageWindow(
                    id=win_id.strip(),
                    kind=kind,
                    label=_window_label(win_id.strip(), kind, item.get("label")),
                    remaining_percent=rem,
                    resets_at=parse_iso_utc(item.get("resetsAt")),
                    window_duration_mins=duration_mins,
                    model_scope=scope.strip() if isinstance(scope, str) and scope.strip() else None,
                )
            )
    return UsageSnapshot(
        instance_id=instance_id,
        source="t3-cache",
        checked_at=checked_at,
        windows=tuple(windows),
        reset_credits=_parse_reset_credits(limits.get("resetCredits")),
    )


def parse_claude_probe_payload(
    instance_id: str,
    payload: dict[str, Any],
    checked_at: datetime,
    reset_credits: ResetCredits | None = None,
) -> tuple[UsageSnapshot | None, ProviderError | None]:
    if not isinstance(payload, dict):
        return None, ProviderError("invalid_probe_response", "Claude probe returned non-object payload.")
    if payload.get("rate_limits_available") is False:
        return None, ProviderError("rate_limits_unavailable", "Claude probe reported rate_limits_available=false.")
    rate_limits = payload.get("rate_limits")
    if not isinstance(rate_limits, dict):
        return None, ProviderError("invalid_probe_response", "Claude probe omitted rate_limits.")

    specs = (
        ("five_hour", "session", "Session (5h)", 300, None),
        ("seven_day", "weekly", "Weekly (7d)", 10080, None),
        ("seven_day_opus", "weekly", "Opus weekly (7d)", 10080, "opus"),
    )
    windows: list[UsageWindow] = []
    for key, kind, label, duration, scope in specs:
        raw_win = rate_limits.get(key)
        if not isinstance(raw_win, dict):
            continue
        rem = _clamp_remaining(raw_win.get("utilization"))
        if rem is None:
            continue
        windows.append(
            UsageWindow(
                id=key,
                kind=kind,
                label=label,
                remaining_percent=rem,
                resets_at=parse_iso_utc(raw_win.get("resets_at")),
                window_duration_mins=duration,
                model_scope=scope,
            )
        )

    if not windows:
        return None, ProviderError("empty_usage_windows", "Claude probe returned no parseable quota windows.")

    return (
        UsageSnapshot(
            instance_id=instance_id,
            source="claude-probe",
            checked_at=checked_at,
            windows=tuple(windows),
            reset_credits=reset_credits,
        ),
        None,
    )


def load_provider_specs(t3_dir: Path, include_all: bool = False) -> list[ProviderSpec]:
    settings_path = t3_dir / "userdata" / "settings.json"
    caches_dir = t3_dir / "caches"
    settings = _read_json_file(settings_path) or {}
    raw_instances = settings.get("providerInstances")

    specs: list[ProviderSpec] = []
    seen: set[str] = set()

    if isinstance(raw_instances, dict):
        for instance_id, raw in raw_instances.items():
            if not isinstance(raw, dict):
                continue
            enabled = raw.get("enabled")
            if enabled is False:
                continue
            driver = str(raw.get("driver") or "")
            if not include_all and driver != CLAUDE_DRIVER:
                continue
            cache_data = _read_json_file(caches_dir / f"{instance_id}.json")
            display = raw.get("displayName")
            if not isinstance(display, str) or not display.strip():
                cache_display = cache_data.get("displayName") if cache_data else None
                display = cache_display if isinstance(cache_display, str) and cache_display.strip() else instance_id
            cfg = raw.get("config") if isinstance(raw.get("config"), dict) else {}
            binary_path = cfg.get("binaryPath")
            home_path = cfg.get("homePath")
            specs.append(
                ProviderSpec(
                    instance_id=instance_id,
                    driver=driver,
                    display_name=display.strip(),
                    enabled=True,
                    binary_path=binary_path.strip() if isinstance(binary_path, str) and binary_path.strip() else None,
                    home_path=home_path.strip() if isinstance(home_path, str) else None,
                    model=_pick_model_slug(cache_data, driver),
                )
            )
            seen.add(instance_id)

    # Fallback discovery from cache files if settings.json is absent.
    if not specs and caches_dir.is_dir():
        for cache_file in sorted(caches_dir.glob("*.json")):
            cache_data = _read_json_file(cache_file)
            if not cache_data or cache_data.get("enabled") is not True:
                continue
            instance_id = cache_data.get("instanceId")
            driver = cache_data.get("driver")
            if not isinstance(instance_id, str) or not isinstance(driver, str) or instance_id in seen:
                continue
            if not include_all and driver != CLAUDE_DRIVER:
                continue
            display = cache_data.get("displayName")
            specs.append(
                ProviderSpec(
                    instance_id=instance_id,
                    driver=driver,
                    display_name=display.strip() if isinstance(display, str) and display.strip() else instance_id,
                    enabled=True,
                    binary_path="claude" if driver == CLAUDE_DRIVER else None,
                    home_path=None,
                    model=_pick_model_slug(cache_data, driver),
                )
            )
            seen.add(instance_id)

    specs.sort(key=lambda s: (0 if s.driver == CLAUDE_DRIVER else 1, s.instance_id))
    return specs


def snapshot_to_dict(snapshot: UsageSnapshot) -> dict[str, Any]:
    return {
        "schemaVersion": SCHEMA_VERSION,
        "instanceId": snapshot.instance_id,
        "source": snapshot.source,
        "checkedAt": format_iso_utc(snapshot.checked_at),
        "windows": [
            {
                "id": w.id,
                "kind": w.kind,
                "label": w.label,
                "remainingPercent": _clean_number(w.remaining_percent),
                "resetsAt": format_iso_utc(w.resets_at),
                "windowDurationMins": w.window_duration_mins,
                "modelScope": w.model_scope,
            }
            for w in snapshot.windows
        ],
        "resetCredits": (
            {
                "availableCount": snapshot.reset_credits.available_count,
                "nextExpiresAt": format_iso_utc(snapshot.reset_credits.next_expires_at),
            }
            if snapshot.reset_credits is not None
            else None
        ),
    }


def snapshot_from_dict(instance_id: str, data: dict[str, Any]) -> UsageSnapshot | None:
    if not isinstance(data, dict):
        return None
    checked_at = parse_iso_utc(data.get("checkedAt"))
    if checked_at is None:
        return None
    raw_windows = data.get("windows")
    windows: list[UsageWindow] = []
    if isinstance(raw_windows, list):
        for item in raw_windows:
            if not isinstance(item, dict):
                continue
            win_id = item.get("id")
            rem = _clean_number(item.get("remainingPercent"))
            if not isinstance(win_id, str) or not win_id.strip() or rem is None:
                continue
            kind = str(item.get("kind") or "")
            dur = item.get("windowDurationMins")
            scope = item.get("modelScope")
            cleaned = _clean_number(max(0.0, min(100.0, float(rem))))
            assert cleaned is not None
            windows.append(
                UsageWindow(
                    id=win_id.strip(),
                    kind=kind,
                    label=_window_label(win_id.strip(), kind, item.get("label")),
                    remaining_percent=cleaned,
                    resets_at=parse_iso_utc(item.get("resetsAt")),
                    window_duration_mins=dur if isinstance(dur, int) and not isinstance(dur, bool) else None,
                    model_scope=scope if isinstance(scope, str) and scope else None,
                )
            )
    if not windows:
        return None
    return UsageSnapshot(
        instance_id=instance_id,
        source=str(data.get("source") or "tool-cache"),
        checked_at=checked_at,
        windows=tuple(windows),
        reset_credits=_parse_reset_credits(data.get("resetCredits")),
    )
