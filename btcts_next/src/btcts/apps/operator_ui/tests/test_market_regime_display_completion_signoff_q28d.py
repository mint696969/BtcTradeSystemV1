# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_display_completion_signoff_q28d.py
# desc: PS-Q28D signoff guard. Market-regime logic-to-display path completed by automated checks; production code unchanged.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q28D_WARROOM_MARKET_REGIME_DISPLAY_COMPLETION_SIGNOFF_2026-07-02.md"
DOC_Q27Z = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q27Z_MARKET_REGIME_FORECAST_METRIC_EVIDENCE_QUALITY_CALIBRATION_2026-07-02.md"
DOC_Q28A = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q28A_WARROOM_MARKET_REGIME_REAL_PREVIEW_DEFAULT_2026-07-02.md"
DOC_Q28B = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q28B_WARROOM_MARKET_REGIME_RENDER_PATH_COMPLETION_SMOKE_2026-07-02.md"
DOC_Q28C = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q28C_WARROOM_MARKET_REGIME_OPERATOR_REVIEW_SNAPSHOT_2026-07-02.md"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def test_q28d_doc_records_display_completion_signoff_boundary() -> None:
    text = _read(DOC)
    assert "ps_q28d_warroom_market_regime_display_completion_signoff=true" in text
    assert "market_regime_logic_to_display_automated_path_complete=true" in text
    assert "actual_screenshot_review_required_only_if_visual_issue_seen=true" in text
    assert "production_code_changed=false" in text
    assert "ui_copy_added=false" in text
    assert "would_send_to_broker=false" in text


def test_q28d_prior_completion_docs_prove_logic_to_display_chain() -> None:
    q27z = _read(DOC_Q27Z)
    q28a = _read(DOC_Q28A)
    q28b = _read(DOC_Q28B)
    q28c = _read(DOC_Q28C)
    assert "evidence_quality_calibrated_from_forecast_metric=true" in q27z
    assert "classifier_version=prediction.market_regime.regime_classifier.ps_q27z.v1" in q27z
    assert "warroom_market_regime_real_preview_default_on=true" in q28a
    assert "ui_copy_added=false" in q28a
    assert "renderer_session_state_stage_versions_verified=true" in q28b
    assert "renderer_real_preview_html_smoke_verified=true" in q28b
    assert "tmp_snapshot_runner_added=true" in q28c
    assert "dhot_read_only_snapshot=true" in q28c
    assert "would_send_to_broker=false" in q28c


def test_q28d_production_ui_remains_compact_and_non_executing() -> None:
    page_text = _read(WARROOM_PAGE)
    panel_text = _read(PANEL)
    assert '"地合い preview"' in page_text
    assert "value=True" in page_text
    assert "warroom_page_preview_default_on" in page_text
    assert "stage_versions" in panel_text
    assert "地合いカード preview はデフォルトOFF" not in page_text
    assert "勝率ではありません" not in panel_text
    assert "分類信頼度" not in panel_text
    for text in (page_text, panel_text):
        for token in (
            "send_to_broker(",
            "append_ledger(",
            "ledger.append(",
            "write_runtime_artifact(",
            "write_prediction_artifact(",
            "write_status_artifact(",
        ):
            assert token not in text
