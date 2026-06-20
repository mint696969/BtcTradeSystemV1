# path: ./tools/test_prediction_system_ps_q6d_dry_run_status_panel_close_guard.py
# desc: Close guard for PS-Q6D latest payload dry-run status panel.

from __future__ import annotations

import ast
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TOUCHED = (
    REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_latest_payload_dry_run_status_panel.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q6d_dry_run_status_panel_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q6d_dry_run_status_panel_close_guard.py",
)
GUARDS = (
    REPO_ROOT / "tools/test_prediction_system_ps_q6d_dry_run_status_panel_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q6c_loader_dry_run_simulator_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q6b_loader_permission_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q6a_latest_payload_preflight_status_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q5c_payload_schema_validator_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q5b_explanation_widget_groups_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q5a_source_quality_explanations_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q4d_warroom_sample_packets_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q4c_l4_latest_adapter_contract_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q4b_warroom_widget_groups_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q4a_warroom_display_packet_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q3c_signal_strength_bands_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q3b_profile_family_source_caps_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q3a_tier0_family_signal_caps_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q2d_tier0_source_quality_gate_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q2c_context_evidence_profiles_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q2b_source_artifact_runtime_coverage_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_q2_source_artifact_coverage_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_g_lite_runner_guard.py",
    REPO_ROOT / "tools/test_prediction_system_ps_h1_scenario_core_lite_guard.py",
)
PROTECTED_PREFIXES = (
    "btcts_next/src/btcts/collector_vnext/",
    "btcts_next/src/btcts/autotrade/",
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
        failures.append(f"guard failed: {path.relative_to(REPO_ROOT)}\nSTDOUT:\n{proc.stdout[-2000:]}\nSTDERR:\n{proc.stderr[-2000:]}")


def main() -> int:
    failures: list[str] = []
    for path in TOUCHED:
        _syntax(path, failures)
    for guard in GUARDS:
        _run(guard, failures)
    proc = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=True)
    protected_dirty_hits = [line for line in proc.stdout.splitlines() if any(prefix in line for prefix in PROTECTED_PREFIXES)]
    failures.extend(f"protected collector/autotrade dirty: {line}" for line in protected_dirty_hits)
    if failures:
        print("[FAIL] Prediction System PS-Q6D dry-run status panel close guard")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("[OK] Prediction System PS-Q6D dry-run status panel close guard")
    return 0


def test_prediction_system_ps_q6d_dry_run_status_panel_close_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
