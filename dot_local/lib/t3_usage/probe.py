"""Claude CLI stream-json control-protocol usage probe."""

from __future__ import annotations

import json
import os
import re
import select
import subprocess
import tempfile
import time
from typing import Any

from .models import ProviderError, ProviderSpec

DEFAULT_PROBE_TIMEOUT_SECONDS = 15.0

_RETRY_AFTER_RE = re.compile(r"retry[-_\s]?after[:=\s]+(\d+)", re.IGNORECASE)


def _classify_error(detail: str) -> ProviderError:
    lower = detail.lower()
    retry_match = _RETRY_AFTER_RE.search(detail)
    retry_after = int(retry_match.group(1)) if retry_match else None

    if "429" in lower or "rate_limit" in lower or "throttl" in lower or "too many requests" in lower:
        return ProviderError(
            code="lookup_throttled",
            message="Claude usage lookup was throttled (429).",
            retry_after_seconds=retry_after,
        )
    if "401" in lower or "unauthorized" in lower or "not logged in" in lower or "authentication" in lower:
        return ProviderError(
            code="auth_error",
            message="Claude usage lookup failed authentication; re-authenticate this provider in T3 Code.",
        )
    compact = " ".join(detail.strip().split())
    if len(compact) > 200:
        compact = compact[:197] + "..."
    return ProviderError(
        code="probe_failed",
        message=compact or "Claude usage probe failed.",
    )


def _read_line_with_deadline(proc: subprocess.Popen[bytes], deadline: float) -> str | None:
    assert proc.stdout is not None
    fd = proc.stdout.fileno()
    buf = bytearray()
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("Claude usage probe timed out.")
        ready, _, _ = select.select([fd], [], [], min(0.25, remaining))
        if not ready:
            if proc.poll() is not None:
                chunk = os.read(fd, 4096)
                if chunk:
                    buf.extend(chunk)
                return buf.decode("utf-8", errors="replace") if buf else None
            continue
        ch = os.read(fd, 1)
        if not ch:
            return buf.decode("utf-8", errors="replace") if buf else None
        buf.extend(ch)
        if ch == b"\n":
            return buf.decode("utf-8", errors="replace")


def probe_claude_usage(
    spec: ProviderSpec,
    timeout_seconds: float = DEFAULT_PROBE_TIMEOUT_SECONDS,
) -> tuple[dict[str, Any] | None, ProviderError | None]:
    """Run Claude's initialize + get_usage control requests without reading credentials."""
    binary = spec.binary_path or "claude"
    env = os.environ.copy()
    if spec.home_path:
        env["CLAUDE_CONFIG_DIR"] = spec.home_path
    else:
        env.pop("CLAUDE_CONFIG_DIR", None)

    cmd = [
        binary,
        "--output-format",
        "stream-json",
        "--verbose",
        "--input-format",
        "stream-json",
        "--no-session-persistence",
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False,
            cwd=tempfile.gettempdir(),
            env=env,
        )
    except FileNotFoundError:
        return None, ProviderError("binary_not_found", f"Claude binary not found: {binary}")
    except OSError as exc:
        return None, ProviderError("probe_spawn_failed", f"Failed to launch {binary}: {exc}")

    deadline = time.monotonic() + timeout_seconds
    assert proc.stdin is not None
    assert proc.stdout is not None

    def send_request(request_id: str, request_body: dict[str, Any]) -> None:
        assert proc.stdin is not None
        payload = {
            "type": "control_request",
            "request_id": request_id,
            "request": request_body,
        }
        proc.stdin.write((json.dumps(payload) + "\n").encode("utf-8"))
        proc.stdin.flush()

    def read_stderr() -> str:
        if proc.stderr is None:
            return ""
        try:
            return proc.stderr.read().decode("utf-8", errors="replace")
        except OSError:
            return ""

    try:
        send_request("init-1", {"subtype": "initialize"})
        usage_requested = False

        while True:
            line = _read_line_with_deadline(proc, deadline)
            if line is None:
                return None, _classify_error(read_stderr() or "Claude probe exited before returning usage.")
            stripped = line.strip()
            if not stripped:
                continue
            try:
                msg = json.loads(stripped)
            except json.JSONDecodeError:
                continue
            if not isinstance(msg, dict) or msg.get("type") != "control_response":
                continue

            resp_outer = msg.get("response")
            if not isinstance(resp_outer, dict):
                continue
            req_id = resp_outer.get("request_id")
            subtype = resp_outer.get("subtype")

            if req_id == "init-1" and not usage_requested:
                if subtype == "error":
                    return None, _classify_error(str(resp_outer.get("error") or "initialize failed"))
                usage_requested = True
                send_request("usage-1", {"subtype": "get_usage", "skip_behaviors": True})
            elif req_id == "usage-1":
                if subtype == "error":
                    return None, _classify_error(str(resp_outer.get("error") or "get_usage failed"))
                resp_body = resp_outer.get("response")
                if not isinstance(resp_body, dict):
                    return None, ProviderError("invalid_probe_response", "Claude get_usage response was not an object.")
                return resp_body, None
    except TimeoutError:
        return None, ProviderError("probe_timeout", f"Claude usage probe timed out after {timeout_seconds:g}s.")
    except BrokenPipeError:
        return None, _classify_error(read_stderr() or "Claude probe closed stdin unexpectedly.")
    finally:
        try:
            if proc.stdin and not proc.stdin.closed:
                proc.stdin.close()
        except OSError:
            pass
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2.0)
