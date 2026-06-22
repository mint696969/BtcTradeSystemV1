# path: ./tools/test_phase4a_prediction_system_ps_q12h_warroom_uicheck_snapshot_guard.py
# desc: Guard for PS-Q12H WarRoom inference GPT UI Check snapshot/check automation.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_latest_prediction_source_review_panel import (  # noqa: E402
    PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_UICHECK_SNAPSHOT_VERSION,
    build_prediction_warroom_latest_prediction_source_uicheck_snapshot,
)
from check_phase4a_prediction_system_ps_q12h_warroom_uicheck_snapshot import (  # noqa: E402
    SNAPSHOT_KEY,
    validate_warroom_inference_uicheck_snapshot_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py"
CHECK = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q12h_warroom_uicheck_snapshot.py"
GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q12h_warroom_uicheck_snapshot_guard.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_prediction_source_review_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_latest_prediction_source_review_panel.py",
    "tools/check_phase4a_prediction_system_ps_q12h_warroom_uicheck_snapshot.py",
    "tools/test_phase4a_prediction_system_ps_q12h_warroom_uicheck_snapshot_guard.py",
}
FORBIDDEN_TRUE_TOKENS = (
    "runtime_artifact_write_allowed=True",
    "runtime_artifact_write_allowed = True",
    "ledger_append_allowed=True",
    "ledger_append_allowed = True",
    "autotrade_trigger_allowed=True",
    "autotrade_trigger_allowed = True",
    "broker_private_api_allowed=True",
    "broker_private_api_allowed = True",
    "would_send_to_broker=True",
    "would_send_to_broker = True",
    "would_write_runtime_artifact=True",
    "would_write_runtime_artifact = True",
    "broker_execution_requested=True",
    "broker_execution_requested = True",
    "mode_apply_requested=True",
    "mode_apply_requested = True",
    "command_ledger_append_requested=True",
    "command_ledger_append_requested = True",
    "approval_append_requested=True",
    "approval_append_requested = True",
    "authorization_grant_requested=True",
    "authorization_grant_requested = True",
    "autotrade_trigger_enabled=True",
    "autotrade_trigger_enabled = True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _dirty_paths() -> set[str]:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    out: set[str] = set()
    for line in proc.stdout.splitlines():
        if line.strip():
            out.add(line[3:].replace(chr(92), "/"))
    return out


def _sample_panel() -> dict:
    adapter = {
        "adapter_state": "latest_prediction_source_ready",
        "source_summary": {
            "prediction_run_id": "run-ps-q12h",
            "generated_at": "2026-06-22T15:00:00Z",
            "market_uid": "BTC_JPY:bitFlyer",
            "signal_strength_percent": 40,
            "signal_strength_band": "low_reference",
        },
        "actual_file_read_succeeded": True,
        "payload_decode_succeeded": True,
        "review_packet_ready": True,
        "session_state_updated": True,
        "loaded_payload_count": 1,
        "blocker_count": 0,
        "warning_count": 2,
    }
    return {
        "panel_version": "prediction_warroom_latest_prediction_source_review_panel.ps_q12b.v1",
        "readability_polish_version": "prediction_warroom_latest_prediction_source_readability_polish.ps_q12g.v1",
        "panel_state": "latest_prediction_source_review_panel_ready",
        "adapter_packet": adapter,
        "q9g_session_state_seed_ready": True,
        "readability_rows": [{"item": "source_panel"}] * 6,
        "issue_rows": [{"severity": "warning"}],
        "read_only": True,
        "non_executing": True,
        "display_only": True,
        "warroom_page_mutation_allowed": False,
        "warroom_panel_mutation_allowed": False,
        "runtime_artifact_write_allowed": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "would_write_runtime_artifact": False,
        "would_send_to_broker": False,
    }


def _sample_uicheck(snapshot: dict) -> dict:
    return {
        "schema_version": "btcts.operator_ui.uicheck.v2",
        "page": {"selected_page_key": "warroom", "selected_page_label": "WarRoom"},
        "session_state_safe": {
            "selected_safe_values": {
                SNAPSHOT_KEY: snapshot,
            }
        },
        "repo": {"status_short": []},
    }


def main() -> int:
    failures: list[str] = []
    for path in (PANEL, TEST, CHECK, GUARD):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        try:
            ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")
    for path in (PANEL, TEST, CHECK):
        text = _read(path)
        for token in FORBIDDEN_TRUE_TOKENS:
            if token in text:
                failures.append(f"forbidden true token in {path.relative_to(REPO_ROOT)}: {token}")

    panel_text = _read(PANEL)
    test_text = _read(TEST)
    check_text = _read(CHECK)
    for marker in (
        "PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_UICHECK_SNAPSHOT_VERSION",
        "prediction_warroom_latest_prediction_source_uicheck_snapshot.ps_q12h.v1",
        "build_prediction_warroom_latest_prediction_source_uicheck_snapshot",
        "warroom_latest_prediction_source_review_panel_uicheck_snapshot",
        "PS-Q12H uicheck snapshot is display-only",
    ):
        if marker not in panel_text:
            failures.append(f"missing panel marker: {marker}")
    for marker in (
        "snapshot_panel = {",
        "q9g_session_state_seed_ready",
        "issue_row_count",
    ):
        if marker not in test_text:
            failures.append(f"missing unit test marker: {marker}")
    for marker in (
        "validate_warroom_inference_uicheck_snapshot_payload",
        "tmp/uicheck/uicheck_*_warroom.json",
        "--allow-missing",
        "Enable GPT UI Auto Save, open WarRoom, then rerun this checker.",
    ):
        if marker not in check_text:
            failures.append(f"missing check marker: {marker}")

    snapshot = build_prediction_warroom_latest_prediction_source_uicheck_snapshot(_sample_panel())
    if snapshot.get("snapshot_version") != PREDICTION_WARROOM_LATEST_PREDICTION_SOURCE_UICHECK_SNAPSHOT_VERSION:
        failures.append("snapshot version mismatch")
    if snapshot.get("panel_state") != "latest_prediction_source_review_panel_ready":
        failures.append("snapshot panel_state mismatch")
    if snapshot.get("adapter_state") != "latest_prediction_source_ready":
        failures.append("snapshot adapter_state mismatch")
    if snapshot.get("loaded_payload_count") != 1:
        failures.append("snapshot loaded payload count mismatch")
    if snapshot.get("blocker_count") != 0:
        failures.append("snapshot blocker count mismatch")
    if not snapshot.get("safe_boundary") or not all(snapshot["safe_boundary"].values()):
        failures.append("snapshot safe boundary must be all true")

    valid = validate_warroom_inference_uicheck_snapshot_payload(_sample_uicheck(snapshot))
    if valid.get("ok") is not True:
        failures.append(f"sample uicheck should validate: {valid.get('failures')}")
    missing = validate_warroom_inference_uicheck_snapshot_payload({"page": {"selected_page_key": "warroom"}, "session_state_safe": {"selected_safe_values": {}}})
    if missing.get("ok") is not False or "warroom_latest_prediction_source_uicheck_snapshot_missing" not in missing.get("failures", []):
        failures.append("missing snapshot must fail closed")
    wrong_page = validate_warroom_inference_uicheck_snapshot_payload({"page": {"selected_page_key": "collector"}, "session_state_safe": {"selected_safe_values": {SNAPSHOT_KEY: snapshot}}})
    if wrong_page.get("ok") is not False or "selected_page_key_not_warroom" not in wrong_page.get("failures", []):
        failures.append("non-warroom uicheck must fail page check")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q12h_warroom_uicheck_snapshot",
        "phase": "phase3_prediction_system_warroom_read_only_inference_display",
        "contract": {
            "uicheck_session_state_snapshot_present": not failures,
            "non_ui_checker_present": not failures,
            "snapshot_validation_fails_closed": not failures,
            "no_execution_surface": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q12h_warroom_uicheck_snapshot_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
