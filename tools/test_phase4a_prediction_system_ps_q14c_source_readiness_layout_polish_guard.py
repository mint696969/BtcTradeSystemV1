# path: ./tools/test_phase4a_prediction_system_ps_q14c_source_readiness_layout_polish_guard.py
# desc: Guard for PS-Q14C compact display layout for WarRoom source-readiness explanations.

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_review_panel import (  # noqa: E402
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_LAYOUT_POLISH_VERSION,
    build_prediction_warroom_latest_prediction_source_review_panel_packet,
    latest_prediction_source_readiness_explanation_display_rows,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py"
GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q14c_source_readiness_layout_polish_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py",
    "tools/test_phase4a_prediction_system_ps_q14c_source_readiness_layout_polish_guard.py",
}
REQUIRED_PANEL_MARKERS = (
    "PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_LAYOUT_POLISH_VERSION",
    "prediction_warroom_latest_prediction_source_readiness_layout_polish.ps_q14c.v1",
    "latest_prediction_source_readiness_explanation_display_rows",
    "readiness_explanation_display_rows",
    "safe_flags",
    "PS-Q14C source-readiness layout polish",
    "important columns stay left",
    "does not change readiness or bypass blockers",
)
REQUIRED_TEST_MARKERS = (
    "PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_LAYOUT_POLISH_VERSION",
    "latest_prediction_source_readiness_explanation_display_rows",
    "readiness_explanation_display_rows",
    "safe_flags",
    "no_bypass",
    "no_warroom_fix",
)
FORBIDDEN_TRUE_TOKENS = (
    "can_fix_in_warroom=True",
    "can_fix_in_warroom = True",
    "bypass_allowed=True",
    "bypass_allowed = True",
    "runtime_artifact_write_allowed=True",
    "ledger_append_allowed=True",
    "autotrade_trigger_allowed=True",
    "broker_private_api_allowed=True",
    "would_send_to_broker=True",
    "would_write_runtime_artifact=True",
    "mode_apply_requested=True",
    "approval_append_requested=True",
    "authorization_grant_requested=True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def main() -> int:
    failures: list[str] = []
    for path in (PANEL, TEST, GUARD):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
    panel_text = _read(PANEL) if PANEL.exists() else ""
    test_text = _read(TEST) if TEST.exists() else ""
    for marker in REQUIRED_PANEL_MARKERS:
        if marker not in panel_text:
            failures.append(f"missing panel marker: {marker}")
    for marker in REQUIRED_TEST_MARKERS:
        if marker not in test_text:
            failures.append(f"missing test marker: {marker}")
    for token in FORBIDDEN_TRUE_TOKENS:
        if token in panel_text or token in test_text:
            failures.append(f"forbidden true token present: {token}")
    if PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_LAYOUT_POLISH_VERSION != "prediction_warroom_latest_prediction_source_readiness_layout_polish.ps_q14c.v1":
        failures.append("layout polish version mismatch")

    sample_rows = [
        {
            "severity": "blocker",
            "category": "freshness_guard",
            "reason": "freshness_status_stale_before_actual_read",
            "human_explanation_ja": "推論ソースの鮮度確認で止まっています。freshness bypass はしません。",
            "next_check_ja": "生成時刻と鮮度判定を見る。",
            "can_fix_in_warroom": False,
            "bypass_allowed": False,
            "read_only": True,
            "execution": "false",
        }
    ]
    display_rows = latest_prediction_source_readiness_explanation_display_rows(sample_rows)
    expected_keys = ["severity", "category", "reason", "explanation_ja", "next_check_ja", "safe_flags"]
    if list(display_rows[0]) != expected_keys:
        failures.append(f"display row key order mismatch: {list(display_rows[0])}")
    if "can_fix_in_warroom" in display_rows[0] or "bypass_allowed" in display_rows[0]:
        failures.append("display row must not expose wide boolean columns")
    for flag in ("read_only", "no_exec", "no_warroom_fix", "no_bypass"):
        if flag not in display_rows[0].get("safe_flags", ""):
            failures.append(f"missing safe flag: {flag}")

    blocked_panel = build_prediction_warroom_latest_prediction_source_review_panel_packet(
        session_state={},
        allow_actual_read=False,
        store_in_session_state=False,
    )
    if blocked_panel.get("readiness_layout_polish_version") != PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_READINESS_LAYOUT_POLISH_VERSION:
        failures.append("panel missing readiness_layout_polish_version")
    if len(blocked_panel.get("readiness_explanation_display_rows", [])) != len(blocked_panel.get("readiness_explanation_rows", [])):
        failures.append("display/raw explanation row count mismatch")
    if blocked_panel.get("uicheck_snapshot", {}).get("readiness_explanation_row_count") != len(blocked_panel.get("readiness_explanation_rows", [])):
        failures.append("UI Check snapshot must keep raw readiness_explanation_row_count")
    for key in (
        "warroom_page_mutation_allowed",
        "warroom_panel_mutation_allowed",
        "runtime_artifact_write_allowed",
        "ledger_append_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_write_runtime_artifact",
        "would_write_collector_state",
        "would_send_to_broker",
        "broker_execution_requested",
        "mode_apply_requested",
        "command_ledger_append_requested",
        "approval_append_requested",
        "authorization_grant_requested",
        "autotrade_trigger_enabled",
    ):
        if blocked_panel.get(key) is not False:
            failures.append(f"panel {key} must remain false")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")
    payload = {
        "ok": not failures,
        "guard": "ps_q14c_source_readiness_layout_polish",
        "phase": "phase3_prediction_system_warroom_source_readiness_layout_polish",
        "contract": {
            "display_rows_present": not failures,
            "safe_flags_compact": not failures,
            "raw_rows_preserved": not failures,
            "uicheck_snapshot_preserved": not failures,
            "no_loader_or_readiness_behavior_change": not failures,
            "no_execution_surface": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q14c_source_readiness_layout_polish_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
