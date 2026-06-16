# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_warroom_page_graph_refresh_path.py
# desc: Verify WarRoom graph widgets use fragment refresh path and keep slot fallback path.

from __future__ import annotations

import sys
from contextlib import contextmanager
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.slot_definitions as slot_definitions  # noqa: E402
import btcts.apps.operator_ui.views.warroom_page as warroom_page  # noqa: E402


@contextmanager
def _recording_slot(calls: list[tuple[str, str]] | list[tuple[str, str, bool]], widget_id: str):
    calls.append(("slot", widget_id))
    yield


def main() -> int:
    original_render_fragment_slot = warroom_page.live_shell.render_fragment_slot
    original_slot_widget_from_meta = warroom_page.live_shell.slot_widget_from_meta
    original_renderers = dict(warroom_page._GRAPH_WIDGET_RENDERERS)

    calls: list[tuple] = []

    try:
        def _fake_render_fragment_slot(
            meta,
            render_body,
            *,
            enabled: bool = True,
            default_sec: int = 15,
        ) -> None:
            calls.append(("fragment", str(meta["widget_id"]), enabled))
            render_body()

        def _fake_slot_widget_from_meta(meta):
            return _recording_slot(calls, str(meta["widget_id"]))

        def _renderer_factory(widget_id: str):
            def _render(*, overlay_contract=None) -> None:
                calls.append(("render", widget_id, bool(overlay_contract)))

            return _render

        warroom_page.live_shell.render_fragment_slot = _fake_render_fragment_slot
        warroom_page.live_shell.slot_widget_from_meta = _fake_slot_widget_from_meta
        warroom_page._GRAPH_WIDGET_RENDERERS = {
            widget_id: _renderer_factory(widget_id)
            for widget_id in slot_definitions.warroom_graph_widget_ids()
        }

        for widget_id in slot_definitions.warroom_graph_widget_ids():
            bundle = slot_definitions.warroom_graph_widget_bundle(widget_id)
            warroom_page._render_graph_widget_bundle(
                bundle,
                fragment_enabled=True,
            )

        fragment_widget_ids = [
            row[1]
            for row in calls
            if row[0] == "fragment"
        ]
        rendered_widget_ids = [
            row[1]
            for row in calls
            if row[0] == "render"
        ]
        slot_widget_ids = [
            row[1]
            for row in calls
            if row[0] == "slot"
        ]

        assert fragment_widget_ids == slot_definitions.warroom_graph_widget_ids()
        assert rendered_widget_ids == slot_definitions.warroom_graph_widget_ids()
        assert slot_widget_ids == []

        calls.clear()

        bundle = slot_definitions.warroom_graph_widget_bundle("market_monitor")
        warroom_page._render_graph_widget_bundle(
            bundle,
            fragment_enabled=False,
        )

        assert ("fragment", "market_monitor", True) not in calls
        assert ("slot", "market_monitor") in calls
        assert ("render", "market_monitor", True) in calls

    finally:
        warroom_page.live_shell.render_fragment_slot = original_render_fragment_slot
        warroom_page.live_shell.slot_widget_from_meta = original_slot_widget_from_meta
        warroom_page._GRAPH_WIDGET_RENDERERS = original_renderers

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())