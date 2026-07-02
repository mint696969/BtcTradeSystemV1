# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/scenario_placeholder.py
# desc: WarRoom v2 Japanese scenario placeholder composition. No live data, classifier, or transport behavior.

from __future__ import annotations

from typing import Any, Iterable

from .card_axis_policy import WARROOM_V2_HORIZON_LABELS

WARROOM_V2_SCENARIO_PLACEHOLDER_VERSION = "prediction_warroom.v2.scenario_placeholder.ps_q29h.v1"


def build_warroom_v2_scenario_placeholder_payload(*, item_titles: Iterable[str], generated_at: str = "") -> dict[str, Any]:
    items = [str(item) for item in item_titles if str(item)]
    horizons = list(WARROOM_V2_HORIZON_LABELS)
    return {
        "scenario_placeholder_version": WARROOM_V2_SCENARIO_PLACEHOLDER_VERSION,
        "scenario_area_below_cards": True,
        "scenario_source": "placeholder_matrix_contract",
        "row_axis": "prediction_item",
        "column_axis": "horizon",
        "horizon_labels": horizons,
        "prediction_item_titles": items,
        "matrix_row_count": len(items),
        "matrix_column_count": len(horizons),
        "scenario_lines": [
            f"現在〜24時間後の {len(horizons)} 時間軸カードを横に読み、{len(items)} 項目を縦に統合する placeholder シナリオです。",
            "現時点では全カードが未接続のため、方向・優位性・警戒点は確定していません。",
            "将来は read model builder が各項目×時間軸の要約をここへ渡します。",
        ],
        "watch_points": [
            "地合い・方向感・反転候補の整合性",
            "ボラ警戒と流動性 / 約定品質の悪化",
            "ブレイク / だましと市場間確認の一致・不一致",
        ],
        "invalidation_lines": [
            "runtime_connected=false",
            "all_horizon_cards_placeholder_only=true",
            "freshness_badge=NO_DATA",
        ],
        "placeholder_only": True,
        "runtime_connected": False,
        "push_connected": False,
        "websocket_enabled": False,
        "sse_enabled": False,
        "generated_at": generated_at,
    }
