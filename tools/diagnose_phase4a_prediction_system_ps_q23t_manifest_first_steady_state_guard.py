# path: ./tools/diagnose_phase4a_prediction_system_ps_q23t_manifest_first_steady_state_guard.py
# desc: No-write diagnostic hardening manifest-first WarRoom steady state after PS-Q23R closeout.

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT,
    build_latest_prediction_warroom_display_panel_packet,
)
from tools.diagnose_phase4a_prediction_system_ps_q23e_manifest_first_live_read_model import (  # noqa: E402
    run_manifest_first_live_read_model_diagnostic,
)
from tools.diagnose_phase4a_prediction_system_ps_q23r_closeout_steady_state_guard_sync import (  # noqa: E402
    run_ps_q23r_closeout_steady_state_guard_sync,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q23t_manifest_first_steady_state_guard.v1"
LATEST_MANIFEST_RELATIVE_PATH = "prediction/latest_manifest.json"
EXPECTED_LEGACY_COMPACT_RECORD_COUNT = 24
EXPECTED_FULL_RECORD_COUNT = 110


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _git(args: list[str]) -> str:
    proc = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _build_live_display_panel_packet() -> dict[str, Any]:
    packet = build_latest_prediction_warroom_display_panel_packet(fragment_enabled=False, lang="en")
    return dict(packet) if isinstance(packet, Mapping) else {}


def run_manifest_first_steady_state_guard() -> dict[str, Any]:
    branch = _git(["rev-parse", "--abbrev-ref", "HEAD"])
    head = _git(["rev-parse", "--short", "HEAD"])
    status_short = _git(["status", "--short", "--untracked-files=all"])

    q23r = run_ps_q23r_closeout_steady_state_guard_sync()
    q23e = run_manifest_first_live_read_model_diagnostic()
    panel = _build_live_display_panel_packet()

    q23r_artifact = _mapping(q23r.get("artifact_summary"))
    q23e_payload = _mapping(q23e.get("payload_status"))
    q23e_model = _mapping(q23e.get("read_model"))

    blockers: list[str] = []
    warnings: list[str] = []

    if q23r.get("ready") is not True:
        blockers.append("q23r_closeout_guard_ready_required")
    for item in list(q23r.get("blockers") or []):
        blockers.append(f"q23r:{item}")

    if q23r_artifact.get("legacy_compact_record_count") != EXPECTED_LEGACY_COMPACT_RECORD_COUNT:
        blockers.append("q23r_legacy_compact_record_count_24_required")
    if q23r_artifact.get("legacy_original_record_count") != EXPECTED_FULL_RECORD_COUNT:
        blockers.append("q23r_legacy_original_record_count_110_required")
    if q23r_artifact.get("manifest_record_count") != EXPECTED_FULL_RECORD_COUNT:
        blockers.append("q23r_manifest_record_count_110_required")
    if q23r_artifact.get("forecast_records_line_count") != EXPECTED_FULL_RECORD_COUNT:
        blockers.append("q23r_forecast_records_line_count_110_required")

    if q23e.get("ok") is not True:
        blockers.append("q23e_manifest_first_live_diagnostic_ok_required")
    if q23e.get("source_artifact_mode") != "distributed":
        blockers.append("q23e_must_select_distributed")
    if q23e_payload.get("source_artifact_relative_path") != LATEST_MANIFEST_RELATIVE_PATH:
        blockers.append("q23e_payload_status_must_use_latest_manifest")
    if q23e_model.get("source_artifact_relative_path") != LATEST_MANIFEST_RELATIVE_PATH:
        blockers.append("q23e_read_model_must_use_latest_manifest")
    if q23e.get("distributed_reader_ready") is not True:
        blockers.append("q23e_distributed_reader_ready_required")
    if q23e.get("distributed_stale_vs_legacy") is True:
        blockers.append("q23e_distributed_must_not_be_stale_vs_legacy")
    if q23e.get("legacy_fallback_ready") is not True:
        blockers.append("q23e_legacy_fallback_ready_required")
    if q23e.get("selected_record_count") != EXPECTED_FULL_RECORD_COUNT:
        blockers.append("q23e_selected_record_count_110_required")

    if panel.get("ok") is not True:
        blockers.append("display_panel_packet_ok_required")
    if panel.get("source_artifact_mode") != "distributed":
        blockers.append("display_panel_must_use_distributed_source")
    if panel.get("source_artifact_relative_path") != LATEST_MANIFEST_RELATIVE_PATH:
        blockers.append("display_panel_must_use_latest_manifest")
    if panel.get("distributed_reader_ready") is not True:
        blockers.append("display_panel_distributed_reader_ready_required")
    if panel.get("distributed_stale_vs_legacy") is True:
        blockers.append("display_panel_distributed_must_not_be_stale_vs_legacy")
    if panel.get("legacy_fallback_ready") is not True:
        blockers.append("display_panel_legacy_fallback_ready_required")
    try:
        prediction_row_count = int(panel.get("prediction_row_count") or 0)
    except Exception:
        prediction_row_count = 0
    if prediction_row_count <= 0:
        blockers.append("display_panel_prediction_rows_visible_required")
    if panel.get("fragment_enabled") is not False:
        warnings.append("display_panel_guard_expected_fragment_disabled")

    for key in (
        "runtime_artifact_write_allowed",
        "status_artifact_write_allowed",
        "prediction_artifact_write_allowed",
        "view_artifact_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "would_send_to_broker",
    ):
        if panel.get(key) is not False:
            blockers.append(f"display_panel_boundary_not_false:{key}")

    for key in (
        "latest_prediction_artifact_written",
        "status_artifact_written",
        "latest_manifest_written",
        "run_sidecars_written",
        "runtime_artifact_write_enabled",
        "broker_private_api_allowed",
        "autotrade_trigger_allowed",
        "would_send_to_broker",
    ):
        if q23e.get(key) is not False:
            blockers.append(f"q23e_boundary_not_false:{key}")

    ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "repo": {
            "branch": branch,
            "head": head,
            "status_short": status_short,
        },
        "ready": ready,
        "state": "ps_q23t_manifest_first_steady_state_ready" if ready else "ps_q23t_manifest_first_steady_state_blocked",
        "blockers": blockers,
        "warnings": warnings,
        "q23r_closeout": {
            "ready": q23r.get("ready"),
            "diagnostic_version": q23r.get("diagnostic_version"),
            "blockers": list(q23r.get("blockers") or []),
            "artifact_summary": dict(q23r_artifact),
        },
        "q23e_manifest_first_live": {
            "ok": q23e.get("ok"),
            "diagnostic_version": q23e.get("diagnostic_version"),
            "source_artifact_mode": q23e.get("source_artifact_mode"),
            "selected_record_count": q23e.get("selected_record_count"),
            "selected_generated_at": q23e.get("selected_generated_at"),
            "distributed_reader_ready": q23e.get("distributed_reader_ready"),
            "distributed_stale_vs_legacy": q23e.get("distributed_stale_vs_legacy"),
            "legacy_fallback_ready": q23e.get("legacy_fallback_ready"),
            "payload_status_source_artifact_relative_path": q23e_payload.get("source_artifact_relative_path"),
            "read_model_source_artifact_relative_path": q23e_model.get("source_artifact_relative_path"),
        },
        "display_panel_default": {
            "ok": panel.get("ok"),
            "hot_root_hint": Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT,
            "source_artifact_mode": panel.get("source_artifact_mode"),
            "source_artifact_relative_path": panel.get("source_artifact_relative_path"),
            "distributed_reader_ready": panel.get("distributed_reader_ready"),
            "distributed_stale_vs_legacy": panel.get("distributed_stale_vs_legacy"),
            "legacy_fallback_ready": panel.get("legacy_fallback_ready"),
            "prediction_row_count": prediction_row_count,
            "fragment_enabled": panel.get("fragment_enabled"),
            "runtime_artifact_write_allowed": panel.get("runtime_artifact_write_allowed"),
            "status_artifact_write_allowed": panel.get("status_artifact_write_allowed"),
            "prediction_artifact_write_allowed": panel.get("prediction_artifact_write_allowed"),
            "view_artifact_write_allowed": panel.get("view_artifact_write_allowed"),
            "autotrade_trigger_allowed": panel.get("autotrade_trigger_allowed"),
            "broker_private_api_allowed": panel.get("broker_private_api_allowed"),
            "would_send_to_broker": panel.get("would_send_to_broker"),
        },
        "safety": {
            "read_only_diagnostic": True,
            "latest_prediction_artifact_written": False,
            "status_artifact_written": False,
            "latest_manifest_written": False,
            "run_sidecars_written": False,
            "runtime_artifact_write_enabled": False,
            "scheduler_action_changed": False,
            "scheduler_enabled_by_this_tool": False,
            "trigger_added": False,
            "broker_private_api_allowed": False,
            "autotrade_trigger_allowed": False,
            "approval_or_ledger_allowed": False,
            "parameter_apply_allowed": False,
            "parameter_staging_write_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_manifest_first_steady_state_guard()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
