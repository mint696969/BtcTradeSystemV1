# path: ./tools/diagnose_phase4a_prediction_system_ps_q26x_market_regime_card_contract.py
# desc: Diagnostic for PS-Q26X market regime card pure-data contract helpers.

from __future__ import annotations

import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "btcts_next" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.contracts.market_regime_card_contract import (  # noqa: E402
    BackgroundTone,
    EvidenceQuality,
    FreshnessBadge,
    MarketRegimeCode,
    RegimeDiagnosticReason,
    ShortTag,
    build_market_regime_card_contract_report,
    build_market_regime_card_spec,
    build_unknown_market_regime_diagnostic_record,
)

DIAGNOSTIC_VERSION = "prediction_warroom.ps_q26x_market_regime_card_contract.v1"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q26X_MARKET_REGIME_CARD_CONTRACT_2026-07-01.md"
CONTRACT = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/contracts/market_regime_card_contract.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
APP_TEST = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_card_contract_q26x.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig") if path.exists() else ""


def run_market_regime_card_contract_diagnostic() -> dict:
    blockers: list[str] = []
    doc = _read(DOC)
    contract_text = _read(CONTRACT)
    page_text = _read(WARROOM_PAGE)
    app_test = _read(APP_TEST)
    for marker in (
        "ps_q26x_market_regime_card_contract=true",
        "base_reentry=PS_Q26W_MARKET_REGIME_CARD_SPEC_DONE",
        "contract_helper_only=true",
        "production_ui_code_changed=false",
        "warroom_page_changed=false",
        "runtime_code_changed=false",
        "streamlit_render_allowed=false",
        "freshness_encoded_by_badge_only=true",
        "border_meaning=evidence_quality",
        "unknown_improvement_record_required=true",
        "low_confidence_improvement_record_required=true",
        "would_send_to_broker=false",
    ):
        if marker not in doc:
            blockers.append(f"doc_marker_required:{marker}")
    for marker in (
        "MARKET_REGIME_CARD_CONTRACT_VERSION",
        "class MarketRegimeCode",
        "class BackgroundTone",
        "class FreshnessBadge",
        "class EvidenceQuality",
        "class RegimeDiagnosticReason",
        "class MarketRegimeDiagnosticRecord",
        "def build_market_regime_card_spec",
        "def build_unknown_market_regime_diagnostic_record",
        "def build_market_regime_card_contract_report",
        "freshness_encoded_by_badge_only",
        "border_meaning",
    ):
        if marker not in contract_text:
            blockers.append(f"contract_marker_required:{marker}")
    if "MARKET_REGIME_CARD_CONTRACT_VERSION" in page_text or "build_market_regime_card_spec" in page_text:
        blockers.append("warroom_page_should_not_import_market_regime_contract_yet")
    for marker in (
        "test_q26x_contract_report_matches_q26w_spec",
        "test_q26x_card_spec_uses_three_lines_badge_and_evidence_border",
        "test_q26x_unknown_record_preserves_improvement_reasons",
        "test_q26x_does_not_touch_warroom_page",
    ):
        if marker not in app_test:
            blockers.append(f"test_marker_required:{marker}")

    report = build_market_regime_card_contract_report()
    if report.get("ok") is not True:
        blockers.append("contract_report_not_ok")
    if len(report.get("regime_codes") or []) != 9:
        blockers.append("regime_code_count_mismatch")
    if "UNKNOWN" not in (report.get("regime_codes") or []):
        blockers.append("unknown_regime_missing")
    for key in ("freshness_encoded_by_badge_only", "background_tone_is_readability_first", "unknown_regime_available", "diagnostic_record_required_for_unknown_and_low_confidence", "pure_data_contract_only"):
        if report.get(key) is not True:
            blockers.append(f"report_true_required:{key}")
    for key in ("production_ui_code_changed", "warroom_page_changed", "streamlit_render_allowed", "streamlit_render_invoked", "runtime_read_allowed", "runtime_artifact_write_allowed", "status_artifact_write_allowed", "prediction_artifact_write_allowed", "view_artifact_write_allowed", "scheduler_enabled", "producer_enabled", "autotrade_trigger_allowed", "broker_private_api_allowed", "ledger_append_allowed", "mode_apply_allowed", "parameter_apply_allowed", "would_send_to_broker"):
        if report.get(key) is not False:
            blockers.append(f"report_false_required:{key}")

    unknown_record = build_unknown_market_regime_diagnostic_record(
        record_id="diag-q26x-example",
        created_at_utc="2026-07-01T00:00:00Z",
        horizon="現在",
        confidence_percent=83,
        unknown_reason_codes=[RegimeDiagnosticReason.SIGNAL_CONFLICT, RegimeDiagnosticReason.WIDE_SPREAD],
        missing_sources=["liquidity_context"],
    )
    unknown_card = build_market_regime_card_spec(
        horizon="現在",
        regime_code=MarketRegimeCode.UNKNOWN,
        confidence_percent=83,
        background_tone=BackgroundTone.UNKNOWN,
        freshness_badge=FreshnessBadge.LIVE,
        evidence_quality=EvidenceQuality.CONFLICTED,
        short_tag=ShortTag.SIGNAL_CONFLICT,
        diagnostic_record=unknown_record,
    ).to_dict()
    if unknown_card.get("card_lines") != ["予測不能", "83%", "シグナル割れ"]:
        blockers.append("unknown_card_lines_mismatch")
    diag = unknown_card.get("diagnostic_record") or {}
    if diag.get("unknown_reason_codes") != ["SIGNAL_CONFLICT", "WIDE_SPREAD"]:
        blockers.append("unknown_reason_codes_not_preserved")

    return {
        "ok": True,
        "diagnostic_version": DIAGNOSTIC_VERSION,
        "ready": not blockers,
        "blockers": blockers,
        "contract_report": report,
        "unknown_card_example": unknown_card,
        "safety": {
            "contract_helper_only": True,
            "production_ui_code_changed": False,
            "warroom_page_changed": False,
            "runtime_code_changed": False,
            "streamlit_render_allowed": False,
            "streamlit_render_invoked": False,
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
    result = run_market_regime_card_contract_diagnostic()
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result.get("ready") is True else 1


if __name__ == "__main__":
    raise SystemExit(main())
