# path: ./tools/test_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke_guard.py
# desc: Structural close guard for PS-Q12C WarRoom live inference smoke CLI. Does not depend on D-hot current freshness; stubs adapter for deterministic guard.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

import check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke as smoke_mod  # noqa: E402
from check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke import (  # noqa: E402
    SMOKE_VERSION,
    build_warroom_live_inference_smoke_payload,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
SMOKE = REPO_ROOT / "tools/check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke.py"
GUARD = REPO_ROOT / "tools/test_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke_guard.py"
EXPECTED_DIRTY = {
    "tools/check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke.py",
    "tools/test_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke_guard.py",
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


def _stub_adapter(*, hot_latest_root_hint: str, allow_actual_read: bool, session_state: dict | None, store_in_session_state: bool, **_: object):
    class _Packet:
        def to_dict(self) -> dict:
            if session_state is not None and store_in_session_state:
                session_state["warroom_prediction_lowered_display_packet_visibility_review_packet"] = {"seeded": True}
            return {
                "adapter_state": "latest_prediction_source_ready",
                "source_summary": {
                    "prediction_run_id": "stub-ps-q12c-live",
                    "generated_at": "2026-06-22T13:00:00Z",
                    "market_uid": "bitflyer.spot.BTC_JPY",
                    "signal_strength_percent": 77,
                    "signal_strength_band": "high",
                },
                "ready_for_warroom_review_panel": True,
                "review_packet_ready": True,
                "session_state_updated": True,
                "actual_file_read_attempted": True,
                "actual_file_read_succeeded": True,
                "payload_decode_attempted": True,
                "payload_decode_succeeded": True,
                "loaded_payload_count": 1,
                "blocker_count": 0,
                "warning_count": 1,
                "blocked_reasons": [],
                "warning_reasons": ["schema_validation_deferred_to_ps_q9c"],
                "loader_result": {
                    "artifact_results": [
                        {
                            "artifact_role": "prediction_system_result_snapshot",
                            "loader_state": "loaded_read_only_payload_decode_succeeded",
                            "path_exists": True,
                            "observed_file_size_bytes": 1234,
                            "observed_age_sec": 12,
                            "observed_last_modified_at": "2026-06-22T12:59:00+00:00",
                            "actual_file_read_attempted": True,
                            "actual_file_read_succeeded": True,
                            "payload_decode_attempted": True,
                            "payload_decode_succeeded": True,
                            "blocker_reasons": [],
                            "warning_reasons": ["schema_validation_deferred_to_ps_q9c"],
                        }
                    ]
                },
                "read_only": True,
                "non_executing": True,
                "source_adapter_only": True,
                "in_memory_result_only": True,
                "runtime_artifact_write_allowed": False,
                "ledger_append_allowed": False,
                "autotrade_trigger_allowed": False,
                "broker_private_api_allowed": False,
                "would_write_runtime_artifact": False,
                "would_write_collector_state": False,
                "would_send_to_broker": False,
                "broker_execution_requested": False,
                "mode_apply_requested": False,
                "command_ledger_append_requested": False,
                "approval_append_requested": False,
                "authorization_grant_requested": False,
                "autotrade_trigger_enabled": False,
            }
    return _Packet()


def main() -> int:
    failures: list[str] = []
    for path in (SMOKE, GUARD):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        try:
            ast.parse(text, filename=str(path))
        except SyntaxError as exc:
            failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")

    # Scan implementation text for forbidden execution/write true-tokens.
    # Do not scan this guard file itself, because it intentionally contains
    # the forbidden token literals inside FORBIDDEN_TRUE_TOKENS.
    smoke_text_for_forbidden_scan = _read(SMOKE)
    for token in FORBIDDEN_TRUE_TOKENS:
        if token in smoke_text_for_forbidden_scan:
            failures.append(f"forbidden true token in {SMOKE.relative_to(REPO_ROOT)}: {token}")

    smoke_text = _read(SMOKE)
    required_markers = (
        "SMOKE_VERSION",
        "prediction_system_ps_q12c_warroom_live_inference_smoke.v1",
        "build_warroom_live_inference_smoke_payload",
        "build_prediction_warroom_latest_prediction_source_adapter",
        "allow_actual_read=True",
        "store_in_session_state=True",
        "expected_prediction_path",
        "artifact_status",
        "boundary",
        "--allow-blocked",
        "no runtime write, no approval, no ledger, no AutoTrade, no broker/private API",
    )
    for marker in required_markers:
        if marker not in smoke_text:
            failures.append(f"missing smoke marker: {marker}")

    original = smoke_mod.build_prediction_warroom_latest_prediction_source_adapter
    try:
        smoke_mod.build_prediction_warroom_latest_prediction_source_adapter = _stub_adapter
        payload = build_warroom_live_inference_smoke_payload(hot_latest_root_hint="D:\btc_ts_hot")
    finally:
        smoke_mod.build_prediction_warroom_latest_prediction_source_adapter = original

    if payload.get("smoke_version") != SMOKE_VERSION:
        failures.append("smoke version mismatch")
    if payload.get("ok") is not True:
        failures.append("stubbed smoke should be ok")
    if payload.get("adapter_state") != "latest_prediction_source_ready":
        failures.append("adapter state mismatch")
    if payload.get("actual_file_read_succeeded") is not True or payload.get("payload_decode_succeeded") is not True:
        failures.append("read/decode should be true in stubbed smoke")
    if payload.get("source_summary", {}).get("prediction_run_id") != "stub-ps-q12c-live":
        failures.append("source summary mismatch")
    if "warroom_prediction_lowered_display_packet_visibility_review_packet" not in payload.get("session_state_keys", []):
        failures.append("session_state handoff key missing from smoke payload")
    boundary = payload.get("boundary", {})
    if not boundary or not all(boundary.values()):
        failures.append(f"boundary summary must be all true: {boundary}")
    if not payload.get("artifact_status"):
        failures.append("artifact status rows missing")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    result = {
        "ok": not failures,
        "guard": "ps_q12c_warroom_live_inference_smoke",
        "phase": "phase3_prediction_system_warroom_read_only_inference_display",
        "contract": {
            "operator_live_smoke_cli_present": not failures,
            "uses_ps_q12a_adapter_path": not failures,
            "read_only_no_execution_boundaries": not failures,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q12c_warroom_live_inference_smoke_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
