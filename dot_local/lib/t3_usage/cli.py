"""CLI entrypoint for t3-usage."""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any, Callable

from .models import (
    CLAUDE_DRIVER,
    DEFAULT_TTL_SECONDS,
    ERROR_COOLDOWN_SECONDS,
    FIVE_HOUR_FLOOR_PERCENT,
    SCHEMA_VERSION,
    THROTTLE_COOLDOWN_SECONDS,
    WEEKLY_FLOOR_PERCENT,
    ProviderError,
    ProviderReport,
    ProviderSpec,
    Recommendation,
    UsageSnapshot,
    format_duration,
    format_iso_utc,
    load_provider_specs,
    parse_claude_probe_payload,
    parse_t3_cache_snapshot,
)
from .policy import evaluate_provider, needs_refresh, recommend_opus, window_reset_passed
from .probe import DEFAULT_PROBE_TIMEOUT_SECONDS, probe_claude_usage
from .store import InstanceCacheStore, pick_newest_snapshot

ProbeFn = Callable[[ProviderSpec, float], tuple[dict[str, Any] | None, ProviderError | None]]


def default_t3_dir() -> Path:
    return Path.home() / ".t3"


def default_cache_dir() -> Path:
    xdg = os.environ.get("XDG_CACHE_HOME")
    base = Path(xdg) if xdg else Path.home() / ".cache"
    return base / "t3-usage"


def _resolve_provider(
    spec: ProviderSpec,
    t3_dir: Path,
    store: InstanceCacheStore,
    now_fn: Callable[[], datetime],
    ttl_seconds: int,
    force_refresh: bool,
    no_refresh: bool,
    probe_timeout: float,
    probe_fn: ProbeFn,
) -> ProviderReport:
    now = now_fn()
    t3_cache_path = t3_dir / "caches" / f"{spec.instance_id}.json"
    t3_snap = parse_t3_cache_snapshot(spec.instance_id, t3_cache_path)

    if spec.driver != CLAUDE_DRIVER:
        return evaluate_provider(spec, t3_snap, now, ttl_seconds)

    cached = store.read(spec.instance_id)
    best = pick_newest_snapshot(t3_snap, cached.snapshot)
    stale, _ = needs_refresh(best, now, ttl_seconds)

    if no_refresh or (not force_refresh and not stale):
        return evaluate_provider(spec, best, now, ttl_seconds)

    with store.lock(spec.instance_id):
        # Double-check after acquiring per-instance lock so parallel callers share one refresh.
        t3_snap = parse_t3_cache_snapshot(spec.instance_id, t3_cache_path)
        cached = store.read(spec.instance_id)
        best = pick_newest_snapshot(t3_snap, cached.snapshot)
        stale, _ = needs_refresh(best, now, ttl_seconds)

        if not force_refresh and not stale:
            return evaluate_provider(spec, best, now, ttl_seconds)

        if not force_refresh and cached.cooldown_until is not None and cached.cooldown_until > now:
            rem_secs = max(1, int((cached.cooldown_until - now).total_seconds()))
            err = cached.last_error or ProviderError("refresh_cooldown", "Recent usage refresh failed.")
            cooldown_err = ProviderError(
                code=err.code,
                message=f"{err.message} (cooldown active for {format_duration(rem_secs)})",
                retry_after_seconds=rem_secs,
            )
            return evaluate_provider(spec, best, now, ttl_seconds, error=cooldown_err)

        raw_payload, probe_err = probe_fn(spec, probe_timeout)
        checked_now = now_fn()
        if probe_err is not None or raw_payload is None:
            err = probe_err or ProviderError("probe_failed", "Claude usage probe returned no data.")
            cooldown = THROTTLE_COOLDOWN_SECONDS if err.code == "lookup_throttled" else ERROR_COOLDOWN_SECONDS
            store.record_failure(spec.instance_id, best, err, checked_now, cooldown)
            return evaluate_provider(spec, best, checked_now, ttl_seconds, error=err)

        fresh_snap, parse_err = parse_claude_probe_payload(
            spec.instance_id,
            raw_payload,
            checked_now,
            reset_credits=t3_snap.reset_credits if t3_snap is not None else None,
        )
        if parse_err is not None or fresh_snap is None:
            err = parse_err or ProviderError("invalid_probe_response", "Failed to parse Claude usage payload.")
            store.record_failure(spec.instance_id, best, err, checked_now, ERROR_COOLDOWN_SECONDS)
            return evaluate_provider(spec, best, checked_now, ttl_seconds, error=err)

        store.write(spec.instance_id, fresh_snap)
        return evaluate_provider(spec, fresh_snap, checked_now, ttl_seconds)


def collect_report(
    *,
    t3_dir: Path,
    cache_dir: Path,
    include_all: bool = False,
    ttl_seconds: int = DEFAULT_TTL_SECONDS,
    force_refresh: bool = False,
    no_refresh: bool = False,
    probe_timeout: float = DEFAULT_PROBE_TIMEOUT_SECONDS,
    now: datetime | None = None,
    probe_fn: ProbeFn = probe_claude_usage,
) -> dict[str, Any]:
    now_fn: Callable[[], datetime] = (lambda: now) if now is not None else (lambda: datetime.now(timezone.utc))
    specs = load_provider_specs(t3_dir, include_all=include_all)
    store = InstanceCacheStore(cache_dir)

    if len(specs) <= 1:
        reports = [
            _resolve_provider(
                spec,
                t3_dir,
                store,
                now_fn,
                ttl_seconds,
                force_refresh,
                no_refresh,
                probe_timeout,
                probe_fn,
            )
            for spec in specs
        ]
    else:
        with ThreadPoolExecutor(max_workers=min(4, len(specs))) as pool:
            futures = [
                pool.submit(
                    _resolve_provider,
                    spec,
                    t3_dir,
                    store,
                    now_fn,
                    ttl_seconds,
                    force_refresh,
                    no_refresh,
                    probe_timeout,
                    probe_fn,
                )
                for spec in specs
            ]
            reports = [f.result() for f in futures]

    final_now = now_fn()
    recommendation, rec_reason = recommend_opus(reports, final_now)

    return _serialize_report(reports, recommendation, rec_reason, final_now, ttl_seconds)


def _serialize_report(
    reports: list[ProviderReport],
    recommendation: Recommendation | None,
    rec_reason: str,
    now: datetime,
    ttl_seconds: int,
) -> dict[str, Any]:
    def serialize_provider(r: ProviderReport) -> dict[str, Any]:
        windows_out: list[dict[str, Any]] = []
        if r.snapshot is not None:
            for w in r.snapshot.windows:
                reset_passed = window_reset_passed(w, r.snapshot.checked_at, now)
                resets_in: str | None = None
                if w.resets_at is not None:
                    delta = (w.resets_at - now).total_seconds()
                    resets_in = "passed" if delta <= 0 else format_duration(delta)
                entry: dict[str, Any] = {
                    "id": w.id,
                    "kind": w.kind,
                    "label": w.label,
                    "remainingPercent": w.remaining_percent,
                    "resetsAt": format_iso_utc(w.resets_at),
                    "resetsIn": resets_in,
                    "resetPassed": reset_passed,
                }
                if w.model_scope:
                    entry["modelScope"] = w.model_scope
                windows_out.append(entry)

        credits_out = None
        if r.snapshot is not None and r.snapshot.reset_credits is not None:
            credits_out = {
                "availableCount": r.snapshot.reset_credits.available_count,
                "nextExpiresAt": format_iso_utc(r.snapshot.reset_credits.next_expires_at),
            }

        error_out = None
        if r.error is not None:
            error_out = {
                "code": r.error.code,
                "message": r.error.message,
                **({"retryAfterSeconds": r.error.retry_after_seconds} if r.error.retry_after_seconds is not None else {}),
            }

        return {
            "providerInstanceId": r.spec.instance_id,
            "displayName": r.spec.display_name,
            "driver": r.spec.driver,
            "model": r.spec.model,
            "status": r.status,
            "freshness": r.freshness,
            "source": r.snapshot.source if r.snapshot is not None else None,
            "checkedAt": format_iso_utc(r.snapshot.checked_at) if r.snapshot is not None else None,
            "ageSeconds": r.age_seconds,
            "windows": windows_out,
            "resetCredits": credits_out,
            "warnings": list(r.warnings),
            "error": error_out,
        }

    recommended_out = (
        {
            "providerInstanceId": recommendation.provider_instance_id,
            "displayName": recommendation.display_name,
            "model": recommendation.model,
            "lowHeadroom": recommendation.low_headroom,
            "reason": recommendation.reason,
        }
        if recommendation is not None
        else None
    )

    out: dict[str, Any] = {
        "schemaVersion": SCHEMA_VERSION,
        "observedAt": format_iso_utc(now),
        "ttlSeconds": ttl_seconds,
        "policy": {
            "fiveHourFloorPercent": int(FIVE_HOUR_FLOOR_PERCENT),
            "weeklyFloorPercent": int(WEEKLY_FLOOR_PERCENT),
            "tieBreak": "earliest_active_weekly_reset_then_higher_5h_remaining",
        },
        "recommended": recommended_out,
    }
    if recommended_out is None:
        out["recommendationReason"] = rec_reason
    out["providers"] = [serialize_provider(r) for r in reports]
    return out


def format_text_report(report: dict[str, Any]) -> str:
    lines: list[str] = []
    rec = report.get("recommended")
    if isinstance(rec, dict):
        model_str = f" model={rec['model']}" if rec.get("model") else ""
        tag = "RECOMMENDED (LOW HEADROOM)" if rec.get("lowHeadroom") else "RECOMMENDED"
        lines.append(
            f"{tag}: {rec['providerInstanceId']} ({rec['displayName']}){model_str} - {rec['reason']}"
        )
    else:
        lines.append(f"RECOMMENDED: none - {report.get('recommendationReason', 'no eligible Opus instance')}")

    for p in report.get("providers", []):
        win_parts: list[str] = []
        for w in p.get("windows", []):
            rem = f"{w['remainingPercent']}% rem"
            if w.get("resetsIn"):
                rem += f" (resets {w['resetsIn']})"
            elif w.get("resetsAt") is None:
                rem += " (not started)"
            win_parts.append(f"{w['id']}={rem}")
        wins_str = "  ".join(win_parts) if win_parts else "no windows"
        age = f"{p['ageSeconds']}s" if p.get("ageSeconds") is not None else "n/a"
        src = p.get("source") or "none"
        line = (
            f"{p['providerInstanceId']} ({p['displayName']})  [{p['status']}]  "
            f"{wins_str}  [{p['freshness']} {age} {src}]"
        )
        lines.append(line)
        if p.get("error"):
            lines.append(f"  error: {p['error']['code']}: {p['error']['message']}")
        for warn in p.get("warnings", []):
            lines.append(f"  warning: {warn}")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="t3-usage",
        description="Inspect T3 Code provider usage remaining and recommend the best Claude Opus instance.",
    )
    fmt = parser.add_mutually_exclusive_group()
    fmt.add_argument("--text", action="store_true", help="Output compact text (default).")
    fmt.add_argument("--json", action="store_true", help="Output structured JSON.")
    parser.add_argument("--all", action="store_true", help="Include all enabled T3 providers, not only Claude/Opus.")
    parser.add_argument("--refresh", action="store_true", help="Force a live Claude probe even within the cache TTL.")
    parser.add_argument("--no-refresh", action="store_true", help="Read cached snapshots only; never run live probes.")
    parser.add_argument(
        "--ttl",
        type=int,
        default=DEFAULT_TTL_SECONDS,
        help=f"Cache freshness TTL in seconds (default: {DEFAULT_TTL_SECONDS}).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_PROBE_TIMEOUT_SECONDS,
        help=f"Per-provider live probe timeout in seconds (default: {DEFAULT_PROBE_TIMEOUT_SECONDS:g}).",
    )
    parser.add_argument("--t3-dir", type=Path, default=None, help="Override ~/.t3 directory.")
    parser.add_argument("--cache-dir", type=Path, default=None, help="Override tool cache directory.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.ttl < 0:
        raise SystemExit("--ttl must be >= 0")
    if args.timeout <= 0:
        raise SystemExit("--timeout must be > 0")

    report = collect_report(
        t3_dir=args.t3_dir or default_t3_dir(),
        cache_dir=args.cache_dir or default_cache_dir(),
        include_all=args.all,
        ttl_seconds=args.ttl,
        force_refresh=args.refresh,
        no_refresh=args.no_refresh,
        probe_timeout=args.timeout,
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(format_text_report(report))
    return 0
