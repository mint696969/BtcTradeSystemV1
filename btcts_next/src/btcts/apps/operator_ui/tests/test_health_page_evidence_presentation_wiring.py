# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_page_evidence_presentation_wiring.py
# desc: Verify Health page evidence presentation wiring stays snapshot-only and Health-only.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))


def _read(rel_path: str) -> str:
    return (_SRC_ROOT / rel_path).read_text(encoding="utf-8")


def main() -> int:
    health_page = _read("btcts/apps/operator_ui/views/health_page.py")
    warroom_page = _read("btcts/apps/operator_ui/views/warroom_page.py")
    slot_defs = _read("btcts/apps/operator_ui/components/slot_definitions.py")

    assert "render_evidence_presentation_panel" in health_page
    assert "_snapshot_evidence_presentation_payload" in health_page
    assert "lower_health_snapshot_evidence_presentation_for_ui" in health_page
    assert "evidence_presentation_payload" in health_page
    assert "health_warroom_evidence_presentation_payload" in health_page
    assert "real_data_validation_evidence_presentation" in health_page
    assert 'health_widget_slot("evidence_presentation_panel")' in health_page
    assert "render_evidence_presentation_panel(evidence_payload" in health_page

    slot_call = health_page.find('health_widget_slot("evidence_presentation_panel")')
    section_def = health_page.find("def _render_evidence_presentation_section()")
    assert section_def >= 0 and slot_call > section_def

    assert "evidence_presentation_panel" in slot_defs
    # WarRoom evidence presentation wiring is allowed after the Health wiring close.
    assert "render_evidence_presentation_panel" in warroom_page
    assert "_warroom_evidence_presentation_payload" in warroom_page

    forbidden = [
        "D:" + "\\",
        "E:" + "\\",
        "health_warroom_evidence_presentation_payload(",
        "health_warroom_evidence_presentation_model(",
        "build_real_data_validation_evidence_summary(",
        "runtime_state_path",
        "market_engine_signal",
        "collector_write_path",
        "place" + "_" + "order(",
        "broker" + "_" + "order(",
        "training_dataset",
        "inference_job",
    ]
    for token in forbidden:
        assert token not in health_page

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
