# path: ./tools/test_phase4a_prediction_system_ps_q18av_observation_quick_status_manual_ui_smoke_packet_guard.py
# desc: Focused guard for PS-Q18AV manual UI smoke packet.

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.test_phase4a_prediction_system_ps_q18av_observation_quick_status_manual_ui_smoke_packet import (  # noqa: E402
    FALSE_BOUNDARIES,
    MANUAL_CHECKS,
    build_ps_q18av_observation_quick_status_manual_ui_smoke_packet,
)

DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q18AV_WARROOM_OBSERVATION_QUICK_STATUS_MANUAL_UI_SMOKE_PACKET_2026-06-24.md"
UNIT = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q18av_observation_quick_status_manual_ui_smoke_packet.py"
EXPECTED_DIRTY = {
    "docs/strategy/PREDICTION_SYSTEM_PS_Q18AV_WARROOM_OBSERVATION_QUICK_STATUS_MANUAL_UI_SMOKE_PACKET_2026-06-24.md",
    "tools/test_phase4a_prediction_system_ps_q18av_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q18av_observation_quick_status_manual_ui_smoke_packet.py",
    "tools/test_phase4a_prediction_system_ps_q18av_observation_quick_status_manual_ui_smoke_packet_guard.py",
}


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    return {line[3:].replace(chr(92), "/") for line in proc.stdout.splitlines() if line.strip() and "/__pycache__/" not in line and not line.endswith(".pyc")}


def main_guard() -> int:
    failures: list[str] = []
    for path in (UNIT,):
        try:
            ast.parse(_read(path), filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    packet = build_ps_q18av_observation_quick_status_manual_ui_smoke_packet()
    if packet.get("manual_ui_smoke_expected_result") != "pass_if_all_checks_true":
        failures.append("manual UI smoke expected result mismatch")
    if packet.get("manual_check_count") != len(MANUAL_CHECKS):
        failures.append("manual check count mismatch")
    for token in ("PS_Q18AU_OBSERVATION_QUICK_STATUS", "latest_prediction_observation_status", "implementation_gate=blocked_not_ready_to_enable", "real_render=false", "component_runtime_binding=false", "autotrade=false", "broker=false"):
        if token not in packet.get("required_browser_find_tokens", []):
            failures.append(f"missing required browser find token: {token}")
    for key in FALSE_BOUNDARIES:
        if packet.get(key) is not False:
            failures.append(f"{key} must stay false")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in (
        "PS-Q18AV",
        "PS_Q18AU_OBSERVATION_QUICK_STATUS",
        "manual_ui_smoke_expected_result=pass_if_all_checks_true",
        "refresh_heartbeat_utc value advances",
        "broker_private_api_allowed=false",
    ):
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    dirty = _dirty_paths()
    unexpected = dirty - EXPECTED_DIRTY
    missing = EXPECTED_DIRTY - dirty
    if unexpected:
        failures.append(f"unexpected dirty paths: {sorted(unexpected)}")
    if missing:
        failures.append(f"missing expected dirty paths: {sorted(missing)}")
    result = {
        "ok": not failures,
        "guard": "ps_q18av_observation_quick_status_manual_ui_smoke_packet_guard",
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected),
        "missing_dirty": sorted(missing),
        "failures": failures,
        "manual_ui_smoke_expected_result": packet.get("manual_ui_smoke_expected_result"),
        "manual_check_count": packet.get("manual_check_count"),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q18av_observation_quick_status_manual_ui_smoke_packet_guard() -> None:
    assert main_guard() == 0


if __name__ == "__main__":
    raise SystemExit(main_guard())
