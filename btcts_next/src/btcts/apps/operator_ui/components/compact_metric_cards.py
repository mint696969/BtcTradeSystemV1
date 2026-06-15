# path: ./btcts_next/src/btcts/apps/operator_ui/components/compact_metric_cards.py
# desc: Lightweight HTML metric-card renderer for Operator UI panels that need fewer Streamlit DOM nodes.

from __future__ import annotations

from html import escape
from typing import Iterable

import streamlit as st


def _cell(label: object, value: object) -> str:
    label_text = escape(str(label if label is not None else "-").strip() or "-")
    value_text = escape(str(value if value is not None else "-").strip() or "-")
    return (
        '<div class="btcts-compact-metric-card">'
        f'<div class="btcts-compact-metric-label">{label_text}</div>'
        f'<div class="btcts-compact-metric-value">{value_text}</div>'
        '</div>'
    )


def render_compact_metric_grid(
    rows: Iterable[tuple[object, object]],
    *,
    min_width_px: int = 120,
) -> None:
    cells = [_cell(label, value) for label, value in rows]
    if not cells:
        return

    html = f"""
    <style>
    .btcts-compact-metric-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax({int(min_width_px)}px, 1fr));
        gap: 0.42rem;
        margin: 0.2rem 0 0.45rem 0;
    }}
    .btcts-compact-metric-card {{
        border: 1px solid rgba(148, 163, 184, 0.28);
        border-radius: 0.55rem;
        padding: 0.42rem 0.55rem;
        background: rgba(15, 23, 42, 0.025);
        min-height: 3.2rem;
    }}
    .btcts-compact-metric-label {{
        font-size: 0.74rem;
        color: rgba(100, 116, 139, 0.95);
        line-height: 1.15;
        margin-bottom: 0.18rem;
        overflow-wrap: anywhere;
    }}
    .btcts-compact-metric-value {{
        font-size: 1.0rem;
        font-weight: 700;
        line-height: 1.25;
        overflow-wrap: anywhere;
    }}
    </style>
    <div class="btcts-compact-metric-grid">
        {''.join(cells)}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
