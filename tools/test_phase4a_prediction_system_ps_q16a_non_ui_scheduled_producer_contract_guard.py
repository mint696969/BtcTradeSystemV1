# path: ./tools/test_phase4a_prediction_system_ps_q16a_non_ui_scheduled_producer_contract_guard.py
# desc: Structural guard for PS-Q16A non-UI scheduled producer contract/guard/visibility design only.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_contract import (  # noqa: E402
    build_prediction_warroom_non_ui_scheduled_producer_contract,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py"
UNIT_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_contract.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16A_NON_UI_SCHEDULED_PRODUCER_CONTRACT_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_contract.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_contract.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16A_NON_UI_SCHEDULED_PRODUCER_CONTRACT_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16a_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16a_non_ui_scheduled_producer_contract_guard.py",
}
REQUIRED_DOC_MARKERS = (
    "WarRoom tab can observe Prediction System output as a continually refreshed read-only source",
    "AutoTrade trigger-candidate work is deferred.",
    "contract_version=prediction_warroom_non_ui_scheduled_producer_contract.ps_q16a.v1",
    "producer_status_artifact_relative_path=prediction/status/non_ui_scheduled_producer_status.json",
    "freshness_max_age_sec=3600",
    "recommended_cadence_sec=300",
    "producer_enabled=false",
    "scheduler_enabled=false",
    "runtime_artifact_write_enabled=false",
    "warroom_ui_trigger_enabled=false",
    "source_quality_cap_review",
    "signal_strength_band_calibration_review",
    "rollback_does_not_force_ready=yes",
    "PS-Q16B: disabled-by-default non-UI producer runner scaffold",
)
FORBIDDEN_SOURCE_TOKENS = (
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "run_ps_q12d_export_and_smoke",
    "subprocess.run(",
    "Path(",
    "open(",
    "write_text(",
    "replace(",
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    "import streamlit",
    "from streamlit",
)
FORBIDDEN_DOC_MARKERS = (
    "scheduler_enabled=true",
    "runtime_artifact_write_enabled=true",
    "producer_enabled=true",
    "warroom_ui_trigger_enabled=true",
    "parameter_apply=true",
    "parameter_staging_write=true",
    "silent_live_parameter_mutation=true",
    "broker_private_api=true",
    "ledger_append=true",
    "freshness_bypass=true",
    "force_ready=true",
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
    for path in (MODULE, UNIT_TEST, DOC):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")

    module_text = _read(MODULE) if MODULE.exists() else ""
    for token in FORBIDDEN_SOURCE_TOKENS:
        if token in module_text:
            failures.append(f"forbidden source token in contract module: {token}")

    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")

    ready = build_prediction_warroom_non_ui_scheduled_producer_contract().to_dict()
    if ready.get("contract_state") != "non_ui_scheduled_producer_contract_ready_for_disabled_runner_slice":
        failures.append("default contract should be ready only for disabled runner slice")
    for key in (
        "producer_enabled",
        "scheduler_enabled",
        "runtime_artifact_write_enabled",
        "warroom_ui_trigger_enabled",
        "ready_for_scheduler_enablement",
        "ready_for_runtime_artifact_write_automation_enablement",
        "would_write_runtime_artifact",
        "would_write_status_artifact",
        "would_mutate_live_parameters",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if ready.get(key) is not False:
            failures.append(f"default contract unsafe flag not false: {key}={ready.get(key)!r}")

    blocked = build_prediction_warroom_non_ui_scheduled_producer_contract(
        request_scheduler_enable=True,
        request_runtime_artifact_write_enable=True,
        request_producer_enable=True,
        request_warroom_ui_trigger=True,
        request_parameter_apply=True,
        request_parameter_staging_write=True,
        request_approval_or_ledger_or_autotrade_or_broker=True,
    ).to_dict()
    if blocked.get("contract_state") != "non_ui_scheduled_producer_contract_blocked":
        failures.append("enablement request should be blocked in PS-Q16A")
    if not blocked.get("blocked_reasons"):
        failures.append("blocked enablement request should expose blocked_reasons")

    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q16a_non_ui_scheduled_producer_contract",
        "phase": "phase3_prediction_system_warroom_realtime_observation_contract",
        "contract": {
            "warroom_realtime_observation_priority": True,
            "autotrade_trigger_candidate_deferred": True,
            "design_only_no_scheduler_enablement": True,
            "accuracy_adjustment_review_only": True,
            "rollback_disable_path_required": True,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16a_non_ui_scheduled_producer_contract_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
