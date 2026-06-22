# path: ./tools/test_phase4a_prediction_system_ps_q16b_disabled_non_ui_producer_runner_guard.py
# desc: Focused guard for PS-Q16B disabled-by-default non-UI producer runner scaffold and status artifact writer.

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_runner import (  # noqa: E402
    build_prediction_warroom_non_ui_scheduled_producer_runner,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py"
UNIT_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_runner.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16B_DISABLED_NON_UI_PRODUCER_RUNNER_2026-06-22.md"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_runner.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_runner.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16B_DISABLED_NON_UI_PRODUCER_RUNNER_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16b_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16b_disabled_non_ui_producer_runner_guard.py",
}
REQUIRED_DOC_MARKERS = (
    "PS-Q16B follows PS-Q16A",
    "producer_status_artifact_relative_path=prediction/status/non_ui_scheduled_producer_status.json",
    "latest_prediction_artifact_write_enabled=false",
    "producer_enabled=false",
    "scheduler_enabled=false",
    "actual_export_runner_invoked=false",
    "operator_acknowledged=true",
    "allow_status_artifact_write=true",
    "execute_status_artifact_write=true",
    "PS-Q16C: WarRoom read-only producer status loader/panel.",
)
FORBIDDEN_SOURCE_TOKENS = (
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "run_ps_q12d_export_and_smoke",
    "subprocess.run(",
    "import streamlit",
    "from streamlit",
    "send_order(",
    "create_order(",
    "append_decision(",
    "append_command(",
)
FORBIDDEN_DOC_MARKERS = (
    "producer_enabled=true",
    "scheduler_enabled=true",
    "latest_prediction_artifact_write_enabled=true",
    "ready_for_scheduler_enablement=true",
    "actual_export_runner_invoked=true",
    "prediction_build_requested=true",
    "warroom_ui_trigger_enabled=true",
    "parameter_apply=true",
    "parameter_staging_write=true",
    "broker_private_api=true",
    "ledger_append=true",
    "AutoTrade trigger-candidate=enabled",
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
            failures.append(f"forbidden source token in PS-Q16B module: {token}")

    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")

    default_packet = build_prediction_warroom_non_ui_scheduled_producer_runner().to_dict()
    for key in (
        "producer_enabled",
        "scheduler_enabled",
        "runtime_artifact_write_enabled",
        "latest_prediction_artifact_write_enabled",
        "status_artifact_written",
        "actual_export_runner_invoked",
        "prediction_build_requested",
        "warroom_ui_trigger_enabled",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "ready_for_scheduler_enablement",
        "ready_for_latest_prediction_artifact_write_automation",
    ):
        if default_packet.get(key) is not False:
            failures.append(f"default unsafe flag not false: {key}={default_packet.get(key)!r}")
    with TemporaryDirectory() as temp_dir:
        written_packet = build_prediction_warroom_non_ui_scheduled_producer_runner(
            hot_latest_root_hint=temp_dir,
            operator_acknowledged=True,
            allow_status_artifact_write=True,
            execute_status_artifact_write=True,
            allow_guard_test_root=True,
        ).to_dict()
        status_path = Path(str(written_packet.get("status_artifact_path")))
        if written_packet.get("status_artifact_written") is not True:
            failures.append("explicit guard-root status write should write status artifact")
        if not status_path.exists():
            failures.append("written status artifact path does not exist")
        else:
            data = json.loads(status_path.read_text(encoding="utf-8"))
            if data.get("producer_enabled") is not False or data.get("scheduler_enabled") is not False:
                failures.append("status artifact should preserve disabled producer/scheduler state")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q16b_disabled_non_ui_producer_runner",
        "phase": "phase3_prediction_system_warroom_realtime_observation_status_writer",
        "contract": {
            "disabled_by_default": True,
            "status_artifact_writer_explicit_only": True,
            "scheduler_enabled": False,
            "latest_prediction_artifact_write_enabled": False,
            "warroom_status_observation_next": True,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16b_disabled_non_ui_producer_runner_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
