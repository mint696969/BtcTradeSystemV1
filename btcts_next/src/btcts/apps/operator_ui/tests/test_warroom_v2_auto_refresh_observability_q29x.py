# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_v2_auto_refresh_observability_q29x.py
# desc: PS-Q29X guards for WarRoom v2 auto-refresh observability.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

from btcts.apps.operator_ui.prediction_warroom.panels.warroom_v2.auto_refresh_control import build_warroom_v2_auto_refresh_control_packet  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[6]
RENDERER_DIR = REPO_ROOT / "btcts_next/src/btcts/apps/operator_ui/prediction_warroom/panels/warroom_v2"
CONTROL = RENDERER_DIR / "auto_refresh_control.py"
INIT = RENDERER_DIR / "__init__.py"
DOC = REPO_ROOT / "docs/strategy/PREDICTION_SYSTEM_PS_Q29X_WARROOM_V2_AUTO_REFRESH_OBSERVABILITY_2026-07-02.md"


def test_q29x_packet_exposes_last_rendered_at_and_status_strip_contract() -> None:
    packet = build_warroom_v2_auto_refresh_control_packet(enabled=True, interval_ms=3000, source="operator_sidebar", last_rendered_at="2026-07-02T12:00:00Z")
    assert packet["observable_status_strip"] is True
    assert packet["last_rendered_at"] == "2026-07-02T12:00:00Z"
    assert packet["auto_refresh_enabled"] is True
    assert packet["interval_ms"] == 3000
    assert packet["push_connected"] is False
    assert packet["websocket_enabled"] is False
    assert packet["sse_enabled"] is False


def test_q29x_status_strip_is_always_rendered_before_expander_details() -> None:
    text = CONTROL.read_text(encoding="utf-8-sig")
    assert "def render_warroom_v2_auto_refresh_status_strip" in text
    assert text.index("render_warroom_v2_auto_refresh_status_strip(packet)") < text.index('with st.expander("Auto refresh / 高頻度更新"')
    assert "Last render UTC" in text
    assert "observable browser-timer status" in text


def test_q29x_exports_status_strip_and_sidebar_settings() -> None:
    text = INIT.read_text(encoding="utf-8-sig")
    assert "render_warroom_v2_auto_refresh_status_strip" in text
    assert "sidebar_auto_refresh_settings" in text


def test_q29x_renderer_files_remain_small_and_non_executing() -> None:
    forbidden = ("send_to_broker(", "append_ledger(", "ledger.append(", "write_runtime_artifact(", "write_prediction_artifact(", "write_status_artifact(", "websocket.", "sse.")
    for path in RENDERER_DIR.glob("*.py"):
        text = path.read_text(encoding="utf-8-sig")
        assert len(text.splitlines()) <= 120, f"renderer file is too large: {path}"
        for token in forbidden:
            assert token not in text, f"forbidden token {token!r} found in {path}"


def test_q29x_doc_records_observability_boundary() -> None:
    text = DOC.read_text(encoding="utf-8-sig")
    assert "auto_refresh_observable_status_strip=true" in text
    assert "last_rendered_at_visible=true" in text
    assert "push_connected=false" in text
    assert "would_send_to_broker=false" in text
