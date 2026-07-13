# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_continuity_reason_inline.py
# desc: Verifies inline continuity reason rendering on the Health page.

from __future__ import annotations

from pathlib import Path

TARGET = Path(__file__).resolve().parents[1] / "components" / "health_continuity.py"


def _source() -> str:
    return TARGET.read_text(encoding="utf-8-sig")


def test_continuity_reason_is_rendered_inline_with_spacing() -> None:
    text = _source()
    assert "display: flex;" in text
    assert "align-items: baseline;" in text
    assert "gap: 1.25rem;" in text
    assert "flex-wrap: wrap;" in text
    assert "health-continuity-reason-title" in text
    assert "health-continuity-reason-text" in text


def test_continuity_reason_no_longer_forces_line_break() -> None:
    text = _source()
    assert "</strong><br>" not in text
    assert "white-space: nowrap;" in text
