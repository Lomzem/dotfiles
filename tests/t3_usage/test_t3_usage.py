"""Behavior tests for t3-usage."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import time
import unittest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "dot_local" / "lib"))

from t3_usage.cli import collect_report, format_text_report
from t3_usage.models import ProviderError, ProviderSpec, format_iso_utc

NOW = datetime(2026, 11, 25, 22, 0, 0, tzinfo=timezone.utc)


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def _make_t3_env(
    root: Path,
    *,
    claude_agent_cache: dict | None = None,
    claude_team_cache: dict | None = None,
    extra_providers: dict | None = None,
    binary_path: str = "claude",
) -> tuple[Path, Path]:
    t3_dir = root / ".t3"
    cache_dir = root / ".cache" / "t3-usage"
    team_home = str(root / ".claude_team")

    instances: dict = {
        "claudeAgent": {
            "driver": "claudeAgent",
            "enabled": True,
            "displayName": None,
            "config": {"binaryPath": binary_path, "homePath": ""},
        },
        "claudeTeam": {
            "driver": "claudeAgent",
            "enabled": True,
            "displayName": "AJA",
            "config": {"binaryPath": binary_path, "homePath": team_home},
        },
    }
    if extra_providers:
        instances.update(extra_providers)

    _write_json(t3_dir / "userdata" / "settings.json", {"providerInstances": instances})

    if claude_agent_cache is not None:
        _write_json(t3_dir / "caches" / "claudeAgent.json", claude_agent_cache)
    if claude_team_cache is not None:
        _write_json(t3_dir / "caches" / "claudeTeam.json", claude_team_cache)
    return t3_dir, cache_dir


def _cache_doc(
    instance_id: str,
    display_name: str,
    *,
    checked_at: datetime,
    five_used: float,
    five_reset: datetime | None,
    seven_used: float,
    seven_reset: datetime | None,
    opus_seven_used: float | None = None,
    opus_seven_reset: datetime | None = None,
    driver: str = "claudeAgent",
) -> dict:
    windows = [
        {
            "id": "five_hour",
            "kind": "session",
            "label": "Session",
            "windowDurationMins": 300,
            "usedPercent": five_used,
            **({"resetsAt": format_iso_utc(five_reset)} if five_reset else {}),
        },
        {
            "id": "seven_day",
            "kind": "weekly",
            "label": "Weekly",
            "windowDurationMins": 10080,
            "usedPercent": seven_used,
            **({"resetsAt": format_iso_utc(seven_reset)} if seven_reset else {}),
        },
    ]
    if opus_seven_used is not None:
        windows.append(
            {
                "id": "seven_day_opus",
                "kind": "weekly",
                "label": "Opus Weekly",
                "windowDurationMins": 10080,
                "usedPercent": opus_seven_used,
                "modelScope": "opus",
                **({"resetsAt": format_iso_utc(opus_seven_reset)} if opus_seven_reset else {}),
            }
        )
    return {
        "instanceId": instance_id,
        "driver": driver,
        "displayName": display_name,
        "enabled": True,
        "models": [{"slug": "claude-opus-5-5", "isDefault": True}],
        "usageLimits": {
            "checkedAt": format_iso_utc(checked_at),
            "windows": windows,
            "resetCredits": {"availableCount": 1, "nextExpiresAt": "2026-12-10T22:00:00Z"},
        },
    }


def _probe_payload(five_used: float, five_reset: datetime | None, seven_used: float, seven_reset: datetime | None) -> dict:
    return {
        "rate_limits_available": True,
        "rate_limits": {
            "five_hour": {
                "utilization": five_used,
                "resets_at": format_iso_utc(five_reset),
            },
            "seven_day": {
                "utilization": seven_used,
                "resets_at": format_iso_utc(seven_reset),
            },
            "seven_day_opus": None,
        },
    }


class TestOpusRoutingPolicy(unittest.TestCase):
    def test_case_a_prefers_earlier_weekly_reset_and_reports_remaining_percent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            t3_dir, cache_dir = _make_t3_env(
                root,
                claude_agent_cache=_cache_doc(
                    "claudeAgent",
                    "Claude",
                    checked_at=NOW - timedelta(seconds=30),
                    five_used=0,
                    five_reset=None,
                    seven_used=2,
                    seven_reset=NOW + timedelta(days=6),
                ),
                claude_team_cache=_cache_doc(
                    "claudeTeam",
                    "AJA",
                    checked_at=NOW - timedelta(seconds=20),
                    five_used=10,
                    five_reset=NOW + timedelta(hours=4),
                    seven_used=40,
                    seven_reset=NOW + timedelta(hours=8),
                ),
            )
            probe_calls: list[str] = []

            def fail_if_called(spec: ProviderSpec, _timeout: float):
                probe_calls.append(spec.instance_id)
                raise AssertionError("fresh cache should not invoke probe")

            report = collect_report(t3_dir=t3_dir, cache_dir=cache_dir, now=NOW, probe_fn=fail_if_called)

            self.assertEqual(probe_calls, [])
            self.assertEqual(report["recommended"]["providerInstanceId"], "claudeTeam")
            self.assertEqual(report["recommended"]["model"], "claude-opus-5-5")
            self.assertFalse(report["recommended"]["lowHeadroom"])

            by_id = {p["providerInstanceId"]: p for p in report["providers"]}
            team_wins = {w["id"]: w for w in by_id["claudeTeam"]["windows"]}
            self.assertEqual(team_wins["five_hour"]["remainingPercent"], 90)
            self.assertEqual(team_wins["seven_day"]["remainingPercent"], 60)
            self.assertNotIn("usedPercent", team_wins["five_hour"])

    def test_case_b_and_c_safety_floors_protect_low_headroom_instances(self) -> None:
        for label, team_5h_used, team_7d_used in (
            ("5h_below_15_remaining", 90, 50),
            ("7d_below_10_remaining", 10, 95),
        ):
            with self.subTest(label):
                with tempfile.TemporaryDirectory() as tmp:
                    t3_dir, cache_dir = _make_t3_env(
                        Path(tmp),
                        claude_agent_cache=_cache_doc(
                            "claudeAgent",
                            "Claude",
                            checked_at=NOW - timedelta(seconds=10),
                            five_used=5,
                            five_reset=NOW + timedelta(hours=5),
                            seven_used=10,
                            seven_reset=NOW + timedelta(days=6),
                        ),
                        claude_team_cache=_cache_doc(
                            "claudeTeam",
                            "AJA",
                            checked_at=NOW - timedelta(seconds=10),
                            five_used=team_5h_used,
                            five_reset=NOW + timedelta(hours=3),
                            seven_used=team_7d_used,
                            seven_reset=NOW + timedelta(days=1),
                        ),
                    )
                    report = collect_report(t3_dir=t3_dir, cache_dir=cache_dir, now=NOW, no_refresh=True)
                    self.assertEqual(report["recommended"]["providerInstanceId"], "claudeAgent")
                    by_id = {p["providerInstanceId"]: p for p in report["providers"]}
                    self.assertEqual(by_id["claudeTeam"]["status"], "low_headroom")

    def test_case_d_active_ticking_weekly_window_beats_unstarted_weekly_window(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t3_dir, cache_dir = _make_t3_env(
                Path(tmp),
                claude_agent_cache=_cache_doc(
                    "claudeAgent",
                    "Claude",
                    checked_at=NOW - timedelta(seconds=10),
                    five_used=0,
                    five_reset=None,
                    seven_used=0,
                    seven_reset=None,
                ),
                claude_team_cache=_cache_doc(
                    "claudeTeam",
                    "AJA",
                    checked_at=NOW - timedelta(seconds=10),
                    five_used=20,
                    five_reset=NOW + timedelta(hours=4),
                    seven_used=30,
                    seven_reset=NOW + timedelta(days=3),
                ),
            )
            report = collect_report(t3_dir=t3_dir, cache_dir=cache_dir, now=NOW, no_refresh=True)
            self.assertEqual(report["recommended"]["providerInstanceId"], "claudeTeam")
            self.assertIn("not started", report["recommended"]["reason"])

    def test_both_below_floor_warns_and_picks_higher_bottleneck(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t3_dir, cache_dir = _make_t3_env(
                Path(tmp),
                claude_agent_cache=_cache_doc(
                    "claudeAgent",
                    "Claude",
                    checked_at=NOW - timedelta(seconds=10),
                    five_used=88,  # 12% remaining
                    five_reset=NOW + timedelta(hours=2),
                    seven_used=20,
                    seven_reset=NOW + timedelta(days=5),
                ),
                claude_team_cache=_cache_doc(
                    "claudeTeam",
                    "AJA",
                    checked_at=NOW - timedelta(seconds=10),
                    five_used=94,  # 6% remaining
                    five_reset=NOW + timedelta(hours=2),
                    seven_used=20,
                    seven_reset=NOW + timedelta(days=1),
                ),
            )
            report = collect_report(t3_dir=t3_dir, cache_dir=cache_dir, now=NOW, no_refresh=True)
            self.assertEqual(report["recommended"]["providerInstanceId"], "claudeAgent")
            self.assertTrue(report["recommended"]["lowHeadroom"])
            self.assertIn("low-headroom", report["recommended"]["reason"])

    def test_exhausted_instance_excluded_and_all_exhausted_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t3_dir, cache_dir = _make_t3_env(
                Path(tmp),
                claude_agent_cache=_cache_doc(
                    "claudeAgent",
                    "Claude",
                    checked_at=NOW - timedelta(seconds=10),
                    five_used=100,
                    five_reset=NOW + timedelta(hours=2),
                    seven_used=2,
                    seven_reset=NOW + timedelta(days=6),
                ),
                claude_team_cache=_cache_doc(
                    "claudeTeam",
                    "AJA",
                    checked_at=NOW - timedelta(seconds=10),
                    five_used=20,
                    five_reset=NOW + timedelta(hours=2),
                    seven_used=10,
                    seven_reset=NOW + timedelta(days=5),
                    opus_seven_used=100,
                    opus_seven_reset=NOW + timedelta(days=2),
                ),
            )
            report = collect_report(t3_dir=t3_dir, cache_dir=cache_dir, now=NOW, no_refresh=True)
            self.assertIsNone(report["recommended"])
            self.assertIn("exhausted", report["recommendationReason"])
            by_id = {p["providerInstanceId"]: p for p in report["providers"]}
            self.assertEqual(by_id["claudeAgent"]["status"], "exhausted")
            self.assertEqual(by_id["claudeTeam"]["status"], "exhausted")


class TestDeterministicRefreshAndCaching(unittest.TestCase):
    def test_passed_reset_triggers_refresh_even_within_ttl_and_avoids_false_exhausted_on_failure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t3_dir, cache_dir = _make_t3_env(
                Path(tmp),
                claude_agent_cache=_cache_doc(
                    "claudeAgent",
                    "Claude",
                    checked_at=NOW - timedelta(seconds=90),
                    five_used=100,
                    five_reset=NOW - timedelta(seconds=10),  # reset just passed!
                    seven_used=2,
                    seven_reset=NOW + timedelta(days=6),
                ),
                claude_team_cache=_cache_doc(
                    "claudeTeam",
                    "AJA",
                    checked_at=NOW - timedelta(seconds=30),
                    five_used=10,
                    five_reset=NOW + timedelta(hours=4),
                    seven_used=15,
                    seven_reset=NOW + timedelta(days=5),
                ),
            )
            probed: list[str] = []

            def failing_probe(spec: ProviderSpec, _timeout: float):
                probed.append(spec.instance_id)
                return None, ProviderError("lookup_throttled", "429 throttled", retry_after_seconds=120)

            report = collect_report(t3_dir=t3_dir, cache_dir=cache_dir, now=NOW, probe_fn=failing_probe)
            self.assertEqual(probed, ["claudeAgent"])
            self.assertEqual(report["recommended"]["providerInstanceId"], "claudeTeam")

            by_id = {p["providerInstanceId"]: p for p in report["providers"]}
            agent = by_id["claudeAgent"]
            self.assertEqual(agent["status"], "unknown")
            self.assertEqual(agent["freshness"], "stale")
            self.assertEqual(agent["error"]["code"], "lookup_throttled")
            five_w = {w["id"]: w for w in agent["windows"]}["five_hour"]
            self.assertTrue(five_w["resetPassed"])

            # Subsequent call during cooldown must not hammer the probe again.
            report2 = collect_report(
                t3_dir=t3_dir,
                cache_dir=cache_dir,
                now=NOW + timedelta(seconds=30),
                probe_fn=failing_probe,
            )
            self.assertEqual(probed, ["claudeAgent"])
            agent2 = {p["providerInstanceId"]: p for p in report2["providers"]}["claudeAgent"]
            self.assertIn("cooldown", agent2["error"]["message"])

    def test_concurrent_refresh_shares_one_probe_per_instance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            t3_dir, cache_dir = _make_t3_env(
                Path(tmp),
                claude_agent_cache=_cache_doc(
                    "claudeAgent",
                    "Claude",
                    checked_at=NOW - timedelta(minutes=10),
                    five_used=50,
                    five_reset=NOW + timedelta(hours=2),
                    seven_used=10,
                    seven_reset=NOW + timedelta(days=6),
                ),
                claude_team_cache=_cache_doc(
                    "claudeTeam",
                    "AJA",
                    checked_at=NOW - timedelta(seconds=10),
                    five_used=10,
                    five_reset=NOW + timedelta(hours=4),
                    seven_used=15,
                    seven_reset=NOW + timedelta(days=5),
                ),
            )
            calls: list[str] = []

            def slow_probe(spec: ProviderSpec, _timeout: float):
                calls.append(spec.instance_id)
                time.sleep(0.15)
                return _probe_payload(20, NOW + timedelta(hours=3), 10, NOW + timedelta(days=6)), None

            with ThreadPoolExecutor(max_workers=3) as pool:
                futs = [
                    pool.submit(collect_report, t3_dir=t3_dir, cache_dir=cache_dir, now=NOW, probe_fn=slow_probe)
                    for _ in range(3)
                ]
                results = [f.result() for f in futs]

            self.assertEqual(calls, ["claudeAgent"])
            for res in results:
                by_id = {p["providerInstanceId"]: p for p in res["providers"]}
                self.assertEqual(by_id["claudeAgent"]["freshness"], "fresh")
                self.assertEqual(
                    {w["id"]: w for w in by_id["claudeAgent"]["windows"]}["five_hour"]["remainingPercent"],
                    80,
                )

    def test_real_subprocess_probe_cli_and_all_flag(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            counter_file = root / "probe_calls.log"
            stub_bin = root / "fake-claude"
            stub_bin.write_text(
                f"""#!/usr/bin/env python3
import json, os, sys
cfg = os.environ.get("CLAUDE_CONFIG_DIR", "")
with open({str(counter_file)!r}, "a", encoding="utf-8") as fh:
    fh.write(cfg + "\\n")
for raw in sys.stdin:
    msg = json.loads(raw)
    req_id = msg.get("request_id")
    subtype = (msg.get("request") or {{}}).get("subtype")
    if subtype == "initialize":
        print(json.dumps({{"type": "control_response", "response": {{"subtype": "success", "request_id": req_id, "response": {{}}}}}}), flush=True)
    elif subtype == "get_usage":
        is_team = cfg.endswith(".claude_team")
        payload = {{
            "rate_limits_available": True,
            "rate_limits": {{
                "five_hour": {{"utilization": 25 if is_team else 100, "resets_at": "2099-11-26T02:10:00Z"}},
                "seven_day": {{"utilization": 12 if is_team else 2, "resets_at": "2099-12-01T19:00:00Z"}},
            }},
        }}
        print(json.dumps({{"type": "control_response", "response": {{"subtype": "success", "request_id": req_id, "response": payload}}}}), flush=True)
        break
""",
                encoding="utf-8",
            )
            stub_bin.chmod(stub_bin.stat().st_mode | stat.S_IXUSR)

            t3_dir, cache_dir = _make_t3_env(
                root,
                binary_path=str(stub_bin),
                extra_providers={
                    "codex": {
                        "driver": "codex",
                        "enabled": True,
                        "displayName": "Codex",
                        "config": {},
                    }
                },
            )
            _write_json(
                t3_dir / "caches" / "codex.json",
                _cache_doc(
                    "codex",
                    "Codex",
                    driver="codex",
                    checked_at=datetime.now(timezone.utc) - timedelta(seconds=15),
                    five_used=0,
                    five_reset=None,
                    seven_used=5,
                    seven_reset=datetime(2099, 12, 2, 0, 0, tzinfo=timezone.utc),
                ),
            )

            exe = REPO_ROOT / "dot_local" / "bin" / "executable_t3-usage"
            run1 = subprocess.run(
                [sys.executable, str(exe), "--t3-dir", str(t3_dir), "--cache-dir", str(cache_dir), "--all"],
                capture_output=True,
                text=True,
                check=True,
            )
            data1 = json.loads(run1.stdout)
            self.assertEqual(data1["recommended"]["providerInstanceId"], "claudeTeam")
            ids = [p["providerInstanceId"] for p in data1["providers"]]
            self.assertEqual(ids, ["claudeAgent", "claudeTeam", "codex"])
            by_id = {p["providerInstanceId"]: p for p in data1["providers"]}
            self.assertEqual(by_id["claudeTeam"]["source"], "claude-probe")
            self.assertEqual(by_id["claudeAgent"]["status"], "exhausted")
            self.assertEqual(by_id["codex"]["status"], "eligible")

            # Verify CLAUDE_CONFIG_DIR isolation for both instances.
            logged = sorted(counter_file.read_text(encoding="utf-8").splitlines())
            self.assertEqual(logged, ["", str(root / ".claude_team")])

            # Second run should hit tool-cache with zero new stub invocations.
            run2 = subprocess.run(
                [sys.executable, str(exe), "--t3-dir", str(t3_dir), "--cache-dir", str(cache_dir), "--text"],
                capture_output=True,
                text=True,
                check=True,
            )
            self.assertIn("RECOMMENDED: claudeTeam (AJA)", run2.stdout)
            self.assertIn("75% rem", run2.stdout)
            self.assertEqual(len(counter_file.read_text(encoding="utf-8").splitlines()), 2)

            # Text formatter handles null recommendation cleanly.
            empty_text = format_text_report({"recommended": None, "recommendationReason": "all exhausted", "providers": []})
            self.assertIn("RECOMMENDED: none - all exhausted", empty_text)


if __name__ == "__main__":
    unittest.main()
