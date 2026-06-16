# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_live_shell_page_auto_refresh_js.py
# desc: Guard Collector page auto-refresh JS stays robust and parent-page scoped.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


def main() -> int:
    live_shell_path = _SRC_ROOT / "btcts" / "apps" / "operator_ui" / "components" / "live_shell.py"
    text = live_shell_path.read_text(encoding="utf-8")
    start = text.index("def render_page_auto_refresh(")
    end = text.index("\ndef render_folded_section(", start)
    block = text[start:end]

    assert "window.parent || window" in block
    assert "setInterval" in block
    assert "clearInterval" in block
    assert "parentWindow.location.reload()" in block
    assert "(() =>" in block and "})();" in block
    assert "setTimeout" not in block
    assert "if (!parentWindow)" not in block
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
