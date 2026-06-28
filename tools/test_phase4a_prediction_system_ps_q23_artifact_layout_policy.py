# path: ./tools/test_phase4a_prediction_system_ps_q23_artifact_layout_policy.py
# desc: Focused guard for PS-Q23 distributed artifact layout policy. No runtime writes.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q23_ARTIFACT_LAYOUT_POLICY_2026-06-28.md"

REQUIRED_MARKERS = (
    "ps_q23_artifact_layout_policy=true",
    "monolithic_latest_mitigation=true",
    "distributed_run_artifacts=true",
    "latest_manifest_pointer=true",
    "backward_compat_latest_retained=true",
    "runtime_artifact_write_changed=false",
    "broker_autotrade=false",
)

REQUIRED_PATHS = (
    "prediction/latest_manifest.json",
    "prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/manifest.json",
    "prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/summary.json",
    "prediction/runs/YYYY-MM-DD/HHMMSS_<run_id>/forecast_records.jsonl",
    "prediction/status/non_ui_scheduled_producer_status.json",
    "prediction/latest_prediction_system_result.json",
)

REQUIRED_CONTRACTS = (
    "1 artifact = 1 responsibility",
    "1 run = 1 immutable run_id directory",
    "latest = pointer + thin summary, not the full body",
    "try latest_manifest distributed layout",
    "fallback to legacy latest",
    "never silently return empty on oversized artifacts",
    "atomically replace latest_manifest.json only after run manifest is complete",
)

FALSE_BOUNDARIES = (
    "broker_private_api_allowed=false",
    "autotrade_trigger_allowed=false",
    "approval_or_ledger_allowed=false",
    "parameter_apply_allowed=false",
    "parameter_staging_write_allowed=false",
    "would_send_to_broker=false",
)


def test_policy_markers_present() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in REQUIRED_MARKERS:
        assert marker in text, marker


def test_target_layout_paths_are_declared() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for path in REQUIRED_PATHS:
        assert path in text, path


def test_compatibility_and_atomicity_contracts_declared() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for contract in REQUIRED_CONTRACTS:
        assert contract in text, contract


def test_safety_boundaries_remain_false() -> None:
    text = SPEC.read_text(encoding="utf-8-sig")
    for marker in FALSE_BOUNDARIES:
        assert marker in text, marker


if __name__ == "__main__":
    test_policy_markers_present()
    test_target_layout_paths_are_declared()
    test_compatibility_and_atomicity_contracts_declared()
    test_safety_boundaries_remain_false()
    print(json.dumps({"ok": True}))
