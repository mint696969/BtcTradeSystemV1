# path: ./tools/diagnose_phase4a_prediction_system_ps_q26k_allowed_tech_term_label_help_text.py
# desc: Read-only diagnostic for PS-Q26K allowed technical term label/help text.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    WARROOM_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_VERSION,
    build_warroom_q26k_allowed_tech_term_label_help_text_packet,
    warroom_allowed_tech_term_help_rows,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_ALLOWED_TECH_TERM_HELP_TEXT_VERSION,
    build_latest_prediction_summary_widget_q18aj_q26k_allowed_tech_term_help_text_packet,
    latest_prediction_summary_widget_q18aj_searchable_plain_text,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_ALLOWED_TECH_TERM_HELP_TEXT_VERSION,
    build_latest_prediction_summary_widget_q18ak_q26k_allowed_tech_term_help_text_packet,
    latest_prediction_summary_widget_q18ak_searchable_plain_text,
)
from tools.diagnose_phase4a_prediction_system_ps_q26i_warroom_technical_term_allowlist_ui_review import run_warroom_technical_term_allowlist_ui_review_diagnostic  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26k_allowed_tech_term_label_help_text.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26K_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_2026-07-01.md"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
Q18AJ = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py"
Q18AK = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py"
COMP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_allowed_tech_term_label_help_text_q26k.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_allowed_tech_term_label_help_text_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    for marker in (
        "ps_q26k_allowed_tech_term_label_help_text=true",
        "allowed_technical_terms_preserved=true",
        "japanese_helper_wording_added=true",
        "warroom_page_helper_rows_added=true",
        "q18aj_helper_wording_added=true",
        "q18ak_helper_wording_added=true",
        "legacy_searchable_compatibility_preserved=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for path, markers in (
        (PAGE, ("WARROOM_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_VERSION", "warroom_allowed_tech_term_help_rows", "画面更新確認時刻", "実データprops接続")),
        (Q18AJ, ("LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_ALLOWED_TECH_TERM_HELP_TEXT_VERSION", "build_latest_prediction_summary_widget_q18aj_q26k_allowed_tech_term_help_text_packet", "heartbeat（画面更新確認時刻）", "予測artifact（生成済み予測ファイル）")),
        (Q18AK, ("LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_ALLOWED_TECH_TERM_HELP_TEXT_VERSION", "build_latest_prediction_summary_widget_q18ak_q26k_allowed_tech_term_help_text_packet", "fallbackは安全側の表示理由", "fragment path（枠内更新経路）")),
        (COMP_TEST, ("test_q26k_warroom_allowed_term_glossary_and_safety", "test_q26k_q18aj_q18ak_helper_wording_and_legacy_searchable_preserved")),
    ):
        text = _read(path)
        for marker in markers:
            if marker not in text:
                blockers.append(f"marker_required:{path.relative_to(REPO_ROOT)}:{marker}")
    page_packet = build_warroom_q26k_allowed_tech_term_label_help_text_packet()
    q18aj_packet = build_latest_prediction_summary_widget_q18aj_q26k_allowed_tech_term_help_text_packet()
    q18ak_packet = build_latest_prediction_summary_widget_q18ak_q26k_allowed_tech_term_help_text_packet()
    joined = json.dumps({"page": page_packet, "q18aj": q18aj_packet, "q18ak": q18ak_packet, "glossary": warroom_allowed_tech_term_help_rows()}, ensure_ascii=False)
    for label in ("heartbeat", "fallback", "runtime binding", "AutoTrade", "broker", "artifact", "fragment", "画面更新確認時刻", "安全側の表示理由", "実データprops接続", "枠内だけの表示更新"):
        if label not in joined:
            blockers.append(f"help_label_missing:{label}")
    if "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT" not in latest_prediction_summary_widget_q18aj_searchable_plain_text({}):
        blockers.append("q18aj_legacy_searchable_missing")
    if "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS" not in latest_prediction_summary_widget_q18ak_searchable_plain_text({}):
        blockers.append("q18ak_legacy_searchable_missing")
    q26i = run_warroom_technical_term_allowlist_ui_review_diagnostic()
    if q26i.get("legacy_compat_count") != 4:
        blockers.append(f"legacy_compat_count_changed:{q26i.get('legacy_compat_count')}")
    for name, packet in (("page", page_packet), ("q18aj", q18aj_packet), ("q18ak", q18ak_packet)):
        for key in ("read_only", "display_only", "non_executing"):
            if packet.get(key) is not True:
                blockers.append(f"{name}_true_required:{key}")
        for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
            if packet.get(key) is not False:
                blockers.append(f"{name}_false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "page_help_text_version": WARROOM_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_VERSION,
        "q18aj_help_text_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_ALLOWED_TECH_TERM_HELP_TEXT_VERSION,
        "q18ak_help_text_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_ALLOWED_TECH_TERM_HELP_TEXT_VERSION,
        "allowed_technical_terms_preserved": True,
        "japanese_helper_wording_added": True,
        "legacy_searchable_compatibility_preserved": q26i.get("legacy_compat_count") == 4,
        "q26i_legacy_compat_count": q26i.get("legacy_compat_count"),
        "q26i_review_candidate_count": q26i.get("review_candidate_count"),
        "term_count": page_packet.get("term_count"),
        "page_packet": page_packet,
        "q18aj_packet": q18aj_packet,
        "q18ak_packet": q18ak_packet,
        "recommended_next_slice": "PS_Q26L_WARROOM_JAPANESE_DISPLAY_FINAL_AUDIT_AND_STOP_POINT",
        "safety": {
            "read_only": True,
            "display_only": True,
            "non_executing": True,
            "trade_guidance_added": False,
            "trade_signal_added": False,
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
    result = run_allowed_tech_term_label_help_text_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
