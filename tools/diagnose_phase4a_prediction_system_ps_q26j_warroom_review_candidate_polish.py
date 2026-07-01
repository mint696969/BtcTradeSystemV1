# path: ./tools/diagnose_phase4a_prediction_system_ps_q26j_warroom_review_candidate_polish.py
# desc: Read-only diagnostic for PS-Q26J WarRoom operator-visible review-candidate polish.

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

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_live_market_nowcast_panel import (  # noqa: E402
    WARROOM_LIVE_NOWCAST_REVIEW_CANDIDATE_POLISH_VERSION,
    build_warroom_live_market_nowcast_packet,
    build_warroom_live_nowcast_operator_summary_packet,
    build_warroom_live_nowcast_q26j_review_candidate_polish_packet,
    build_warroom_live_nowcast_source_importance_packet,
    warroom_live_nowcast_operator_summary_rows,
    warroom_live_nowcast_source_layer_summary_rows,
)
from btcts.apps.operator_ui.prediction_warroom.panels.latest_prediction_warroom_read_model_display_panel import (  # noqa: E402
    WARROOM_PREDICTION_REVIEW_CANDIDATE_POLISH_VERSION,
    build_latest_prediction_warroom_q26j_review_candidate_polish_packet,
    latest_prediction_warroom_q26e_telemetry_footer_text,
)
from tools.diagnose_phase4a_prediction_system_ps_q26i_warroom_technical_term_allowlist_ui_review import run_warroom_technical_term_allowlist_ui_review_diagnostic  # noqa: E402

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26j_warroom_review_candidate_polish.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26J_WARROOM_REVIEW_CANDIDATE_POLISH_2026-07-01.md"
NOWCAST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_live_market_nowcast_panel.py"
PRED = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/latest_prediction_warroom_read_model_display_panel.py"
COMP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_review_candidate_polish_q26j.py"
BASELINE_REVIEW_CANDIDATE_COUNT = 45


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_warroom_review_candidate_polish_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    nowcast_src = _read(NOWCAST)
    pred_src = _read(PRED)
    comp_test = _read(COMP_TEST)
    for marker in (
        "ps_q26j_warroom_review_candidate_polish=true",
        "operator_visible_review_candidates_polished=true",
        "q26i_review_candidate_count_baseline=45",
        "q26i_review_candidate_count_after_q26j_less_than_baseline=true",
        "allowlisted_technical_terms_preserved=true",
        "legacy_searchable_compatibility_preserved=true",
        "trade_guidance_added=false",
        "trade_signal_added=false",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "WARROOM_LIVE_NOWCAST_REVIEW_CANDIDATE_POLISH_VERSION",
        "build_warroom_live_nowcast_q26j_review_candidate_polish_packet",
        "現在状態nowcastです。未来予測でも売買指示でもありません。",
        "表示専用の現在状態レイヤー",
        "現在状態の確認のみ",
    ):
        if marker not in nowcast_src:
            blockers.append(f"nowcast_marker_required:{marker}")
    for marker in (
        "WARROOM_PREDICTION_REVIEW_CANDIDATE_POLISH_VERSION",
        "build_latest_prediction_warroom_q26j_review_candidate_polish_packet",
        "view artifact write=none AutoTrade=none broker=none",
    ):
        if marker not in pred_src:
            blockers.append(f"prediction_marker_required:{marker}")
    for marker in (
        "test_q26j_nowcast_operator_visible_review_candidate_text_polished",
        "test_q26j_prediction_footer_false_fragments_polished",
    ):
        if marker not in comp_test:
            blockers.append(f"component_test_marker_required:{marker}")

    nowcast_packet = build_warroom_live_market_nowcast_packet(sources={}, fragment_enabled=True)
    summary = build_warroom_live_nowcast_operator_summary_packet(nowcast_packet, lang="ja")
    layering = build_warroom_live_nowcast_source_importance_packet(nowcast_packet, summary, lang="ja")
    rows_joined = json.dumps({"summary_rows": warroom_live_nowcast_operator_summary_rows(summary), "layer_rows": warroom_live_nowcast_source_layer_summary_rows(layering)}, ensure_ascii=False)
    footer_en = latest_prediction_warroom_q26e_telemetry_footer_text({"freshness_state": "fresh", "prediction_row_count": 3, "generated_at": "2026-07-01T00:00:00Z"}, lang="en")
    for token in ("current-state guidance only", "display-only current-state layer", "current-state nowcast; not a future prediction"):
        if token in rows_joined or token in str(nowcast_packet.get("operator_note")):
            blockers.append(f"operator_visible_review_candidate_still_present:{token}")
    for token in ("view_artifact_write_allowed=false", "autotrade=false", "broker=false"):
        if token in footer_en:
            blockers.append(f"prediction_footer_false_fragment_still_present:{token}")
    for label in ("表示専用の現在状態レイヤー", "現在状態の確認のみ", "view artifact write=none", "AutoTrade=none", "broker=none"):
        if label not in rows_joined and label not in footer_en:
            blockers.append(f"localized_or_polished_label_missing:{label}")

    q26i_after = run_warroom_technical_term_allowlist_ui_review_diagnostic()
    after_count = q26i_after.get("review_candidate_count")
    if not isinstance(after_count, int) or after_count >= BASELINE_REVIEW_CANDIDATE_COUNT:
        blockers.append(f"review_candidate_count_not_reduced:{after_count}")
    if q26i_after.get("legacy_compat_count") != 4:
        blockers.append(f"legacy_compat_count_changed:{q26i_after.get('legacy_compat_count')}")

    nowcast_loc = build_warroom_live_nowcast_q26j_review_candidate_polish_packet()
    pred_loc = build_latest_prediction_warroom_q26j_review_candidate_polish_packet()
    for name, packet in (("nowcast", nowcast_loc), ("prediction", pred_loc)):
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
        "baseline_review_candidate_count": BASELINE_REVIEW_CANDIDATE_COUNT,
        "post_q26j_review_candidate_count": after_count,
        "post_q26j_allowlist_hit_count": q26i_after.get("allowlist_hit_count"),
        "post_q26j_legacy_compat_count": q26i_after.get("legacy_compat_count"),
        "operator_visible_review_candidates_polished": True,
        "allowlisted_technical_terms_preserved": True,
        "legacy_searchable_compatibility_preserved": q26i_after.get("legacy_compat_count") == 4,
        "nowcast_polish_version": WARROOM_LIVE_NOWCAST_REVIEW_CANDIDATE_POLISH_VERSION,
        "prediction_polish_version": WARROOM_PREDICTION_REVIEW_CANDIDATE_POLISH_VERSION,
        "nowcast_packet": nowcast_loc,
        "prediction_packet": pred_loc,
        "recommended_next_slice": "PS_Q26K_WARROOM_ALLOWED_TECH_TERM_LABEL_HELP_TEXT_DISPLAY_ONLY",
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
    result = run_warroom_review_candidate_polish_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True, default=str))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
