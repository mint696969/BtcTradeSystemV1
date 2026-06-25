# path: ./tools/check_prediction_warroom_periodic_producer_scheduling_decision_ps_q19p.py
# desc: PS-Q19P read-only scheduling decision helper for ACK-gated bounded foreground prediction producer. It recommends a bounded command only; it does not install a scheduler, daemon, UI trigger, AutoTrade, broker, ledger, or parameter behavior.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.components.prediction_warroom_l4_latest_adapter import DEFAULT_HOT_LATEST_ROOT_HINT  # noqa: E402
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH,
    PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH,
    RECOMMENDED_CADENCE_SEC,
)
from tools.check_prediction_source_quality_gaps_ps_q19k import build_prediction_source_quality_gap_audit_packet  # noqa: E402
from tools.run_prediction_warroom_periodic_producer_ps_q19k import (  # noqa: E402
    LOCK_RELATIVE_PATH,
    PS_Q19K_PERIODIC_PRODUCER_ACK,
    STOP_RELATIVE_PATH,
)

PS_Q19P_SCHEDULING_DECISION_VERSION = "prediction_warroom.ps_q19p_periodic_producer_scheduling_decision.v1"
DEFAULT_OBSERVATION_MAX_CYCLES = 12
DEFAULT_OBSERVATION_INTERVAL_SEC = RECOMMENDED_CADENCE_SEC
DEFAULT_MAX_ARTIFACT_AGE_SEC = 900


def _root(root: str) -> Path:
    return Path(str(root).rstrip("\\/"))


def _artifact_path(root: str) -> Path:
    return _root(root) / LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH


def _status_path(root: str) -> Path:
    return _root(root) / PRODUCER_STATUS_ARTIFACT_RELATIVE_PATH


def _parse_ts(value: Any) -> datetime | None:
    text = str(value or "").strip()
    if not text:
        return None
    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _age_sec(value: Any, *, now: datetime | None = None) -> int | None:
    dt = _parse_ts(value)
    if dt is None:
        return None
    now_dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return int(max((now_dt - dt).total_seconds(), 0.0))


def _load_json(path: Path) -> tuple[Mapping[str, Any], str | None]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        return {}, exc.__class__.__name__
    return (loaded if isinstance(loaded, Mapping) else {}), None


def _safe_status_projection(status: Mapping[str, Any]) -> dict[str, Any]:
    safe_flags = status.get("safe_flags") if isinstance(status.get("safe_flags"), Mapping) else {}
    return {
        "producer_state": status.get("producer_state"),
        "last_success_generated_at": status.get("last_success_generated_at"),
        "last_warning_count": status.get("last_warning_count"),
        "consecutive_failure_count": status.get("consecutive_failure_count"),
        "producer_enabled": status.get("producer_enabled"),
        "scheduler_enabled": status.get("scheduler_enabled"),
        "safe_flags": dict(safe_flags),
    }


def build_ps_q19p_scheduling_decision_packet(
    *,
    root: str = DEFAULT_HOT_LATEST_ROOT_HINT,
    max_cycles: int = DEFAULT_OBSERVATION_MAX_CYCLES,
    interval_sec: int = DEFAULT_OBSERVATION_INTERVAL_SEC,
    max_artifact_age_sec: int = DEFAULT_MAX_ARTIFACT_AGE_SEC,
    now: datetime | None = None,
    payload: Mapping[str, Any] | None = None,
    status_payload: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return read-only decision for bounded foreground periodic producer observation.

    This helper never executes the producer and never installs any scheduler/daemon.
    """
    root_path = _root(root)
    artifact = _artifact_path(root)
    status_path = _status_path(root)
    artifact_payload = payload
    status = status_payload
    payload_load_error: str | None = None
    status_load_error: str | None = None
    if artifact_payload is None:
        artifact_payload, payload_load_error = _load_json(artifact)
    if status is None:
        status, status_load_error = _load_json(status_path)
    artifact_payload = artifact_payload if isinstance(artifact_payload, Mapping) else {}
    status = status if isinstance(status, Mapping) else {}

    run_identity = artifact_payload.get("run_identity") if isinstance(artifact_payload.get("run_identity"), Mapping) else {}
    generated_at = str(run_identity.get("generated_at") or artifact_payload.get("generated_at") or status.get("last_success_generated_at") or "")
    age = _age_sec(generated_at, now=now)
    gap_audit = build_prediction_source_quality_gap_audit_packet(payload=artifact_payload, source_path=str(artifact)) if artifact_payload else {"ok": False}
    priority_gap = gap_audit.get("priority_gap_summary") if isinstance(gap_audit.get("priority_gap_summary"), Mapping) else {}
    top_missing = gap_audit.get("top_missing_minimum_required_sources") if isinstance(gap_audit.get("top_missing_minimum_required_sources"), list) else []
    top_caps = gap_audit.get("top_signal_strength_cap_reasons") if isinstance(gap_audit.get("top_signal_strength_cap_reasons"), list) else []
    blockers: list[str] = []
    warnings: list[str] = []

    normalized_root = str(root_path).rstrip("\\/").lower().replace("/", "\\")
    if normalized_root != "d:\\btc_ts_hot":
        blockers.append("hot_root_must_be_d_btc_ts_hot_for_operator_scheduling_decision")
    if payload_load_error:
        blockers.append("latest_prediction_artifact_unreadable:" + payload_load_error)
    if status_load_error:
        warnings.append("producer_status_unreadable:" + status_load_error)
    if not artifact_payload:
        blockers.append("latest_prediction_artifact_missing_or_empty")
    if age is None:
        blockers.append("latest_prediction_generated_at_missing_or_invalid")
    elif age > int(max_artifact_age_sec):
        warnings.append("latest_prediction_artifact_not_fresh_enough_for_schedule_decision")
    if bool(priority_gap.get("tier0_source_quality_warnings_present")):
        blockers.append("tier0_source_quality_warnings_still_present")
    if bool(priority_gap.get("context_evidence_profile_minimum_sources_missing_present")) or bool(top_missing):
        blockers.append("context_profile_minimum_sources_still_missing")
    if top_caps:
        blockers.append("signal_strength_cap_reasons_still_present")
    if status.get("consecutive_failure_count") not in (None, 0):
        blockers.append("producer_consecutive_failures_present")
    if status.get("producer_enabled") is True:
        blockers.append("unexpected_status_producer_enabled_true")
    if status.get("scheduler_enabled") is True:
        blockers.append("unexpected_status_scheduler_enabled_true")
    if (root_path / LOCK_RELATIVE_PATH).exists():
        blockers.append("periodic_producer_lock_exists")
    if (root_path / STOP_RELATIVE_PATH).exists():
        warnings.append("periodic_producer_stop_file_exists_operator_should_remove_before_run")

    bounded_cycles = max(1, min(12, int(max_cycles)))
    bounded_interval = max(60, min(900, int(interval_sec)))
    if int(max_cycles) != bounded_cycles:
        warnings.append("max_cycles_clamped_for_observation_decision")
    if int(interval_sec) != bounded_interval:
        warnings.append("interval_sec_clamped_for_observation_decision")

    decision = "allow_ack_gated_bounded_foreground_observation" if not blockers else "keep_manual_or_fix_blockers_first"
    command = (
        "python .\\tools\\run_prediction_warroom_periodic_producer_ps_q19k.py "
        "--root D:\\btc_ts_hot "
        "--execute-periodic-producer "
        f"--ack {PS_Q19K_PERIODIC_PRODUCER_ACK} "
        f"--max-cycles {bounded_cycles} "
        f"--interval-sec {bounded_interval}"
    )
    followup = "python .\\tools\\check_prediction_source_quality_gaps_ps_q19k.py --root D:\\btc_ts_hot"
    smoke = (
        "python .\\tools\\check_phase4a_prediction_system_ps_q19f_warroom_live_smoke.py "
        "--root D:\\btc_ts_hot --manual-visual-confirmation --observed-panel-visible "
        "--observed-prediction-rows --observed-market-snapshot --observed-safety-flags"
    )
    return {
        "ok": True,
        "ps_q19p_version": PS_Q19P_SCHEDULING_DECISION_VERSION,
        "decision": decision,
        "ready_for_bounded_foreground_observation": decision == "allow_ack_gated_bounded_foreground_observation",
        "root": str(root_path),
        "latest_prediction_artifact_path": str(artifact),
        "producer_status_artifact_path": str(status_path),
        "latest_prediction_generated_at": generated_at,
        "latest_prediction_age_sec": age,
        "gap_audit_ok": gap_audit.get("ok") is True,
        "warning_kind_count": gap_audit.get("warning_kind_count"),
        "cap_reason_kind_count": gap_audit.get("cap_reason_kind_count"),
        "priority_gap_summary": dict(priority_gap),
        "top_missing_minimum_required_sources": top_missing[:5],
        "top_signal_strength_cap_reasons": top_caps[:5],
        "status_projection": _safe_status_projection(status),
        "recommended_bounded_command": command,
        "recommended_gap_audit_command_after_run": followup,
        "recommended_warroom_smoke_command_after_run": smoke,
        "recommended_max_cycles": bounded_cycles,
        "recommended_interval_sec": bounded_interval,
        "lock_relative_path": LOCK_RELATIVE_PATH,
        "stop_relative_path": STOP_RELATIVE_PATH,
        "blocked_reasons": list(dict.fromkeys(blockers)),
        "warning_reasons": list(dict.fromkeys(warnings)),
        "scheduler_install_performed": False,
        "scheduler_enabled": False,
        "scheduled_loop_enabled": False,
        "producer_enabled": False,
        "bounded_foreground_observation_only": True,
        "explicit_ack_required": True,
        "warroom_ui_trigger_enabled": False,
        "ui_triggered_runner_execution": False,
        "approval_or_authorization_allowed": False,
        "ledger_append_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "parameter_staging_write_allowed": False,
        "would_send_to_broker": False,
    }


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="PS-Q19P periodic producer scheduling decision helper")
    parser.add_argument("--root", default=DEFAULT_HOT_LATEST_ROOT_HINT)
    parser.add_argument("--max-cycles", type=int, default=DEFAULT_OBSERVATION_MAX_CYCLES)
    parser.add_argument("--interval-sec", type=int, default=DEFAULT_OBSERVATION_INTERVAL_SEC)
    parser.add_argument("--max-artifact-age-sec", type=int, default=DEFAULT_MAX_ARTIFACT_AGE_SEC)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    packet = build_ps_q19p_scheduling_decision_packet(
        root=str(args.root),
        max_cycles=int(args.max_cycles),
        interval_sec=int(args.interval_sec),
        max_artifact_age_sec=int(args.max_artifact_age_sec),
    )
    print(json.dumps(packet, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if packet.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
