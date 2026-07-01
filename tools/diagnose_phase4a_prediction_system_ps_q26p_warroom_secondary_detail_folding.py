# path: ./tools/diagnose_phase4a_prediction_system_ps_q26p_warroom_secondary_detail_folding.py
# desc: Diagnostic for PS-Q26P WarRoom secondary detail folding via externalized focus layout policy.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_focus_layout_policy import (  # noqa: E402
    build_warroom_focus_layout_policy_packet,
    warroom_focus_section_expanded,
    warroom_focus_section_label,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26p_warroom_secondary_detail_folding.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26P_WARROOM_SECONDARY_DETAIL_FOLDING_2026-07-01.md"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
POLICY = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_focus_layout_policy.py"
APP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_secondary_detail_folding_q26p.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_secondary_detail_folding_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    page = _read(PAGE)
    policy = _read(POLICY)
    app_test = _read(APP_TEST)
    for marker in (
        "ps_q26p_warroom_secondary_detail_folding=true",
        "secondary_detail_sections_folded_default=true",
        "market_evidence_detail_folded_default=true",
        "operator_support_detail_folded_default=true",
        "warroom_page_change_boundary=import_and_policy_lookup_only",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        'warroom_focus_section_expanded("header_alert_operator")',
        'warroom_focus_section_expanded("market_evidence_detail")',
        'warroom_focus_section_expanded("operator_support_detail")',
        'warroom_focus_section_label("market_evidence_detail")',
        'warroom_focus_section_label("operator_support_detail")',
    ):
        if marker not in page:
            blockers.append(f"page_marker_required:{marker}")
    for marker in (
        '"market_evidence_detail": False',
        '"operator_support_detail": False',
        "secondary_detail_sections_folded_default",
    ):
        if marker not in policy:
            blockers.append(f"policy_marker_required:{marker}")
    for marker in (
        "test_q26p_secondary_detail_policy_folds_priority_4_and_5_sections",
        "test_q26p_warroom_page_wraps_secondary_details_in_policy_sections",
    ):
        if marker not in app_test:
            blockers.append(f"test_marker_required:{marker}")

    packet = build_warroom_focus_layout_policy_packet()
    if warroom_focus_section_label("market_evidence_detail") != "市場証拠 / graph / active event":
        blockers.append("market_evidence_detail_label_mismatch")
    if warroom_focus_section_expanded("market_evidence_detail") is not False:
        blockers.append("market_evidence_detail_not_folded_default")
    if warroom_focus_section_expanded("operator_support_detail") is not False:
        blockers.append("operator_support_detail_not_folded_default")
    if warroom_focus_section_expanded("header_alert_operator") is not True:
        blockers.append("header_alert_operator_not_expanded_default")
    if packet.get("secondary_detail_sections_folded_default") is not True:
        blockers.append("secondary_detail_sections_folded_default_not_true")
    for key in ("read_only", "display_only", "non_executing", "layout_only_change", "keeps_existing_panels_available"):
        if packet.get(key) is not True:
            blockers.append(f"packet_true_required:{key}")
    for key in ("runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if packet.get(key) is not False:
            blockers.append(f"packet_false_required:{key}")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "packet": packet,
        "safety": {
            "production_ui_code_changed": True,
            "layout_only_change": True,
            "externalized_layout_policy_module": True,
            "warroom_page_change_boundary": "import_and_policy_lookup_only",
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "runtime_artifact_write_allowed": False,
            "status_artifact_write_allowed": False,
            "prediction_artifact_write_allowed": False,
            "view_artifact_write_allowed": False,
            "scheduler_enabled": False,
            "producer_enabled": False,
            "autotrade_trigger_allowed": False,
            "broker_private_api_allowed": False,
            "ledger_append_allowed": False,
            "mode_apply_allowed": False,
            "parameter_apply_allowed": False,
            "would_send_to_broker": False,
        },
    }


def main() -> int:
    result = run_warroom_secondary_detail_folding_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
