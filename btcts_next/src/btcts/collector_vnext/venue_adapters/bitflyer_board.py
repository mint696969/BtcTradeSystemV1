# path: ./btcts_next/src/btcts/collector_vnext/venue_adapters/bitflyer_board.py
# desc: bitFlyer board venue adapter for snapshot/delta classification and level extraction.

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Literal


BoardMessageKind = Literal["snapshot", "delta", "unknown"]


@dataclass(frozen=True)
class NormalizedBoardLevels:
    bids: List[Dict[str, float]]
    asks: List[Dict[str, float]]


def _levels(rows: Any) -> List[Dict[str, float]]:
    out: List[Dict[str, float]] = []

    if not isinstance(rows, list):
        return out

    for r in rows:
        if not isinstance(r, dict):
            continue

        try:
            price = float(r["price"])
            size = float(r["size"])
        except Exception:
            continue

        out.append(
            {
                "price": price,
                "size": size,
            }
        )

    return out


class BitflyerBoardVenueAdapter:
    venue_id = "bitflyer"
    supports_sequence = False

    def classify_board_message_kind(self, *, channel: str, payload: Dict[str, Any]) -> BoardMessageKind:
        del payload

        if channel.startswith("lightning_board_snapshot_"):
            return "snapshot"

        if channel.startswith("lightning_board_"):
            return "delta"

        return "unknown"

    def extract_board_levels(self, payload: Dict[str, Any]) -> NormalizedBoardLevels:
        # bitFlyer docs 上、board diff の size=0 は当該価格帯の削除を意味する。
        # ここでは意味解釈までは行わず、仕様上の levels をそのまま正規化する。
        return NormalizedBoardLevels(
            bids=_levels(payload.get("bids")),
            asks=_levels(payload.get("asks")),
        )