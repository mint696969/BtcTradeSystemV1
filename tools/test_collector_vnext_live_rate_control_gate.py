# path: ./tools/test_collector_vnext_live_rate_control_gate.py
# desc: Observe collector_vnext rate_state visibility and judge whether live REST rate control behavior looks operationally safe.

from __future__ import annotations

from _btcts_bootstrap import ensure_btcts_on_syspath
ensure_btcts_on_syspath()

import json
import os
import time
from collections import Counter
from pathlib import Path

from btcts.collector_vnext.config import load_config


def _env_float(name: str, default: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        return float(raw)
    except Exception:
        return default


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _rate_state_path() -> Path:
    cfg = load_config()
    return Path(cfg.roots()["state"]) / "rate_state.json"


def main() -> int:
    observe_seconds = _env_float("BTCTS_RATE_GATE_SECONDS", 120.0)
    poll_sec = _env_float("BTCTS_RATE_GATE_POLL_SEC", 2.0)
    max_wait_ms_warn = _env_float("BTCTS_RATE_GATE_MAX_WAIT_MS_WARN", 5000.0)

    started = time.monotonic()
    path = _rate_state_path()

    sample_count = 0
    summary_state_counts = Counter()
    recovery_phase_counts = Counter()
    engaged_true_count = 0
    last_item = {}

    while (time.monotonic() - started) < observe_seconds:
        snap = _read_json(path)
        items = snap.get("items") if isinstance(snap, dict) else {}
        bitflyer = items.get("bitflyer") if isinstance(items, dict) else {}
        if isinstance(bitflyer, dict) and bitflyer:
            sample_count += 1
            summary_state_counts[str(bitflyer.get("summary_state") or "missing")] += 1
            recovery_phase_counts[str(bitflyer.get("recovery_phase") or "missing")] += 1
            if bool(bitflyer.get("engaged", False)):
                engaged_true_count += 1
            last_item = bitflyer
        time.sleep(poll_sec)

    wait_ms = float(last_item.get("wait_ms") or 0.0) if last_item else 0.0
    util_ratio = float(last_item.get("util_ratio") or 0.0) if last_item else 0.0
    summary_state = str(last_item.get("summary_state") or "") if last_item else ""
    recovery_phase = str(last_item.get("recovery_phase") or "") if last_item else ""

    checks = {
        "rate_state_visible": sample_count > 0,
        "summary_state_visible": bool(summary_state_counts),
        "recovery_phase_visible": bool(recovery_phase_counts),
        "last_summary_state_known": summary_state in {"NORMAL", "WARN", "CRIT"},
        "last_recovery_phase_known": bool(recovery_phase),
        "last_wait_ms_not_excessive": wait_ms <= max_wait_ms_warn,
        "last_util_ratio_bounded": 0.0 <= util_ratio <= 1.0,
    }

    ok = all(checks.values())

    report = {
        "ok": ok,
        "gate_type": "live_rest_rate_control_visibility",
        "observe_seconds": observe_seconds,
        "poll_sec": poll_sec,
        "rate_state_path": str(path),
        "sample_count": sample_count,
        "summary_state_counts": dict(summary_state_counts),
        "recovery_phase_counts": dict(recovery_phase_counts),
        "engaged_true_count": engaged_true_count,
        "last_item": last_item,
        "checks": checks,
        "operator_note": (
            "rate_control_visibility_looks_usable" if ok else "needs_rate_control_investigation"
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())