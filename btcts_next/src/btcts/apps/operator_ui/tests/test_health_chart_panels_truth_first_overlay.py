# path: ./btcts_next/src/btcts/apps/operator_ui/tests/test_health_chart_panels_truth_first_overlay.py
# desc: Verify health overlay panels stop pretending current overlays are history lines.

from __future__ import annotations

import sys
from pathlib import Path

_SRC_ROOT = Path(__file__).resolve().parents[4]
if str(_SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SRC_ROOT))

import btcts.apps.operator_ui.components.health_chart_panels as panels  # noqa: E402


class _DummyContainer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class _DummyStreamlit:
    def __init__(self) -> None:
        self.captions: list[str] = []
        self.line_chart_calls = 0

    def columns(self, count: int):
        return [self for _ in range(count)]

    def metric(self, *args, **kwargs):
        return None

    def caption(self, text):
        self.captions.append(str(text))

    def info(self, *args, **kwargs):
        return None

    def warning(self, *args, **kwargs):
        return None

    def line_chart(self, *args, **kwargs):
        self.line_chart_calls += 1
        return None

    def dataframe(self, *args, **kwargs):
        return None


def main() -> int:
    dummy_st = _DummyStreamlit()

    import types

    original_streamlit = sys.modules.get("streamlit")
    sys.modules["streamlit"] = types.SimpleNamespace(
        columns=dummy_st.columns,
        metric=dummy_st.metric,
        caption=dummy_st.caption,
        info=dummy_st.info,
        warning=dummy_st.warning,
        line_chart=dummy_st.line_chart,
        dataframe=dummy_st.dataframe,
    )

    original_panel_container = panels.live_shell.panel_container
    panels.live_shell.panel_container = lambda **kwargs: _DummyContainer()

    try:
        panels.render_api_chart_panel(
            lang="ja",
            range_key="1h",
            api_ws_series=[
                {
                    "ts": "2026-04-15T01:00:00Z",
                    "api_metric_mode": "short",
                    "api_events": 10,
                    "api_rolling_5m": 30,
                    "api_limit_5m": 500.0,
                    "events_429": 0,
                    "events_429_marker": None,
                    "ws_events": 2,
                    "ws_exec_events": 1,
                    "gap_events": 0,
                    "resync_events": 0,
                    "warn_error_events": 0,
                    "coverage_complete": True,
                }
            ],
            rate_overlay=[
                {
                    "ts": "2026-04-15T01:00:00Z",
                    "source_kind": "rate_state_overlay",
                    "budget_60s": 100,
                    "budget_300s": 500,
                    "utilization": 0.5,
                    "active_target_ratio": 0.5,
                    "target_utilization": 0.95,
                    "hard_cap_utilization": 0.98,
                }
            ],
            bitflyer_rate={"requests_60s": 10, "requests_300s": 50},
            bitflyer_rate_snapshot={"requests_60s": 5},
            bitflyer_rate_trades={"requests_60s": 3},
            get_text=lambda lang, key: key,
            section_title_with_range=lambda title, range_key: f"{title} ({range_key})",
            format_metric_number=lambda value, **kwargs: str(value),
            api_chart_columns_and_labels=lambda df, lang: (
                ["api_events"],
                {"api_events": "api_events"},
            ),
        )

        panels.render_layer3_chart_panel(
            lang="ja",
            range_key="1h",
            layer3_series=[
                {
                    "ts": "2026-04-15T01:00:00Z",
                    "source_kind": "market_state_snapshot_overlay",
                    "trust_score": 2,
                    "continuity_score": 2,
                    "interpretation_score": 2,
                    "freshness_score": 0,
                }
            ],
            layer3_semantic_usage_rows=[],
            layer3_semantic_usage_summary={},
            layer3_runtime_contract_summary={},
            layer3_orderbook_runtime_summary={},
            market_latest={},
            market_diag={},
            get_text=lambda lang, key: key,
            section_title_with_range=lambda title, range_key: f"{title} ({range_key})",
            health_value_label=lambda value, lang: str(value),
        )
    finally:
        panels.live_shell.panel_container = original_panel_container
        if original_streamlit is not None:
            sys.modules["streamlit"] = original_streamlit
        else:
            sys.modules.pop("streamlit", None)

    joined = "\n".join(dummy_st.captions)
    assert "rate overlay is current-state only" in joined
    assert "layer3 score overlay is current-state only" in joined
    assert dummy_st.line_chart_calls == 1

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())