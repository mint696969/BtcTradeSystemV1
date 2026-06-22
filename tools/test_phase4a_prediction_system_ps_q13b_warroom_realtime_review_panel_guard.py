# path: ./tools/test_phase4a_prediction_system_ps_q13b_warroom_realtime_review_panel_guard.py
# desc: Guard for PS-Q13B WarRoom realtime review preflight display integration.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_realtime_review_preflight_panel.py"
TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_prediction_warroom_realtime_review_preflight_panel.py"
WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/prediction_warroom_realtime_review_preflight_contract.py"

REQUIRED_PANEL_MARKERS = (
    "PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_PANEL_VERSION",
    "prediction_warroom_realtime_review_preflight_panel.ps_q13b.v1",
    "build_prediction_warroom_realtime_review_preflight_panel_packet",
    "render_prediction_warroom_realtime_review_preflight_panel",
    "prediction_warroom_realtime_review_surface_rows",
    "prediction_warroom_realtime_review_boundary_rows",
    "parameter_mutation_allowed",
    "would_mutate_live_parameters",
    "would_append_parameter_version",
    "ledger_append_allowed",
    "autotrade_trigger_allowed",
    "broker_private_api_allowed",
)

REQUIRED_WARROOM_MARKERS = (
    "render_prediction_warroom_realtime_review_preflight_panel",
    "latest_prediction_source_panel=latest_prediction_source_panel",
    "latest_prediction_source_panel = render_prediction_warroom_latest_prediction_source_review_panel()",
)

FORBIDDEN_WARROOM_MARKERS = (
    "append_decision(",
    "append_command(",
    "send_order(",
    "create_order(",
    "call_private_api(",
    "apply_live_parameters(",
    "mutate_live_parameters(",
)

REQUIRED_TEST_MARKERS = (
    "test_prediction_warroom_realtime_review_preflight_panel",
    "realtime_review_preflight_panel_ready",
    "realtime_review_preflight_panel_review_only_not_ready",
    "silent_live_parameter_mutation",
    "autotrade_trigger_consumption",
    "broker_private_api",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def main() -> int:
    failures: list[str] = []
    for path in (PANEL, TEST, WARROOM, CONTRACT):
        if not path.exists():
            failures.append(f"missing file: {path.relative_to(REPO_ROOT)}")

    panel_text = _read(PANEL) if PANEL.exists() else ""
    test_text = _read(TEST) if TEST.exists() else ""
    warroom_text = _read(WARROOM) if WARROOM.exists() else ""
    contract_text = _read(CONTRACT) if CONTRACT.exists() else ""

    for marker in REQUIRED_PANEL_MARKERS:
        if marker not in panel_text:
            failures.append(f"missing panel marker: {marker}")
    for marker in REQUIRED_WARROOM_MARKERS:
        if marker not in warroom_text:
            failures.append(f"missing warroom marker: {marker}")
    for marker in FORBIDDEN_WARROOM_MARKERS:
        if marker in warroom_text:
            failures.append(f"forbidden warroom marker present: {marker}")
    for marker in REQUIRED_TEST_MARKERS:
        if marker not in test_text:
            failures.append(f"missing test marker: {marker}")
    if "PREDICTION_WARROOM_REALTIME_REVIEW_PREFLIGHT_VERSION" not in contract_text:
        failures.append("missing PS-Q13A contract dependency marker")

    payload = {
        "ok": not failures,
        "guard": "ps_q13b_warroom_realtime_review_panel",
        "integration": {
            "panel_present": PANEL.exists(),
            "warroom_page_integrated": "render_prediction_warroom_realtime_review_preflight_panel" in warroom_text,
            "display_only": True,
            "parameter_review_only": True,
            "no_autotrade_broker_ledger_runtime_write": True,
        },
        "failures": failures,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if not failures else 1


def test_ps_q13b_warroom_realtime_review_panel_guard() -> None:
    assert main() == 0


if __name__ == "__main__":
    raise SystemExit(main())
