# path: ./tools/diagnose_phase4a_prediction_system_ps_q26d_warroom_header_legacy_section_japanese_localization.py
# desc: Read-only diagnostic for PS-Q26D WarRoom header and legacy section Japanese localization.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    WARROOM_HEADER_LEGACY_SECTION_JAPANESE_LOCALIZATION_VERSION,
    _q26d_prediction_observation_plain_text,
    _q26d_prediction_observation_quick_status_rows,
    build_warroom_q26d_header_legacy_section_localization_packet,
)
from btcts.apps.operator_ui.components.warroom_header import (  # noqa: E402
    WARROOM_HEADER_SOURCE_JAPANESE_LOCALIZATION_VERSION,
    _q26d_header_source_label,
    build_warroom_header_q26d_source_localization_packet,
)
from btcts.apps.operator_ui.prediction_warroom.texts.latest_prediction_display_texts import DISPLAY_TEXTS  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26d_warroom_header_legacy_section_japanese_localization.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26D_WARROOM_HEADER_LEGACY_SECTION_JAPANESE_LOCALIZATION_2026-07-01.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
WARROOM_HEADER = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py"
DISPLAY_TEXTS_FILE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/texts/latest_prediction_display_texts.py"
COMP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_header_legacy_section_japanese_localization_q26d.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_header_legacy_section_japanese_localization_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    page = _read(WARROOM_PAGE)
    header = _read(WARROOM_HEADER)
    display_texts = _read(DISPLAY_TEXTS_FILE)
    comp_test = _read(COMP_TEST)
    for marker in (
        "ps_q26d_warroom_header_legacy_section_japanese_localization=true",
        "quick_status_japanese_localized=true",
        "legacy_section_titles_japanese_localized=true",
        "section_description_japanese_localized=true",
        "warroom_header_source_label_japanese_localized=true",
        "prediction_footer_token_japanese_localized=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_HEADER_LEGACY_SECTION_JAPANESE_LOCALIZATION_VERSION",
        "_q26d_prediction_observation_quick_status_rows",
        "PS-Q18AU 予測最新 quick status",
        "予測最新ステータス / quick status",
        "現在状態 nowcast / board・freshness",
        "リアルタイム予測表示 / read model",
    ):
        if marker not in page:
            blockers.append(f"page_marker_required:{marker}")
    for marker in (
        "WARROOM_HEADER_SOURCE_JAPANESE_LOCALIZATION_VERSION",
        "_q26d_header_source_label",
        "実行市場live基準 + research補助",
    ):
        if marker not in header:
            blockers.append(f"header_marker_required:{marker}")
    if '"footer_token": "PS-Q19I 予測表示の日本語説明"' not in display_texts:
        blockers.append("display_footer_token_japanese_required")
    for marker in (
        "test_q26d_quick_status_rows_are_japanese_and_safe",
        "test_q26d_header_source_and_footer_are_localized_and_safe",
    ):
        if marker not in comp_test:
            blockers.append(f"component_test_marker_required:{marker}")

    sample = {
        "read_order": "quick_status_then_searchable_tokens_then_legacy_preflight_details",
        "q18aq_manual_resmoke_result": "pass",
        "q18aj_auto_refresh_enabled": True,
        "q18aj_refresh_heartbeat_utc": "2026-07-01T00:00:00Z",
        "q18ak_freshness_state": "unknown",
        "q18ak_safe_fallback_reason_codes": ["auto_refresh_source_packet_not_ok", "source_generated_at_missing"],
        "implementation_gate_review_result": "blocked_not_ready_to_enable",
        "latest_prediction_observation_status": "ready_for_operator_review",
    }
    rows = _q26d_prediction_observation_quick_status_rows(sample)
    plain = _q26d_prediction_observation_plain_text(sample)
    joined = json.dumps(rows, ensure_ascii=False) + plain
    for token in ("quick_status_then_searchable_tokens_then_legacy_preflight_details", "ready_for_operator_review", "blocked_not_ready_to_enable"):
        if token in joined:
            blockers.append(f"quick_status_token_still_visible:{token}")
    if "実行市場live基準 + research補助" != _q26d_header_source_label("execution_market_live_canonical + research_experiment"):
        blockers.append("header_source_label_not_localized")
    page_packet = build_warroom_q26d_header_legacy_section_localization_packet()
    header_packet = build_warroom_header_q26d_source_localization_packet()
    for name, packet in (("page", page_packet), ("header", header_packet)):
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
        "quick_status_rows": rows,
        "quick_status_plain_text": plain,
        "page_packet": page_packet,
        "header_packet": header_packet,
        "footer_token_ja": DISPLAY_TEXTS["ja"].get("footer_token"),
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
    result = run_warroom_header_legacy_section_japanese_localization_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
