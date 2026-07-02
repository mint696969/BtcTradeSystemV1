# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_market_regime_operator_review_snapshot_q28c.py
# desc: PS-Q28C tests for D-hot operator-review snapshot runner. Docs/tmp runner only; no production code change.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

REPO_ROOT = Path(__file__).resolve().parents[6]
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q28C_WARROOM_MARKET_REGIME_OPERATOR_REVIEW_SNAPSHOT_2026-07-02.md"
RUNNER = REPO_ROOT / "tmp/work/market_regime_engine_operator_review_snapshot/run_q28c_dhot_warroom_market_regime_snapshot.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_market_regime_card_panel.py"
WARROOM_PAGE = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"


def test_q28c_doc_records_operator_review_snapshot_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "ps_q28c_warroom_market_regime_operator_review_snapshot=true" in text
    assert "production_code_changed=false" in text
    assert "ui_copy_added=false" in text
    assert "tmp_snapshot_runner_added=true" in text
    assert "would_send_to_broker=false" in text


def test_q28c_tmp_runner_is_dhot_read_only_and_tmp_output_only() -> None:
    text = RUNNER.read_text(encoding="utf-8-sig")
    assert "D:\\btc_ts_hot" in text
    assert "build_warroom_market_regime_card_preview_switch_packet" in text
    assert "market_regime_cards_html" in text
    assert "tmp/work/market_regime_engine_operator_review_snapshot/out" in text
    assert "PACKET_PATH" in text
    assert "HTML_PATH" in text
    assert "would_send_to_broker" in text
    assert "False" in text
    for token in (
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
    ):
        assert token not in text


def test_q28c_production_ui_still_uses_q28a_default_real_preview_without_new_copy() -> None:
    page_text = WARROOM_PAGE.read_text(encoding="utf-8-sig")
    panel_text = PANEL.read_text(encoding="utf-8-sig")
    assert '"地合い preview"' in page_text
    assert "value=True" in page_text
    assert "warroom_page_preview_default_on" in page_text
    assert "stage_versions" in panel_text
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
