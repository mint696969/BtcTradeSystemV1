# path: ./tools/test_phase4a_prediction_system_ps_q16c_warroom_producer_status_panel_guard.py
# desc: Focused guard for PS-Q16C WarRoom read-only producer status loader/panel.

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
from btcts.apps.operator_ui.components.prediction_warroom_non_ui_scheduled_producer_status_panel import (  # noqa: E402
    build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_status_panel.py"
UNIT_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_status_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q16C_WARROOM_PRODUCER_STATUS_PANEL_2026-06-22.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
EXPECTED_DIRTY = {
    "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_non_ui_scheduled_producer_status_panel.py",
    "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_non_ui_scheduled_producer_status_panel.py",
    "docs/strategy/PREDICTION_SYSTEM_PS_Q16C_WARROOM_PRODUCER_STATUS_PANEL_2026-06-22.md",
    "tools/test_phase4a_prediction_system_ps_q16c_close_guard.py",
    "tools/test_phase4a_prediction_system_ps_q16c_warroom_producer_status_panel_guard.py",
    "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py",
}
REQUIRED_DOC_MARKERS = (
    "PS-Q16C mounts read-only producer status visibility",
    "prediction/status/non_ui_scheduled_producer_status.json",
    "producer_runner_invoked=false",
    "scheduler_enabled_by_this_panel=false",
    "latest_prediction_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "PS-Q16D: bounded manual refresh runner",
)
FORBIDDEN_PANEL_TOKENS = (
    "build_prediction_warroom_non_ui_scheduled_producer_runner(",
    "build_prediction_warroom_latest_payload_actual_export_runner(",
    "build_prediction_warroom_latest_payload_export_runner(",
    "write_text(",
    "tmp.replace(",
    ".replace(target",
    "subprocess.run(",
    "send_order(",
    "create_order(",
    "append_decision(",
    "append_command(",
)
FORBIDDEN_DOC_MARKERS = (
    "producer_runner_invoked=true",
    "scheduler_enabled_by_this_panel=true",
    "latest_prediction_artifact_write_allowed=true",
    "status_artifact_write_allowed=true",
    "parameter_apply_allowed=true",
    "parameter_staging_write_allowed=true",
    "ledger_append_allowed=true",
    "autotrade_trigger_allowed=true",
    "broker_private_api_allowed=true",
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
    for path in (PANEL, UNIT_TEST, DOC, WARROOM_PAGE):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")
            continue
        text = _read(path)
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=str(path))
            except SyntaxError as exc:
                failures.append(f"syntax failed: {path.relative_to(REPO_ROOT)}: {exc}")

    panel_text = _read(PANEL) if PANEL.exists() else ""
    for token in FORBIDDEN_PANEL_TOKENS:
        if token in panel_text:
            failures.append(f"forbidden panel token: {token}")
    doc_text = _read(DOC) if DOC.exists() else ""
    for marker in REQUIRED_DOC_MARKERS:
        if marker not in doc_text:
            failures.append(f"missing doc marker: {marker}")
    for marker in FORBIDDEN_DOC_MARKERS:
        if marker in doc_text:
            failures.append(f"forbidden doc marker present: {marker}")
    page_text = _read(WARROOM_PAGE) if WARROOM_PAGE.exists() else ""
    if "render_prediction_warroom_non_ui_scheduled_producer_status_panel" not in page_text:
        failures.append("WarRoom page does not import/render PS-Q16C producer status panel")

    default_packet = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet().to_dict()
    if default_packet.get("actual_file_read_attempted") is not False:
        failures.append("default status panel packet must not read without allow_actual_read")
    for key in (
        "producer_runner_invoked",
        "scheduler_enabled_by_this_panel",
        "warroom_ui_trigger_enabled",
        "would_write_status_artifact",
        "would_write_latest_prediction_artifact",
        "would_write_runtime_artifact",
        "parameter_apply_allowed",
        "parameter_staging_write_allowed",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
    ):
        if default_packet.get(key) is not False:
            failures.append(f"default unsafe flag not false: {key}={default_packet.get(key)!r}")
    with TemporaryDirectory() as temp_dir:
        writer = build_prediction_warroom_non_ui_scheduled_producer_runner(
            hot_latest_root_hint=temp_dir,
            operator_acknowledged=True,
            allow_status_artifact_write=True,
            execute_status_artifact_write=True,
            allow_guard_test_root=True,
        ).to_dict()
        packet = build_prediction_warroom_non_ui_scheduled_producer_status_panel_packet(
            hot_latest_root_hint=temp_dir,
            allow_actual_read=True,
            allow_guard_test_root=True,
        ).to_dict()
        if writer.get("status_artifact_written") is not True:
            failures.append("test setup status writer did not write")
        if packet.get("panel_state") != "producer_status_panel_loaded":
            failures.append("status panel should load explicit guard-root status artifact")
        if packet.get("producer_runner_invoked") is not False:
            failures.append("status panel must not invoke producer runner")
    dirty = _dirty_paths()
    unexpected_dirty = dirty - EXPECTED_DIRTY
    if unexpected_dirty:
        failures.append(f"unexpected dirty paths: {sorted(unexpected_dirty)}")

    payload = {
        "ok": not failures,
        "guard": "ps_q16c_warroom_producer_status_panel",
        "phase": "phase3_prediction_system_warroom_realtime_observation_status_panel",
        "contract": {
            "warroom_status_panel_mounted": "render_prediction_warroom_non_ui_scheduled_producer_status_panel" in page_text,
            "read_only_status_observation": True,
            "producer_runner_invoked": False,
            "scheduler_enabled_by_panel": False,
            "latest_prediction_write_by_panel": False,
            "autotrade_trigger_candidate_deferred": True,
            "expected_dirty_only": not unexpected_dirty,
        },
        "dirty_paths": sorted(dirty),
        "unexpected_dirty": sorted(unexpected_dirty),
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q16c_warroom_producer_status_panel_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
