# path: ./tools/diagnose_phase4a_prediction_system_ps_q26g_q18aj_q18ak_legacy_panel_japanese_localization.py
# desc: Read-only diagnostic for PS-Q26G Q18AJ/Q18AK legacy panel Japanese localization.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_JAPANESE_LOCALIZATION_VERSION,
    build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet,
    build_latest_prediction_summary_widget_q18aj_japanese_localization_packet,
    latest_prediction_summary_widget_q18aj_searchable_plain_text,
    latest_prediction_summary_widget_q18aj_visible_display_rows,
    latest_prediction_summary_widget_q18aj_visible_plain_text,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel import (  # noqa: E402
    LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_JAPANESE_LOCALIZATION_VERSION,
    build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet,
    build_latest_prediction_summary_widget_q18ak_japanese_localization_packet,
    latest_prediction_summary_widget_q18ak_searchable_plain_text,
    latest_prediction_summary_widget_q18ak_visible_display_rows,
    latest_prediction_summary_widget_q18ak_visible_plain_text,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26g_q18aj_q18ak_legacy_panel_japanese_localization.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26G_Q18AJ_Q18AK_LEGACY_PANEL_JAPANESE_LOCALIZATION_2026-07-01.md"
Q18AJ = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel.py"
Q18AK = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel.py"
COMP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_q18aj_q18ak_legacy_panel_japanese_localization_q26g.py"

VISIBLE_FORBIDDEN = (
    "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT",
    "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS",
    "autotrade=false",
    "broker=false",
    "writes=false",
    "real_render=false",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""



def _q26g_stale_q18aj_source_packet() -> dict[str, object]:
    return {
        "ok": True,
        "component_source_generated_at": "2026-06-24T03:00:00Z",
        "auto_refresh_enabled": True,
        "fragment_slot_refresh_path_enabled": True,
        "partial_update_enabled": True,
        "broad_page_reload_disabled": True,
        "refresh_mode": "poll_normal",
        "refresh_interval_sec": 5,
        "runtime_artifact_write_allowed": False,
        "status_artifact_write_allowed": False,
        "autotrade_trigger_allowed": False,
        "broker_private_api_allowed": False,
        "parameter_apply_allowed": False,
        "ledger_append_allowed": False,
    }

def run_q18aj_q18ak_legacy_panel_japanese_localization_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    q18aj_src = _read(Q18AJ)
    q18ak_src = _read(Q18AK)
    comp_test = _read(COMP_TEST)
    for marker in (
        "ps_q26g_q18aj_q18ak_legacy_panel_japanese_localization=true",
        "q18aj_visible_plain_text_japanese_localized=true",
        "q18ak_visible_plain_text_japanese_localized=true",
        "legacy_searchable_plain_text_preserved=true",
        "q18ap_compatibility_preserved=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_JAPANESE_LOCALIZATION_VERSION",
        "latest_prediction_summary_widget_q18aj_visible_plain_text",
        "latest_prediction_summary_widget_q18aj_visible_display_rows",
        "PS-Q26G Q18AJ 更新確認",
        "latest_prediction_summary_widget_q18aj_searchable_plain_text",
        "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT",
    ):
        if marker not in q18aj_src:
            blockers.append(f"q18aj_src_marker_required:{marker}")
    for marker in (
        "LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_JAPANESE_LOCALIZATION_VERSION",
        "latest_prediction_summary_widget_q18ak_visible_plain_text",
        "latest_prediction_summary_widget_q18ak_visible_display_rows",
        "PS-Q26G Q18AK 鮮度/fallback確認",
        "latest_prediction_summary_widget_q18ak_searchable_plain_text",
        "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS",
    ):
        if marker not in q18ak_src:
            blockers.append(f"q18ak_src_marker_required:{marker}")
    for marker in (
        "test_q26g_q18aj_visible_text_localized_but_legacy_searchable_preserved",
        "test_q26g_q18ak_visible_text_localized_but_legacy_searchable_preserved",
    ):
        if marker not in comp_test:
            blockers.append(f"component_test_marker_required:{marker}")

    q18aj_packet = build_latest_prediction_summary_widget_q18aj_bounded_auto_refresh_panel_packet()
    q18ak_packet = build_latest_prediction_summary_widget_q18ak_freshness_error_fallback_panel_packet(
        supplied_q18aj_bounded_auto_refresh_packet=_q26g_stale_q18aj_source_packet(),
        now_utc="2026-06-24T04:57:45Z",
    )
    q18aj_visible = latest_prediction_summary_widget_q18aj_visible_plain_text(q18aj_packet)
    q18ak_visible = latest_prediction_summary_widget_q18ak_visible_plain_text(q18ak_packet)
    q18aj_rows = latest_prediction_summary_widget_q18aj_visible_display_rows(q18aj_packet)
    q18ak_rows = latest_prediction_summary_widget_q18ak_visible_display_rows(q18ak_packet)
    q18aj_legacy = latest_prediction_summary_widget_q18aj_searchable_plain_text(q18aj_packet)
    q18ak_legacy = latest_prediction_summary_widget_q18ak_searchable_plain_text(q18ak_packet)
    visible_joined = json.dumps({"q18aj_visible": q18aj_visible, "q18ak_visible": q18ak_visible, "q18aj_rows": q18aj_rows, "q18ak_rows": q18ak_rows}, ensure_ascii=False)
    for token in VISIBLE_FORBIDDEN:
        if token in visible_joined:
            blockers.append(f"visible_token_still_present:{token}")
    for label in ("自動更新", "広域ページreload=なし", "AutoTrade=なし", "broker=なし", "fallback理由", "生成時刻が古い"):
        if label not in visible_joined:
            blockers.append(f"localized_label_missing:{label}")
    if "PS_Q18AP_SEARCHABLE_REFRESH_HEARTBEAT" not in q18aj_legacy:
        blockers.append("q18aj_legacy_searchable_token_not_preserved")
    if "PS_Q18AP_SEARCHABLE_FRESHNESS_STATUS" not in q18ak_legacy:
        blockers.append("q18ak_legacy_searchable_token_not_preserved")
    q18aj_loc = build_latest_prediction_summary_widget_q18aj_japanese_localization_packet()
    q18ak_loc = build_latest_prediction_summary_widget_q18ak_japanese_localization_packet()
    for name, packet in (("q18aj", q18aj_loc), ("q18ak", q18ak_loc)):
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
        "q18aj_localization_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AJ_JAPANESE_LOCALIZATION_VERSION,
        "q18ak_localization_version": LATEST_PREDICTION_SUMMARY_WIDGET_Q18AK_JAPANESE_LOCALIZATION_VERSION,
        "q18aj_visible_plain_text": q18aj_visible,
        "q18ak_visible_plain_text": q18ak_visible,
        "q18aj_visible_row_count": len(q18aj_rows),
        "q18ak_visible_row_count": len(q18ak_rows),
        "legacy_searchable_plain_text_preserved": True,
        "q18ap_compatibility_preserved": True,
        "q18aj_packet": q18aj_loc,
        "q18ak_packet": q18ak_loc,
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
    result = run_q18aj_q18ak_legacy_panel_japanese_localization_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
