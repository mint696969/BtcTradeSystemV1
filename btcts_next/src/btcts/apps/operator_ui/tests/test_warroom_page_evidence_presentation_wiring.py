# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_evidence_presentation_wiring.py
# desc: Verify WarRoom page evidence presentation wiring stays session-state-only and runtime-safe.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


def _read(rel_path: str) -> str:
    return (_SRC_ROOT / rel_path).read_text(encoding="utf-8")


def main() -> int:
    warroom_page = _read("btcts/apps/operator_ui/views/warroom_page.py")
    health_page = _read("btcts/apps/operator_ui/views/health_page.py")
    slot_defs = _read("btcts/apps/operator_ui/components/slot_definitions.py")

    assert "render_evidence_presentation_panel" in warroom_page
    assert "_warroom_evidence_presentation_payload" in warroom_page
    assert "lower_warroom_session_state_evidence_presentation_for_ui" in warroom_page
    assert "warroom_evidence_presentation_payload" in warroom_page
    assert "health_warroom_evidence_presentation_payload" in warroom_page
    assert "real_data_validation_evidence_presentation" in warroom_page
    assert "evidence_presentation_payload" in warroom_page
    assert 'warroom_widget_slot("evidence_presentation_panel")' in warroom_page
    assert "render_evidence_presentation_panel(evidence_payload" in warroom_page

    slot_call = warroom_page.find('warroom_widget_slot("evidence_presentation_panel")')
    section_def = warroom_page.find("def _render_warroom_evidence_presentation()")
    assert section_def >= 0 and slot_call > section_def

    assert "evidence_presentation_panel" in slot_defs
    assert "render_evidence_presentation_panel" in health_page

    forbidden = [
        "D:" + "\\",
        "E:" + "\\",
        "health_warroom_evidence_presentation_payload(",
        "health_warroom_evidence_presentation_model(",
        "build_real_data_validation_evidence_summary(",
        "load_health_snapshot",
        "runtime_state_path",
        "market_engine_signal",
        "collector_write_path",
        "place" + "_" + "order(",
        "broker" + "_" + "order(",
        "training_dataset",
        "inference_job",
    ]
    for token in forbidden:
        assert token not in warroom_page

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
