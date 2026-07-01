# path: ./tools/diagnose_phase4a_prediction_system_ps_q26e_warroom_telemetry_footer_detail_note_localization.py
# desc: Read-only diagnostic for PS-Q26E WarRoom telemetry footer and detail-note localization.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION,
    build_latest_prediction_warroom_q26e_telemetry_footer_detail_note_localization_packet,
    latest_prediction_warroom_q26e_telemetry_footer_text,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION,
    build_warroom_live_nowcast_q26e_telemetry_footer_detail_note_localization_packet,
    warroom_live_nowcast_q26e_localize_display_rows,
    warroom_live_nowcast_q26e_telemetry_footer_text,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26e_warroom_telemetry_footer_detail_note_localization.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26E_WARROOM_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_2026-07-01.md"
PRED = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
NOWCAST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
TEXTS = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/texts/latest_prediction_display_texts.py"
COMP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_telemetry_footer_detail_note_localization_q26e.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_telemetry_footer_detail_note_localization_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    pred_src = _read(PRED)
    nowcast_src = _read(NOWCAST)
    texts_src = _read(TEXTS)
    comp_test = _read(COMP_TEST)
    for marker in (
        "ps_q26e_warroom_telemetry_footer_detail_note_localization=true",
        "prediction_telemetry_footer_japanese_localized=true",
        "nowcast_telemetry_footer_japanese_localized=true",
        "detail_note_token_fragments_localized=true",
        "visible_autotrade_broker_false_fragments_reduced=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_PREDICTION_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION",
        "latest_prediction_warroom_q26e_telemetry_footer_text",
        "build_latest_prediction_warroom_q26e_telemetry_footer_detail_note_localization_packet",
        "PS-Q26E telemetry",
    ):
        if marker not in pred_src:
            blockers.append(f"prediction_src_marker_required:{marker}")
    for marker in (
        "WARROOM_LIVE_NOWCAST_TELEMETRY_FOOTER_DETAIL_NOTE_LOCALIZATION_VERSION",
        "warroom_live_nowcast_q26e_telemetry_footer_text",
        "warroom_live_nowcast_q26e_localize_display_rows",
        "PS-Q26E nowcast telemetry",
    ):
        if marker not in nowcast_src:
            blockers.append(f"nowcast_src_marker_required:{marker}")
    if "表示書込=なし" not in texts_src or "AutoTrade=なし" not in texts_src or "broker=なし" not in texts_src:
        blockers.append("text_catalog_caption_line_not_localized")
    for marker in ("test_q26e_prediction_footer_is_japanese_and_safe", "test_q26e_nowcast_footer_and_notes_are_japanese_and_safe"):
        if marker not in comp_test:
            blockers.append(f"component_test_marker_required:{marker}")

    prediction_footer = latest_prediction_warroom_q26e_telemetry_footer_text({"freshness_state": "fresh", "prediction_row_count": 24, "generated_at": "2026-07-01T00:00:00Z"}, lang="ja")
    nowcast_footer = warroom_live_nowcast_q26e_telemetry_footer_text({"current_state_summary": "current_market_state_live_observable", "nowcast_freshness_state": "live", "market_event_age_sec": 0, "spread_bps": 1.2})
    localized_rows = warroom_live_nowcast_q26e_localize_display_rows([{"item": "operator_instruction", "value": "x", "note": "not a trade instruction"}])
    joined = json.dumps({"prediction_footer": prediction_footer, "nowcast_footer": nowcast_footer, "localized_rows": localized_rows}, ensure_ascii=False)
    for token in ("view_artifact_write_allowed=false", "autotrade=false", "broker=false", "not a trade instruction"):
        if token in joined:
            blockers.append(f"visible_token_still_present:{token}")
    for required in ("表示専用", "AutoTrade=なし", "broker=なし", "売買指示ではありません"):
        if required not in joined:
            blockers.append(f"localized_label_missing:{required}")
    prediction_packet = build_latest_prediction_warroom_q26e_telemetry_footer_detail_note_localization_packet()
    nowcast_packet = build_warroom_live_nowcast_q26e_telemetry_footer_detail_note_localization_packet()
    for name, packet in (("prediction", prediction_packet), ("nowcast", nowcast_packet)):
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
        "prediction_footer": prediction_footer,
        "nowcast_footer": nowcast_footer,
        "localized_rows": localized_rows,
        "prediction_packet": prediction_packet,
        "nowcast_packet": nowcast_packet,
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
    result = run_warroom_telemetry_footer_detail_note_localization_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
