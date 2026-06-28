# path: ./tools/diagnose_phase4a_prediction_system_ps_q23k_legacy_latest_shrink_readiness_no_write.py
# desc: PS-Q23K no-write readiness diagnostic before shrinking legacy latest prediction artifact.

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
for candidate in (REPO_ROOT, SRC_ROOT):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from tools.diagnose_phase4a_prediction_system_ps_q23i_post_switch_closeout_readiness import run_post_switch_closeout_readiness  # noqa: E402
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT,
    build_latest_prediction_warroom_display_panel_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.legacy_latest_shrink_readiness.ps_q23k.v1"
LEGACY_LATEST_RELATIVE_PATH = "prediction/latest_prediction_system_result.json"
LATEST_MANIFEST_RELATIVE_PATH = "prediction/latest_manifest.json"
REFERENCE_GLOBS = (
    "btcts_next/src/**/*.py",
    "tools/**/*.py",
)

ALLOWED_LEGACY_REFERENCE_CLASSES = {
    "tests",
    "docs_or_comments",
    "manifest_first_adapter_legacy_fallback",
    "writer_or_contract_retained",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _as_mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _git_status_short() -> str:
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return proc.stdout.strip()


def _grep(pattern: str, glob: str) -> list[dict[str, Any]]:
    try:
        proc = subprocess.run(
            ["git", "grep", "-n", "--", pattern, glob],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
    except Exception as exc:  # noqa: BLE001 - diagnostic only
        return [{"path": "", "line": 0, "text": f"grep_failed:{exc.__class__.__name__}:{exc}"}]
    hits: list[dict[str, Any]] = []
    if proc.returncode not in (0, 1):
        return [{"path": "", "line": 0, "text": f"grep_returncode:{proc.returncode}:{proc.stderr.strip()}"}]
    for raw in proc.stdout.splitlines():
        try:
            path, line, text = raw.split(":", 2)
            hits.append({"path": path.replace("\\", "/"), "line": int(line), "text": text.strip()})
        except ValueError:
            hits.append({"path": "", "line": 0, "text": raw})
    return hits


def _classify_reference(hit: Mapping[str, Any]) -> str:
    path = str(hit.get("path") or "").replace("\\", "/")
    text = str(hit.get("text") or "")
    if "/tests/" in path or path.startswith("tools/test_"):
        return "tests"
    if text.startswith("#") or "# desc:" in text or path.startswith("docs/"):
        return "docs_or_comments"
    if path.endswith("prediction_warroom/read_models/latest_prediction_warroom_read_model.py"):
        return "manifest_first_adapter_legacy_fallback"
    if "prediction_warroom_latest_payload_export" in path or "prediction_warroom_non_ui_scheduled_producer" in path or "prediction_warroom_bounded_manual_refresh_runner" in path or "disabled_scheduler_design" in path:
        return "writer_or_contract_retained"
    if "q18" in path.lower() or "latest_prediction_summary_widget" in path:
        return "legacy_widget_or_mapping_reader"
    if "prediction_warroom_l4_latest_adapter" in path:
        return "legacy_l4_latest_adapter_reader"
    return "unclassified_legacy_reference"


def legacy_reference_inventory() -> dict[str, Any]:
    hits_by_pattern: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for glob in REFERENCE_GLOBS:
        for pattern in (LEGACY_LATEST_RELATIVE_PATH, "LATEST_PREDICTION_ARTIFACT_RELATIVE_PATH"):
            for hit in _grep(pattern, glob):
                key = (str(hit.get("path") or ""), int(hit.get("line") or 0), str(hit.get("text") or ""))
                if key in seen:
                    continue
                seen.add(key)
                row = dict(hit)
                row["classification"] = _classify_reference(row)
                row["pattern"] = pattern
                hits_by_pattern.append(row)
    class_counts: dict[str, int] = {}
    for row in hits_by_pattern:
        cls = str(row.get("classification") or "")
        class_counts[cls] = class_counts.get(cls, 0) + 1
    blocking = [
        row for row in hits_by_pattern
        if str(row.get("classification") or "") not in ALLOWED_LEGACY_REFERENCE_CLASSES
    ]
    return {
        "legacy_reference_count": len(hits_by_pattern),
        "legacy_reference_class_counts": class_counts,
        "blocking_legacy_reference_count": len(blocking),
        "blocking_legacy_reference_classes": sorted({str(row.get("classification") or "") for row in blocking}),
        "blocking_legacy_reference_samples": blocking[:12],
        "legacy_reference_samples": hits_by_pattern[:20],
    }


def _false_safety_flags() -> dict[str, Any]:
    return {
        "legacy_latest_shrink_executed": False,
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
    }


def run_legacy_latest_shrink_readiness_no_write() -> dict[str, Any]:
    repo_status_short = _git_status_short()
    inventory = legacy_reference_inventory()
    q23i = run_post_switch_closeout_readiness()
    display_packet = build_latest_prediction_warroom_display_panel_packet(fragment_enabled=False, lang="en")
    blockers: list[str] = []
    warnings: list[str] = []
    if repo_status_short:
        blockers.append("repo_clean_required_before_legacy_latest_shrink_readiness")
    if q23i.get("post_switch_closeout_ready") is not True:
        blockers.append("q23i_post_switch_closeout_ready_required")
    if q23i.get("reader_default_change_preflight_ready") is not True:
        blockers.append("q23i_reader_default_change_preflight_ready_required")
    if display_packet.get("source_artifact_mode") != "distributed":
        blockers.append("q23j_display_default_must_select_distributed")
    if display_packet.get("source_artifact_relative_path") != LATEST_MANIFEST_RELATIVE_PATH:
        blockers.append("q23j_display_default_must_use_latest_manifest")
    if display_packet.get("distributed_stale_vs_legacy") is True:
        blockers.append("q23j_distributed_must_not_be_stale_vs_legacy")
    if display_packet.get("legacy_fallback_ready") is not True:
        blockers.append("legacy_fallback_ready_required_before_any_shrink")
    if int(display_packet.get("prediction_row_count") or 0) <= 0:
        blockers.append("q23j_display_prediction_rows_required")
    if int(inventory.get("blocking_legacy_reference_count") or 0) > 0:
        blockers.append("blocking_legacy_latest_references_remain")
    if "writer_or_contract_retained" in _as_mapping(inventory.get("legacy_reference_class_counts")):
        warnings.append("legacy_writer_contract_still_retained_expected_stage2")

    shrink_ready = not blockers
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "generated_at": _utc_now(),
        "read_only_diagnostic": True,
        "legacy_latest_retained": True,
        "legacy_latest_shrink_ready": shrink_ready,
        "legacy_latest_shrink_state": "legacy_latest_shrink_ready" if shrink_ready else "legacy_latest_shrink_blocked_no_write",
        "blockers": blockers,
        "warnings": warnings,
        "repo_status_short": repo_status_short,
        "q23i": {
            "post_switch_closeout_ready": q23i.get("post_switch_closeout_ready"),
            "reader_default_change_preflight_ready": q23i.get("reader_default_change_preflight_ready"),
            "scheduled_sidecar_dual_write_enabled_observed": q23i.get("scheduled_sidecar_dual_write_enabled_observed"),
            "trigger_count": q23i.get("trigger_count"),
        },
        "q23j_display_default": {
            "hot_root_hint": Q23J_DISPLAY_DEFAULT_HOT_ROOT_HINT,
            "ok": display_packet.get("ok"),
            "read_model_ok": display_packet.get("read_model_ok"),
            "source_artifact_mode": display_packet.get("source_artifact_mode"),
            "source_artifact_relative_path": display_packet.get("source_artifact_relative_path"),
            "distributed_reader_ready": display_packet.get("distributed_reader_ready"),
            "distributed_stale_vs_legacy": display_packet.get("distributed_stale_vs_legacy"),
            "legacy_fallback_ready": display_packet.get("legacy_fallback_ready"),
            "prediction_row_count": display_packet.get("prediction_row_count"),
            "freshness_state": display_packet.get("freshness_state"),
        },
        "legacy_reference_inventory": inventory,
        **_false_safety_flags(),
    }


def main() -> int:
    result = run_legacy_latest_shrink_readiness_no_write()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ok") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
