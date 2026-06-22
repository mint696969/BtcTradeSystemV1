# path: ./tools/check_phase4a_prediction_system_ps_q15d_operator_refresh_acceptance_gate.py
# desc: PS-Q15D read-only acceptance gate for an explicitly human-run operator-shell latest prediction refresh. This checker does not execute refresh/export or write runtime artifacts.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from check_phase4a_prediction_system_ps_q12c_warroom_live_inference_smoke import (  # noqa: E402
    build_warroom_live_inference_smoke_payload,
)
from check_phase4a_prediction_system_ps_q15a_source_readiness_root_cause import (  # noqa: E402
    build_report as build_q15a_report,
)
from check_phase4a_prediction_system_ps_q15b_source_readiness_producer_path import (  # noqa: E402
    build_report as build_q15b_report,
)

CHECKER = "ps_q15d_operator_refresh_acceptance_gate"
HOT_ROOT = r"D:\btc_ts_hot"
FRESHNESS_MAX_AGE_SEC = 3600


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, (list, tuple)) else []


def _acceptance_from_reports(q15a: Mapping[str, Any], q15b: Mapping[str, Any], smoke: Mapping[str, Any]) -> dict[str, Any]:
    file_meta = _as_mapping(q15a.get("file_metadata"))
    artifact = _as_mapping(q15b.get("artifact_metadata"))
    smoke_adapter_state = smoke.get("adapter_state")
    q15a_primary = str(q15a.get("primary_root_cause") or "")
    q15b_primary = str(q15b.get("primary_conclusion") or "")
    age = file_meta.get("age_sec")
    fresh = isinstance(age, int) and age <= FRESHNESS_MAX_AGE_SEC and file_meta.get("freshness_status") == "fresh"
    smoke_ready = (
        smoke.get("ok") is True
        and smoke_adapter_state == "latest_prediction_source_ready"
        and smoke.get("actual_file_read_succeeded") is True
        and smoke.get("payload_decode_succeeded") is True
        and smoke.get("loaded_payload_count") == 1
        and smoke.get("review_packet_ready") is True
        and smoke.get("session_state_updated") is True
    )
    producer_path_still_manual = q15b_primary == "operator_shell_refresh_path_exists_but_is_not_scheduler"
    accepted = fresh and smoke_ready and producer_path_still_manual
    blockers: list[str] = []
    warnings: list[str] = []
    if not fresh:
        blockers.append("latest_prediction_artifact_not_fresh_after_operator_refresh")
    if q15a_primary == "latest_prediction_artifact_stale":
        blockers.append("q15a_still_reports_latest_prediction_artifact_stale")
    if not smoke_ready:
        blockers.append("q12c_smoke_not_ready_after_operator_refresh")
    if not producer_path_still_manual:
        warnings.append("q15b_no_longer_reports_manual_operator_refresh_path")
    return {
        "accepted": accepted,
        "state": "operator_refresh_accepted" if accepted else "operator_refresh_not_accepted",
        "blockers": blockers,
        "warnings": warnings,
        "evidence": {
            "q15a_primary_root_cause": q15a_primary,
            "q15a_file_age_sec": age,
            "q15a_freshness_status": file_meta.get("freshness_status"),
            "q15b_primary_conclusion": q15b_primary,
            "q15b_artifact_age_sec": artifact.get("age_sec"),
            "smoke_ok": smoke.get("ok"),
            "smoke_adapter_state": smoke_adapter_state,
            "smoke_actual_file_read_succeeded": smoke.get("actual_file_read_succeeded"),
            "smoke_payload_decode_succeeded": smoke.get("payload_decode_succeeded"),
            "smoke_loaded_payload_count": smoke.get("loaded_payload_count"),
            "smoke_review_packet_ready": smoke.get("review_packet_ready"),
            "smoke_session_state_updated": smoke.get("session_state_updated"),
        },
    }


def build_report(*, hot_root: str = HOT_ROOT) -> dict[str, Any]:
    q15a = build_q15a_report(hot_root=hot_root)
    q15b = build_q15b_report()
    smoke = build_warroom_live_inference_smoke_payload(hot_latest_root_hint=hot_root)
    gate = _acceptance_from_reports(q15a, q15b, smoke)
    return {
        "ok": True,
        "checker": CHECKER,
        "observed_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "hot_root": hot_root,
        "acceptance_gate": gate,
        "q15a_primary_root_cause": q15a.get("primary_root_cause"),
        "q15b_primary_conclusion": q15b.get("primary_conclusion"),
        "q12c_smoke_ok": smoke.get("ok"),
        "q12c_adapter_state": smoke.get("adapter_state"),
        "next_action": "accepted_for_warroom_observation" if gate["accepted"] else "run_explicit_operator_refresh_or_keep_blocked",
        "safety": {
            "read_only_checker": True,
            "refresh_executed_by_this_checker": False,
            "export_runner_executed_by_this_checker": False,
            "runtime_artifact_write_performed_by_this_checker": False,
            "warroom_ui_export_trigger_added": False,
            "scheduler_created": False,
            "freshness_bypass_added": False,
            "force_ready_added": False,
            "ledger_append_allowed": False,
            "broker_private_api_allowed": False,
            "mode_apply_requested": False,
            "order_placement_requested": False,
            "autotrade_trigger_allowed": False,
            "parameter_apply_allowed": False,
            "parameter_staging_write_allowed": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only acceptance gate after explicit operator-shell refresh.")
    parser.add_argument("--hot-root", default=HOT_ROOT)
    args = parser.parse_args(argv)
    print(json.dumps(build_report(hot_root=args.hot_root), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def test_ps_q15d_acceptance_gate_rejects_stale_inputs() -> None:
    q15a = {
        "primary_root_cause": "latest_prediction_artifact_stale",
        "file_metadata": {"age_sec": 7200, "freshness_status": "stale"},
    }
    q15b = {
        "primary_conclusion": "operator_shell_refresh_path_exists_but_is_not_scheduler",
        "artifact_metadata": {"age_sec": 7200},
    }
    smoke = {
        "ok": False,
        "adapter_state": "latest_prediction_source_blocked",
        "actual_file_read_succeeded": False,
        "payload_decode_succeeded": False,
        "loaded_payload_count": 0,
        "review_packet_ready": False,
        "session_state_updated": False,
    }
    gate = _acceptance_from_reports(q15a, q15b, smoke)
    assert gate["accepted"] is False
    assert "latest_prediction_artifact_not_fresh_after_operator_refresh" in gate["blockers"]
    assert "q15a_still_reports_latest_prediction_artifact_stale" in gate["blockers"]
    assert "q12c_smoke_not_ready_after_operator_refresh" in gate["blockers"]


def test_ps_q15d_acceptance_gate_accepts_fresh_ready_inputs() -> None:
    q15a = {
        "primary_root_cause": "no_blocking_root_cause_detected_by_ps_q15a",
        "file_metadata": {"age_sec": 10, "freshness_status": "fresh"},
    }
    q15b = {
        "primary_conclusion": "operator_shell_refresh_path_exists_but_is_not_scheduler",
        "artifact_metadata": {"age_sec": 10},
    }
    smoke = {
        "ok": True,
        "adapter_state": "latest_prediction_source_ready",
        "actual_file_read_succeeded": True,
        "payload_decode_succeeded": True,
        "loaded_payload_count": 1,
        "review_packet_ready": True,
        "session_state_updated": True,
    }
    gate = _acceptance_from_reports(q15a, q15b, smoke)
    assert gate["accepted"] is True
    assert gate["state"] == "operator_refresh_accepted"
    assert gate["blockers"] == []


if __name__ == "__main__":
    raise SystemExit(main())
