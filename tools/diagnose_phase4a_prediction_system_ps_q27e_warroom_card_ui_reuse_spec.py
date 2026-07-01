# path: ./tools/diagnose_phase4a_prediction_system_ps_q27e_warroom_card_ui_reuse_spec.py
# desc: Diagnostic for PS-Q27E WarRoom card UI reuse specification. Spec-only; verifies Q27D remains ready.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.diagnose_phase4a_prediction_system_ps_q27d_market_regime_card_typography_badge_tune import run_market_regime_card_typography_badge_tune_diagnostic  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q27e_warroom_card_ui_reuse_spec.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27E_WARROOM_CARD_UI_REUSE_SPEC_2026-07-02.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_card_ui_reuse_spec_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    q27d = run_market_regime_card_typography_badge_tune_diagnostic()
    packet = q27d.get("packet") if isinstance(q27d.get("packet"), dict) else {}

    for marker in (
        "ps_q27e_warroom_card_ui_reuse_spec=true",
        "base_reentry=PS_Q27D_MARKET_REGIME_CARD_TYPOGRAPHY_BADGE_TUNE_DONE",
        "selected_lane=WARROOM_CARD_UI_REUSE_SPECIFICATION",
        "spec_only_change=true",
        "production_ui_code_changed=false",
        "warroom_page_changed=false",
        "market_regime_card_ui_is_canonical_reference=true",
        "future_prediction_card_reuse_expected=true",
        "next_thread_ready_for_market_regime_live_data_binding_design=true",
        "card_width_px=208",
        "horizon_font_size_rem=0.92rem",
        "primary_label_font_size_rem=1.14rem",
        "confidence_font_size_rem=1.60rem",
        "short_tag_font_size_rem=1.04rem",
        "freshness_badge_font_size_rem=0.78rem",
        "freshness_badge_font_weight=900",
        "freshness_badge_min_width_px=42",
        "freshness_encoded_by_badge_only=true",
        "border_meaning=evidence_quality",
        "detail_disclosure_mode=card_overlay",
        "overlay_covers_card_row=true",
        "overlay_close_button_enabled=true",
        "detail_overlay_background=#F2F4F7",
        "detail_overlay_background_matches_unknown=true",
        "diagnostic_record_required_for_unknown_and_low_confidence=true",
        "live_data_connected=false",
        "runtime_read_allowed=false",
        "would_send_to_broker=false",
        "Next target: MARKET_REGIME_CARD_LIVE_DATA_BINDING_DESIGN",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")

    if q27d.get("ready") is not True:
        blockers.append("q27d_diagnostic_not_ready")
    expected_packet = {
        "card_width_px": 208,
        "horizon_font_size_rem": "0.92rem",
        "regime_font_size_rem": "1.14rem",
        "confidence_font_size_rem": "1.60rem",
        "tag_font_size_rem": "1.04rem",
        "freshness_badge_font_size_rem": "0.78rem",
        "freshness_badge_font_weight": 900,
        "freshness_badge_min_width_px": 42,
        "detail_disclosure_mode": "card_overlay",
        "detail_overlay_background": "#F2F4F7",
        "detail_overlay_background_matches_unknown": True,
        "sample_data_only": True,
        "live_data_connected": False,
        "runtime_read_allowed": False,
        "warroom_page_changed": False,
    }
    for key, value in expected_packet.items():
        if packet.get(key) != value:
            blockers.append(f"q27d_packet_value_required:{key}={value!r}")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "doc": str(DOC.relative_to(REPO_ROOT)).replace("\\", "/"),
        "q27d_ready": q27d.get("ready"),
        "q27d_head_contract": {
            "card_width_px": packet.get("card_width_px"),
            "horizon_font_size_rem": packet.get("horizon_font_size_rem"),
            "regime_font_size_rem": packet.get("regime_font_size_rem"),
            "confidence_font_size_rem": packet.get("confidence_font_size_rem"),
            "tag_font_size_rem": packet.get("tag_font_size_rem"),
            "freshness_badge_font_size_rem": packet.get("freshness_badge_font_size_rem"),
            "freshness_badge_font_weight": packet.get("freshness_badge_font_weight"),
            "freshness_badge_min_width_px": packet.get("freshness_badge_min_width_px"),
            "detail_disclosure_mode": packet.get("detail_disclosure_mode"),
            "detail_overlay_background": packet.get("detail_overlay_background"),
            "detail_overlay_background_matches_unknown": packet.get("detail_overlay_background_matches_unknown"),
        },
        "contract": {
            "spec_only_change": True,
            "market_regime_card_ui_is_canonical_reference": True,
            "future_prediction_card_reuse_expected": True,
            "next_thread_ready_for_market_regime_live_data_binding_design": True,
            "production_ui_code_changed": False,
            "runtime_code_changed": False,
            "warroom_page_changed": False,
            "live_data_connected": False,
            "runtime_read_allowed": False,
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
    result = run_warroom_card_ui_reuse_spec_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
