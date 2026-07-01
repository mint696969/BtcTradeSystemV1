# path: ./tools/diagnose_phase4a_prediction_system_ps_q26h_warroom_top_reading_caption_japanese_localization.py
# desc: Read-only diagnostic for PS-Q26H WarRoom top reading caption and page-level token Japanese localization.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_page import (  # noqa: E402
    WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_VERSION,
    _q26h_observation_plain_text,
    _q26h_observation_quick_status_rows,
    _warroom_reading_block_captions,
    build_warroom_q26h_top_reading_caption_japanese_localization_packet,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26h_warroom_top_reading_caption_japanese_localization.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26H_WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_2026-07-01.md"
PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
COMP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_top_reading_caption_japanese_localization_q26h.py"
VISIBLE_FORBIDDEN = ("real_render=false", "runtime binding=false", "autotrade=false", "broker=false", "read current regime", "read tactic stance")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def _sample_packet() -> dict:
    return {
        "latest_prediction_observation_status": "ready_for_operator_review",
        "q18aq_manual_resmoke_result": "pass",
        "q18ak_freshness_state": "unknown",
        "q18ak_safe_fallback_reason_codes": ["source_generated_at_missing"],
        "q18aj_refresh_heartbeat_utc": "2026-07-01T00:00:00Z",
        "implementation_gate_review_result": "blocked_not_ready_to_enable",
        "read_order": "quick_status_then_searchable_tokens_then_legacy_preflight_details",
        "q18aj_auto_refresh_enabled": True,
    }


def run_warroom_top_reading_caption_japanese_localization_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    page = _read(PAGE)
    comp_test = _read(COMP_TEST)
    for marker in (
        "ps_q26h_warroom_top_reading_caption_japanese_localization=true",
        "reading_block_captions_japanese_localized=true",
        "quick_status_plain_text_japanese_localized=true",
        "quick_status_rows_japanese_localized=true",
        "page_level_false_fragments_reduced=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_VERSION",
        "_q26h_observation_plain_text",
        "_q26h_observation_quick_status_rows",
        "build_warroom_q26h_top_reading_caption_japanese_localization_packet",
        "現在の市場summary",
        "PS-Q26H 予測最新ステータス",
    ):
        if marker not in page:
            blockers.append(f"page_marker_required:{marker}")
    for marker in (
        "test_q26h_reading_block_captions_are_japanese",
        "test_q26h_quick_status_plain_text_and_rows_are_japanese_and_safe",
    ):
        if marker not in comp_test:
            blockers.append(f"component_test_marker_required:{marker}")
    captions = _warroom_reading_block_captions()
    plain = _q26h_observation_plain_text(_sample_packet())
    rows = _q26h_observation_quick_status_rows(_sample_packet())
    joined = json.dumps({"captions": captions, "plain": plain, "rows": rows}, ensure_ascii=False)
    for token in VISIBLE_FORBIDDEN:
        if token in joined:
            blockers.append(f"visible_token_still_present:{token}")
    for label in ("現在の市場summary", "予測はreview補助", "安全fallback理由=生成時刻が欠落", "実render=なし", "AutoTrade=なし", "broker=なし"):
        if label not in joined:
            blockers.append(f"localized_label_missing:{label}")
    packet = build_warroom_q26h_top_reading_caption_japanese_localization_packet()
    for key in ("read_only", "display_only", "non_executing"):
        if packet.get(key) is not True:
            blockers.append(f"true_required:{key}")
    for key in ("trade_guidance_added", "trade_signal_added", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if packet.get(key) is not False:
            blockers.append(f"false_required:{key}")
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "localization_version": WARROOM_TOP_READING_CAPTION_JAPANESE_LOCALIZATION_VERSION,
        "captions": captions,
        "sample_plain_text": plain,
        "sample_row_count": len(rows),
        "packet": packet,
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
    result = run_warroom_top_reading_caption_japanese_localization_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
