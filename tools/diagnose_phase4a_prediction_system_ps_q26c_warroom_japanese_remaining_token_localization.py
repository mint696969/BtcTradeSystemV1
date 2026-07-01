# path: ./tools/diagnose_phase4a_prediction_system_ps_q26c_warroom_japanese_remaining_token_localization.py
# desc: Read-only diagnostic for PS-Q26C WarRoom Japanese remaining token localization.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION,
    build_warroom_live_nowcast_q26c_remaining_token_localization_packet,
    warroom_live_nowcast_q26c_localize_display_rows,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION,
    build_latest_prediction_warroom_q26c_remaining_token_localization_packet,
    latest_prediction_warroom_q26c_localize_display_rows,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26c_warroom_japanese_remaining_token_localization.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26C_WARROOM_JAPANESE_REMAINING_TOKEN_LOCALIZATION_2026-07-01.md"
NOWCAST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
PRED = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
COMP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_japanese_remaining_token_localization_q26c.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_japanese_remaining_token_localization_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    nowcast_src = _read(NOWCAST)
    pred_src = _read(PRED)
    comp_test = _read(COMP_TEST)
    for marker in (
        "ps_q26c_warroom_japanese_remaining_token_localization=true",
        "nowcast_remaining_token_localization_added=true",
        "prediction_remaining_token_localization_added=true",
        "remaining_prediction_rows_readable_as_current_artifact_localized=true",
        "english_table_header_reduction=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_LIVE_NOWCAST_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION",
        "warroom_live_nowcast_q26c_localize_display_rows",
        "build_warroom_live_nowcast_q26c_remaining_token_localization_packet",
        "PS-Q26C 日本語化",
    ):
        if marker not in nowcast_src:
            blockers.append(f"nowcast_src_marker_required:{marker}")
    for marker in (
        "WARROOM_PREDICTION_JAPANESE_REMAINING_TOKEN_LOCALIZATION_VERSION",
        "latest_prediction_warroom_q26c_localize_display_rows",
        "build_latest_prediction_warroom_q26c_remaining_token_localization_packet",
        "prediction_rows_readable_as_current_artifact",
        "予測表示: 現在artifactとして読める",
        "PS-Q26C 日本語化",
    ):
        if marker not in pred_src:
            blockers.append(f"prediction_src_marker_required:{marker}")
    for marker in (
        "test_q26c_nowcast_detail_rows_get_japanese_columns_and_values",
        "test_q26c_prediction_remaining_token_is_localized_and_safe",
    ):
        if marker not in comp_test:
            blockers.append(f"component_test_marker_required:{marker}")

    nowcast_localized = warroom_live_nowcast_q26c_localize_display_rows([
        {"item": "current_state_score", "value": "14", "note": "weak_current_state"},
        {"layer": "foundation_integrity", "source": "collector_freshness", "status": "blocked", "reason": "freshness=stale_caution"},
    ])
    prediction_localized = latest_prediction_warroom_q26c_localize_display_rows([
        {"item": "prediction_tactical_readiness", "value": "prediction_rows_readable_as_current_artifact", "note": "short_horizon_expired_or_stale"},
    ])
    joined_prediction = json.dumps(prediction_localized, ensure_ascii=False)
    joined_nowcast = json.dumps(nowcast_localized, ensure_ascii=False)
    if "prediction_rows_readable_as_current_artifact" in joined_prediction:
        blockers.append("prediction_token_still_visible")
    if "予測表示: 現在artifactとして読める" not in joined_prediction:
        blockers.append("prediction_token_localized_label_missing")
    if "項目" not in joined_nowcast or "現在状態スコア" not in joined_nowcast:
        blockers.append("nowcast_column_or_token_localization_missing")
    nowcast_packet = build_warroom_live_nowcast_q26c_remaining_token_localization_packet()
    prediction_packet = build_latest_prediction_warroom_q26c_remaining_token_localization_packet()
    for name, packet in (("nowcast", nowcast_packet), ("prediction", prediction_packet)):
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
        "nowcast_localized_rows": nowcast_localized,
        "prediction_localized_rows": prediction_localized,
        "nowcast_packet": nowcast_packet,
        "prediction_packet": prediction_packet,
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
    result = run_warroom_japanese_remaining_token_localization_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
