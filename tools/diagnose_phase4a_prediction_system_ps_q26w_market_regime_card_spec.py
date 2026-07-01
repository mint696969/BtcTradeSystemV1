# path: ./tools/diagnose_phase4a_prediction_system_ps_q26w_market_regime_card_spec.py
# desc: Diagnostic for PS-Q26W market regime card specification foundation. Spec-only; no runtime writes or production UI changes.

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26W_MARKET_REGIME_CARD_SPEC_2026-07-01.md"
DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26w_market_regime_card_spec.v1"

REQUIRED_MARKERS = [
    "ps_q26w_market_regime_card_spec=true",
    "base_reentry=PS_Q26V_WARROOM_OPERATOR_FOCUS_ROUTE_TABLE_FOLD_DONE",
    "spec_only_change=true",
    "production_ui_code_changed=false",
    "runtime_code_changed=false",
    "warroom_page_changed=false",
    "warroom_page_slimming_main_goal=false",
    "market_regime_first=true",
    "future_prediction_card_reuse_expected=true",
    "freshness_badge_required=true",
    "freshness_not_encoded_by_border=true",
    "border_meaning=evidence_quality",
    "border_not_freshness=true",
    "background_color_never_encodes_freshness=true",
    "market_regime_diagnostic_record_required=true",
    "unknown_improvement_record_required=true",
    "low_confidence_improvement_record_required=true",
    "card_spec_reusable_for_future_prediction_cards=true",
    "confidence_is_not_directional_win_rate=true",
    "runtime_artifact_write_allowed=false",
    "status_artifact_write_allowed=false",
    "prediction_artifact_write_allowed=false",
    "view_artifact_write_allowed=false",
    "scheduler_enabled=false",
    "producer_enabled=false",
    "autotrade_trigger_allowed=false",
    "broker_private_api_allowed=false",
    "ledger_append=false",
    "mode_apply=false",
    "parameter_apply=false",
    "would_send_to_broker=false",
]

REQUIRED_REGIME_CODES = [
    "UP_TREND=上昇トレンド",
    "DOWN_TREND=下落トレンド",
    "RANGE=レンジ",
    "LOW_VOL_COMPRESSION=低ボラ・膠着",
    "HIGH_VOL_CHOP=高ボラ・乱高下",
    "BREAKOUT=ブレイク",
    "PANIC_SPIKE=急変・パニック",
    "REVERSAL_WATCH=転換候補",
    "UNKNOWN=予測不能",
]

REQUIRED_BACKGROUND_TONES = [
    "background_tone_good=淡い緑 / readable black text",
    "background_tone_caution=淡い黄 / readable black text",
    "background_tone_danger=淡い赤 / readable black text",
    "background_tone_unknown=かなり薄いグレー / readable black text",
]

REQUIRED_FRESHNESS_VALUES = ["freshness_badge_values=LIVE,WARM,STALE,MISSING"]
REQUIRED_EVIDENCE_VALUES = [
    "STRONG=根拠良好",
    "PARTIAL=根拠やや不足",
    "WEAK=根拠不足",
    "CONFLICTED=根拠衝突",
    "MISSING=根拠なし",
]

REQUIRED_REASON_CODES = [
    "DATA_MISSING",
    "STALE_INPUT",
    "SIGNAL_CONFLICT",
    "LOW_LIQUIDITY",
    "WIDE_SPREAD",
    "POST_SPIKE_UNSTABLE",
    "MODEL_DISAGREEMENT",
    "LOW_CONFIDENCE",
    "INSUFFICIENT_HISTORY",
    "NO_CLEAR_REGIME",
]


def run_market_regime_card_spec_diagnostic() -> dict:
    blockers: list[str] = []
    text = DOC.read_text(encoding="utf-8-sig") if DOC.exists() else ""
    if not DOC.exists():
        blockers.append("spec_doc_missing")

    for marker in REQUIRED_MARKERS:
        if marker not in text:
            blockers.append(f"required_marker_missing:{marker}")
    for marker in REQUIRED_REGIME_CODES:
        if marker not in text:
            blockers.append(f"regime_code_missing:{marker}")
    for marker in REQUIRED_BACKGROUND_TONES:
        if marker not in text:
            blockers.append(f"background_tone_missing:{marker}")
    for marker in REQUIRED_FRESHNESS_VALUES:
        if marker not in text:
            blockers.append(f"freshness_value_missing:{marker}")
    for marker in REQUIRED_EVIDENCE_VALUES:
        if marker not in text:
            blockers.append(f"evidence_quality_missing:{marker}")
    for marker in REQUIRED_REASON_CODES:
        if marker not in text:
            blockers.append(f"reason_code_missing:{marker}")

    contract = {
        "spec_only_change": True,
        "production_ui_code_changed": False,
        "runtime_code_changed": False,
        "warroom_page_changed": False,
        "warroom_page_slimming_main_goal": False,
        "market_regime_first": True,
        "future_prediction_card_reuse_expected": True,
        "regime_count_v1": len(REQUIRED_REGIME_CODES),
        "has_unknown_regime": "UNKNOWN=予測不能" in text,
        "background_tone_is_readability_first": True,
        "freshness_badge_required": True,
        "freshness_not_encoded_by_border": True,
        "border_meaning": "evidence_quality",
        "diagnostic_record_required": True,
        "unknown_improvement_record_required": True,
        "low_confidence_improvement_record_required": True,
        "confidence_is_not_directional_win_rate": True,
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
        "ledger_append": False,
        "mode_apply": False,
        "parameter_apply": False,
        "would_send_to_broker": False,
    }
    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "doc": str(DOC.relative_to(REPO_ROOT)).replace("\\", "/"),
        "contract": contract,
    }


def main() -> int:
    result = run_market_regime_card_spec_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
