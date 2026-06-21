# path: ./tools/test_prediction_system_ps_q10f_latest_payload_export_preflight_bridge_close_guard.py
# desc: Close guard for PS-Q10F latest payload export preflight bridge.

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOUCHED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_preflight_bridge.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10f_latest_payload_export_preflight_bridge_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10f_latest_payload_export_preflight_bridge_close_guard.py",
)
GUARDS = (
    REPO_ROOT / "tools/test_prediction_system_ps_q10f_latest_payload_export_preflight_bridge_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10d_prediction_system_result_builder_runner_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10c_source_mapping_actual_observation_runbook_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10b_source_mapping_probe_runner_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q10a_source_mapping_preflight_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9z_hot_source_probe_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9y_latest_payload_export_runner_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9x_latest_payload_export_preflight_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9v_warroom_top_default_expanded_ui_layout_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9s_actual_observation_stdout_review_parser_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9r_actual_observation_runbook_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9q_operator_actual_read_runner_scaffold_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9p_operator_script_boundary_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9o_actual_read_review_composition_harness_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9n_actual_read_to_review_handoff_preflight_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9j_guarded_local_observation_hook_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9i_synthetic_review_packet_session_state_harness_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9h_lowered_display_packet_review_source_handoff_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9f_lowered_display_packet_visibility_review_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9e_actual_display_packet_lowering_adapter_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9d_prediction_result_display_packet_lowering_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9c_loaded_payload_schema_validation_result_panel_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9b_latest_payload_read_only_loader_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q9a_latest_payload_actual_read_preflight_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q8d_guarded_warroom_page_insertion_guard.py",
    REPO_ROOT / "tools/test_prediction_system_thread_close_handoff_guard.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/autotrade/",
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_export_runner.py",
)


def _syntax(path: Path, failures: list[str]) -> None:
    if not path.exists():
        failures.append(f"missing touched file: {path.relative_to(REPO_ROOT)}")
        return
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except Exception as exc:
        failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")


def _run(path: Path, failures: list[str]) -> None:
    proc = subprocess.run([sys.executable, str(path)], cwd=REPO_ROOT, text=True, capture_output=True, timeout=120)
    if proc.returncode != 0:
        failures.append(
            f"guard failed: {path.relative_to(REPO_ROOT)}\n"
            f"STDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}"
        )


def main() -> int:
    failures: list[str] = []
    for path in TOUCHED:
        _syntax(path, failures)
    for guard in GUARDS:
        _run(guard, failures)
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if any(prefix in line for prefix in PROTECTED_PREFIXES)]
    failures.extend(f"protected dirty path: {line}" for line in protected_dirty_hits)
    if failures:
        print("[FAIL] Prediction System PS-Q10F latest payload export preflight bridge close guard")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[OK] Prediction System PS-Q10F latest payload export preflight bridge close guard")
    return 0


def test_prediction_system_ps_q10f_latest_payload_export_preflight_bridge_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
