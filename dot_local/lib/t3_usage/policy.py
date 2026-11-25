"""Pure quota freshness, eligibility, and Opus routing policy."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

from .models import (
    CLAUDE_DRIVER,
    FIVE_HOUR_FLOOR_PERCENT,
    WEEKLY_FLOOR_PERCENT,
    ProviderError,
    ProviderReport,
    ProviderSpec,
    Recommendation,
    UsageSnapshot,
    UsageWindow,
    format_duration,
)


def window_reset_passed(window: UsageWindow, checked_at: datetime, now: datetime) -> bool:
    return window.resets_at is not None and checked_at < window.resets_at <= now


def needs_refresh(
    snapshot: UsageSnapshot | None,
    now: datetime,
    ttl_seconds: int,
) -> tuple[bool, str]:
    if snapshot is None:
        return True, "missing"
    age = (now - snapshot.checked_at).total_seconds()
    if age > ttl_seconds:
        return True, "expired_ttl"
    for window in snapshot.windows:
        if window_reset_passed(window, snapshot.checked_at, now):
            return True, "window_reset_passed"
    return False, "fresh"


def _applicable_opus_windows(windows: Iterable[UsageWindow]) -> list[UsageWindow]:
    result: list[UsageWindow] = []
    for w in windows:
        if w.id in ("five_hour", "seven_day", "seven_day_opus"):
            result.append(w)
        elif w.model_scope and "opus" in w.model_scope.lower():
            result.append(w)
    return result


def _find_window(windows: Iterable[UsageWindow], win_id: str) -> UsageWindow | None:
    for w in windows:
        if w.id == win_id:
            return w
    return None


def _weekly_windows(windows: Iterable[UsageWindow]) -> list[UsageWindow]:
    return [w for w in windows if w.id in ("seven_day", "seven_day_opus") or w.kind == "weekly"]


def _effective_weekly_remaining(windows: Iterable[UsageWindow]) -> float | None:
    vals = [float(w.remaining_percent) for w in _weekly_windows(windows)]
    return min(vals) if vals else None


def _effective_weekly_reset(windows: Iterable[UsageWindow], now: datetime) -> datetime | None:
    resets = [
        w.resets_at
        for w in _weekly_windows(windows)
        if w.resets_at is not None and w.resets_at > now
    ]
    return min(resets) if resets else None


def _bottleneck_remaining(windows: Iterable[UsageWindow]) -> float:
    applicable = _applicable_opus_windows(windows)
    if not applicable:
        return -1.0
    return min(float(w.remaining_percent) for w in applicable)


def evaluate_provider(
    spec: ProviderSpec,
    snapshot: UsageSnapshot | None,
    now: datetime,
    ttl_seconds: int,
    error: ProviderError | None = None,
) -> ProviderReport:
    if snapshot is None:
        warnings = ("no usage snapshot available",)
        return ProviderReport(
            spec=spec,
            snapshot=None,
            status="unknown",
            freshness="unavailable",
            age_seconds=None,
            warnings=warnings,
            error=error,
        )

    age_seconds = max(0, int((now - snapshot.checked_at).total_seconds()))
    stale_needed, stale_reason = needs_refresh(snapshot, now, ttl_seconds)
    freshness = "stale" if stale_needed else "fresh"

    warnings: list[str] = []
    if stale_reason == "expired_ttl":
        warnings.append(f"snapshot is {format_duration(age_seconds)} old (TTL {ttl_seconds}s)")
    elif stale_reason == "window_reset_passed":
        warnings.append("a quota window reset passed since the last check")

    applicable = (
        _applicable_opus_windows(snapshot.windows)
        if spec.driver == CLAUDE_DRIVER
        else list(snapshot.windows)
    )
    if not applicable:
        warnings.append("snapshot contains no applicable quota windows")
        return ProviderReport(
            spec=spec,
            snapshot=snapshot,
            status="unknown",
            freshness=freshness,
            age_seconds=age_seconds,
            warnings=tuple(warnings),
            error=error,
        )

    # A window at 0% remaining whose reset is still in the future remains exhausted even if TTL elapsed.
    for w in applicable:
        if float(w.remaining_percent) <= 0.0:
            if w.resets_at is not None and w.resets_at > now:
                return ProviderReport(
                    spec=spec,
                    snapshot=snapshot,
                    status="exhausted",
                    freshness=freshness,
                    age_seconds=age_seconds,
                    warnings=tuple(warnings),
                    error=error,
                )
            if w.resets_at is None and freshness == "fresh":
                return ProviderReport(
                    spec=spec,
                    snapshot=snapshot,
                    status="exhausted",
                    freshness=freshness,
                    age_seconds=age_seconds,
                    warnings=tuple(warnings),
                    error=error,
                )

    if freshness != "fresh":
        return ProviderReport(
            spec=spec,
            snapshot=snapshot,
            status="unknown",
            freshness=freshness,
            age_seconds=age_seconds,
            warnings=tuple(warnings),
            error=error,
        )

    if spec.driver == CLAUDE_DRIVER:
        five_h = _find_window(applicable, "five_hour")
        weekly_rem = _effective_weekly_remaining(applicable)
        below_5h = five_h is not None and float(five_h.remaining_percent) < FIVE_HOUR_FLOOR_PERCENT
        below_7d = weekly_rem is not None and weekly_rem < WEEKLY_FLOOR_PERCENT
        if below_5h:
            warnings.append(f"5h remaining ({five_h.remaining_percent}%) is below {int(FIVE_HOUR_FLOOR_PERCENT)}% safety floor")
        if below_7d:
            warnings.append(f"weekly remaining ({weekly_rem:g}%) is below {int(WEEKLY_FLOOR_PERCENT)}% safety floor")
        if below_5h or below_7d:
            return ProviderReport(
                spec=spec,
                snapshot=snapshot,
                status="low_headroom",
                freshness=freshness,
                age_seconds=age_seconds,
                warnings=tuple(warnings),
                error=error,
            )

    return ProviderReport(
        spec=spec,
        snapshot=snapshot,
        status="eligible",
        freshness=freshness,
        age_seconds=age_seconds,
        warnings=tuple(warnings),
        error=error,
    )


def _fmt_pct(val: float | int | None) -> str:
    if val is None:
        return "?"
    return f"{val:g}%"


def _describe_exhausted(reports: list[ProviderReport], now: datetime) -> str:
    parts: list[str] = []
    for r in reports:
        if r.snapshot is None:
            continue
        for w in _applicable_opus_windows(r.snapshot.windows):
            if float(w.remaining_percent) <= 0.0 and (w.resets_at is None or w.resets_at > now):
                when = f"resets in {format_duration((w.resets_at - now).total_seconds())}" if w.resets_at else "reset unknown"
                parts.append(f"{r.spec.instance_id} {w.id} is exhausted ({when})")
                break
    return "; ".join(parts)


def recommend_opus(
    reports: list[ProviderReport],
    now: datetime,
) -> tuple[Recommendation | None, str]:
    opus = [r for r in reports if r.spec.driver == CLAUDE_DRIVER]
    if not opus:
        return None, "no enabled Claude Opus provider instances found"

    eligible = [r for r in opus if r.status == "eligible" and r.snapshot is not None]
    low_headroom = [r for r in opus if r.status == "low_headroom" and r.snapshot is not None]
    exhausted = [r for r in opus if r.status == "exhausted"]
    unknown = [r for r in opus if r.status == "unknown"]

    far_future = datetime(9999, 12, 31, tzinfo=timezone.utc)

    def eligible_sort_key(r: ProviderReport) -> tuple[int, datetime, float, float, str]:
        assert r.snapshot is not None
        wk_reset = _effective_weekly_reset(r.snapshot.windows, now)
        has_active_weekly = 0 if wk_reset is not None else 1
        five_h = _find_window(r.snapshot.windows, "five_hour")
        five_h_rem = float(five_h.remaining_percent) if five_h is not None else 100.0
        wk_rem = _effective_weekly_remaining(r.snapshot.windows)
        wk_rem_val = wk_rem if wk_rem is not None else 100.0
        return (has_active_weekly, wk_reset or far_future, -five_h_rem, -wk_rem_val, r.spec.instance_id)

    if eligible:
        ranked = sorted(eligible, key=eligible_sort_key)
        winner = ranked[0]
        assert winner.snapshot is not None
        w_five = _find_window(winner.snapshot.windows, "five_hour")
        w_wk_rem = _effective_weekly_remaining(winner.snapshot.windows)
        w_wk_reset = _effective_weekly_reset(winner.snapshot.windows, now)

        if len(ranked) == 1:
            others: list[str] = []
            ex_desc = _describe_exhausted(exhausted, now)
            if ex_desc:
                others.append(ex_desc)
            for r in low_headroom:
                others.append(f"{r.spec.instance_id} is below safety floor")
            for r in unknown:
                others.append(f"{r.spec.instance_id} status is unknown ({r.freshness})")
            suffix = f"; {'; '.join(others)}" if others else ""
            reason = (
                f"only eligible Opus instance ({_fmt_pct(w_five.remaining_percent if w_five else None)} 5h, "
                f"{_fmt_pct(w_wk_rem)} 7d remaining){suffix}"
            )
        else:
            runner = ranked[1]
            assert runner.snapshot is not None
            r_wk_reset = _effective_weekly_reset(runner.snapshot.windows, now)
            if w_wk_reset is not None and r_wk_reset is None:
                reason = (
                    f"active weekly window resets in {format_duration((w_wk_reset - now).total_seconds())} "
                    f"while {runner.spec.instance_id} weekly clock has not started "
                    f"({_fmt_pct(w_five.remaining_percent if w_five else None)} 5h, {_fmt_pct(w_wk_rem)} 7d remaining)"
                )
            elif w_wk_reset is not None and r_wk_reset is not None and w_wk_reset < r_wk_reset:
                reason = (
                    f"weekly quota resets sooner ({format_duration((w_wk_reset - now).total_seconds())} vs "
                    f"{format_duration((r_wk_reset - now).total_seconds())} on {runner.spec.instance_id}) "
                    f"with {_fmt_pct(w_five.remaining_percent if w_five else None)} 5h and {_fmt_pct(w_wk_rem)} 7d remaining"
                )
            else:
                r_five = _find_window(runner.snapshot.windows, "five_hour")
                reason = (
                    f"more headroom on tie-break ({_fmt_pct(w_five.remaining_percent if w_five else None)} 5h vs "
                    f"{_fmt_pct(r_five.remaining_percent if r_five else None)} on {runner.spec.instance_id})"
                )

        return (
            Recommendation(
                provider_instance_id=winner.spec.instance_id,
                display_name=winner.spec.display_name,
                model=winner.spec.model,
                low_headroom=False,
                reason=reason,
            ),
            reason,
        )

    if low_headroom:
        def low_sort_key(r: ProviderReport) -> tuple[float, float, int, datetime, str]:
            assert r.snapshot is not None
            bottleneck = _bottleneck_remaining(r.snapshot.windows)
            five_h = _find_window(r.snapshot.windows, "five_hour")
            five_h_rem = float(five_h.remaining_percent) if five_h is not None else 100.0
            wk_reset = _effective_weekly_reset(r.snapshot.windows, now)
            return (-bottleneck, -five_h_rem, 0 if wk_reset else 1, wk_reset or far_future, r.spec.instance_id)

        winner = sorted(low_headroom, key=low_sort_key)[0]
        assert winner.snapshot is not None
        w_five = _find_window(winner.snapshot.windows, "five_hour")
        w_wk_rem = _effective_weekly_remaining(winner.snapshot.windows)
        reason = (
            f"low-headroom warning: all usable Opus instances are below safety floor; "
            f"{winner.spec.instance_id} has highest bottleneck headroom "
            f"({_fmt_pct(w_five.remaining_percent if w_five else None)} 5h, {_fmt_pct(w_wk_rem)} 7d remaining)"
        )
        return (
            Recommendation(
                provider_instance_id=winner.spec.instance_id,
                display_name=winner.spec.display_name,
                model=winner.spec.model,
                low_headroom=True,
                reason=reason,
            ),
            reason,
        )

    if exhausted and not unknown:
        ex_desc = _describe_exhausted(exhausted, now)
        return None, f"all Opus instances are exhausted ({ex_desc})"
    if unknown and not exhausted:
        return None, "no fresh Opus usage data available; inspect provider errors"
    ex_desc = _describe_exhausted(exhausted, now)
    unk_ids = ", ".join(r.spec.instance_id for r in unknown)
    return None, f"no eligible Opus instance ({ex_desc}; unknown status on {unk_ids})"
