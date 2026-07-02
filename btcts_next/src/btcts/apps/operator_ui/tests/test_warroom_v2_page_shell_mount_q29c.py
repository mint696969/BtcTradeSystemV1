# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_page_shell_mount_q29c.py
# desc: PS-Q29C guards for mounting WarRoom v2 as a separate thin page shell.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.views.warroom_v2_page import (  # noqa: E402
    WARROOM_V2_PAGE_SHELL_MOUNT_VERSION,
    build_warroom_v2_page_mount_packet,
)
from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2_shell_preview_panel import (  # noqa: E402
    WARROOM_V2_SHELL_PREVIEW_PANEL_VERSION,
    build_warroom_v2_shell_preview_panel_packet,
)

REPO_ROOT = Path(__file__).resolve().parents[6]
APP = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/app.py"
LEGACY_WARROOM = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py"
V2_VIEW = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/views/warroom_v2_page.py"
PANEL = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2_shell_preview_panel.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29C_WARROOM_V2_PAGE_SHELL_MOUNT_2026-07-02.md"


def test_q29c_app_mounts_v2_as_separate_route_and_keeps_legacy() -> None:
    text = APP.read_text(encoding="utf-8-sig")
    assert "warroom_v2_page" in text
    assert '("warroom", get_text(lang, "page_warroom"), warroom_page)' in text
    assert '("warroom_v2", "WarRoom v2", warroom_v2_page)' in text
    assert text.index('("warroom", get_text(lang, "page_warroom"), warroom_page)') < text.index('("warroom_v2", "WarRoom v2", warroom_v2_page)')


def test_q29c_page_mount_packet_is_thin_and_safe() -> None:
    packet = build_warroom_v2_page_mount_packet()
    assert packet["page_shell_mount_version"] == WARROOM_V2_PAGE_SHELL_MOUNT_VERSION
    assert packet["page_key"] == "warroom_v2"
    assert packet["legacy_warroom_retained"] is True
    assert packet["legacy_warroom_route_removed"] is False
    assert packet["thin_page_shell_only"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["dhot_read_in_page"] is False
    assert packet["classifier_invoked_in_page"] is False
    assert packet["would_send_to_broker"] is False


def test_q29c_panel_consumes_shell_preview_without_runtime_connection() -> None:
    packet = build_warroom_v2_shell_preview_panel_packet(page_mount_packet=build_warroom_v2_page_mount_packet())
    shell = packet["shell_preview"]
    assert packet["panel_version"] == WARROOM_V2_SHELL_PREVIEW_PANEL_VERSION
    assert packet["display_only"] is True
    assert packet["runtime_connected"] is False
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False
    assert packet["dhot_read_in_panel"] is False
    assert packet["classifier_invoked_in_panel"] is False
    assert shell["warroom_v2_shell_preview_only"] is True
    assert shell["placeholder_read_models"]["placeholder_only"] is True
    assert shell["prediction_cards_before_scenario"] is True


def test_q29c_legacy_warroom_does_not_import_v2() -> None:
    text = LEGACY_WARROOM.read_text(encoding="utf-8-sig")
    assert "warroom_v2_page" not in text
    assert "prediction_warroom.v2" not in text
    assert "warroom_v2_shell_preview_panel" not in text


def test_q29c_new_page_and_panel_do_not_contain_runtime_owners() -> None:
    forbidden = (
        "D:" + "\\",
        "E:" + "\\",
        "build_market_regime_source_snapshot(",
        "classify_market_regime_feature_bundle(",
        "send_to_broker(",
        "append_ledger(",
        "ledger.append(",
        "write_runtime_artifact(",
        "write_prediction_artifact(",
        "write_status_artifact(",
        "websocket.",
        "sse.",
    )
    for path in (V2_VIEW, PANEL):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 220, f"file too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29c_doc_records_route_mount_non_goals() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "not_removing_legacy_warroom=true" in text
    assert "not_connecting_dhot=true" in text
    assert "not_invoking_classifier=true" in text
    assert "not_enabling_websocket=true" in text
    assert "not_touching_autotrade_broker_ledger_mode_parameter=true" in text
