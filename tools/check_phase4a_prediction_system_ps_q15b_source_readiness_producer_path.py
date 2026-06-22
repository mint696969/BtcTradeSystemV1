# path: ./tools/check_phase4a_prediction_system_ps_q15b_source_readiness_producer_path.py
# desc: PS-Q15B read-only diagnostic for the latest prediction artifact producer/export path. Static source and hot-file metadata inspection only; does not run export, write runtime artifacts, bypass freshness, force-ready, append ledger, call broker, apply mode/order, trigger AutoTrade, or apply/stage parameters.

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
HOT_ROOT = Path(r"D:\btc_ts_hot")
LATEST_ARTIFACT = HOT_ROOT / "prediction" / "latest_prediction_system_result.json"
CHECKER = "ps_q15b_source_readiness_producer_path"

SOURCE_FILES = {
    "q10h_actual_export_runner": "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_actual_export_runner.py",
    "q9y_export_runner": "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_runner.py",
    "q12d_manual_operator_runner": "tmp/work/ps_q12d_refresh_latest_prediction/run_ps_q12d_export_and_smoke.py",
    "warroom_page": "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
}

REQUIRED_MARKERS = {
    "q10h_actual_export_runner": [
        "prediction_warroom_latest_payload_actual_export_runner.ps_q10h.v1",
        "require_operator_acknowledgement",
        "require_runtime_artifact_write_request",
        "do_not_run_from_warroom_ui",
        "build_prediction_warroom_latest_payload_export_runner",
    ],
    "q9y_export_runner": [
        "prediction_warroom_latest_payload_export_runner.ps_q9y.v1",
        "operator_acknowledged",
        "execute_export",
        "write_exactly_latest_prediction_system_result_json",
        "do_not_run_from_warroom_ui",
    ],
    "q12d_manual_operator_runner": [
        "Operator-shell runner",
        "build_prediction_warroom_latest_payload_actual_export_runner",
        "allow_runtime_artifact_write=True",
        "requested_warroom_ui_trigger=False",
        "requested_approval_or_ledger_or_autotrade_or_broker=False",
    ],
}

FORBIDDEN_WARROOM_MARKERS = (
    "prediction_warroom_latest_payload_actual_export_runner",
    "build_prediction_warroom_latest_payload_actual_export_runner",
    "allow_runtime_artifact_write=True",
    "execute_export=True",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _artifact_metadata(now: datetime) -> dict[str, Any]:
    if not LATEST_ARTIFACT.exists():
        return {
            "path": str(LATEST_ARTIFACT),
            "path_exists": False,
            "mtime_utc": "",
            "age_sec": None,
            "size_bytes": None,
        }
    stat = LATEST_ARTIFACT.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
    age_sec = max(0, int((now - mtime).total_seconds()))
    generated_at = ""
    try:
        payload = json.loads(LATEST_ARTIFACT.read_text(encoding="utf-8-sig"))
        if isinstance(payload, Mapping):
            run_identity = payload.get("run_identity") if isinstance(payload.get("run_identity"), Mapping) else {}
            forecast = payload.get("forecast_batch") if isinstance(payload.get("forecast_batch"), Mapping) else {}
            generated_at = str(payload.get("generated_at") or run_identity.get("generated_at") or forecast.get("generated_at") or "")
    except Exception:
        generated_at = ""
    return {
        "path": str(LATEST_ARTIFACT),
        "path_exists": True,
        "mtime_utc": mtime.isoformat().replace("+00:00", "Z"),
        "age_sec": age_sec,
        "size_bytes": int(stat.st_size),
        "generated_at": generated_at,
    }


def _source_marker_report() -> dict[str, Any]:
    report: dict[str, Any] = {}
    for key, rel in SOURCE_FILES.items():
        path = REPO_ROOT / rel
        text = _read(path)
        required = REQUIRED_MARKERS.get(key, [])
        report[key] = {
            "path": rel,
            "exists": path.exists(),
            "required_markers_present": all(marker in text for marker in required),
            "missing_required_markers": [marker for marker in required if marker not in text],
        }
    warroom_text = _read(REPO_ROOT / SOURCE_FILES["warroom_page"])
    report["warroom_page"]["export_runner_mount_markers_present"] = [marker for marker in FORBIDDEN_WARROOM_MARKERS if marker in warroom_text]
    report["warroom_page"]["export_runner_not_mounted"] = not report["warroom_page"]["export_runner_mount_markers_present"]
    return report


def build_report() -> dict[str, Any]:
    now = _utc_now()
    source_report = _source_marker_report()
    artifact = _artifact_metadata(now)
    q10h_ok = bool(source_report.get("q10h_actual_export_runner", {}).get("required_markers_present"))
    q9y_ok = bool(source_report.get("q9y_export_runner", {}).get("required_markers_present"))
    q12d_ok = bool(source_report.get("q12d_manual_operator_runner", {}).get("required_markers_present"))
    warroom_not_mounted = bool(source_report.get("warroom_page", {}).get("export_runner_not_mounted"))
    conclusions = []
    if q10h_ok and q9y_ok and q12d_ok and warroom_not_mounted:
        conclusions.append(
            {
                "category": "operator_shell_refresh_path_exists_but_is_not_scheduler",
                "evidence": "PS-Q10H/PS-Q9Y exist and PS-Q12D uses them from tmp/work operator-shell runner; WarRoom page does not mount export runner",
                "impact": "latest prediction artifact can be refreshed manually, but will go stale unless a separate producer/operator refresh is run",
                "safe_next_check": "decide whether to run the existing operator-shell refresh explicitly, or design a separate non-UI scheduled producer; do not run from WarRoom UI",
            }
        )
    if artifact.get("path_exists") and isinstance(artifact.get("age_sec"), int) and artifact.get("age_sec", 0) > 3600:
        conclusions.append(
            {
                "category": "current_latest_artifact_is_stale",
                "evidence": f"age_sec={artifact.get('age_sec')} > 3600 at {artifact.get('path')}",
                "impact": "Q9A/Q9B will fail closed before read/decode",
                "safe_next_check": "refresh only through an explicitly approved non-UI path, or continue read-only producer investigation",
            }
        )
    return {
        "ok": True,
        "checker": CHECKER,
        "observed_at_utc": now.isoformat().replace("+00:00", "Z"),
        "artifact_metadata": artifact,
        "source_marker_report": source_report,
        "conclusions": conclusions,
        "primary_conclusion": conclusions[0]["category"] if conclusions else "producer_path_inconclusive",
        "safety": {
            "read_only_diagnostic": True,
            "export_runner_executed": False,
            "runtime_artifact_write_performed": False,
            "freshness_bypass_added": False,
            "force_ready_added": False,
            "warroom_ui_export_trigger_added": False,
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
    parser = argparse.ArgumentParser(description="Read-only diagnostic for latest prediction source producer/export path.")
    parser.parse_args(argv)
    print(json.dumps(build_report(), ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def test_ps_q15b_classifies_manual_operator_refresh_path() -> None:
    report = build_report()
    assert report["checker"] == CHECKER
    assert report["safety"]["read_only_diagnostic"] is True
    assert report["safety"]["export_runner_executed"] is False
    assert report["safety"]["runtime_artifact_write_performed"] is False
    assert report["source_marker_report"]["q10h_actual_export_runner"]["exists"] is True
    assert report["source_marker_report"]["q9y_export_runner"]["exists"] is True
    assert report["source_marker_report"]["warroom_page"]["export_runner_not_mounted"] is True


if __name__ == "__main__":
    raise SystemExit(main())
