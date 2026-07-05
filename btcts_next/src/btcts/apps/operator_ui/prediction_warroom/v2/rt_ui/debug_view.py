# path: ./btcts_next/src/btcts/apps/operator_ui/prediction_warroom/v2/rt_ui/debug_view.py
# desc: WarRoom v2 RT debug packet renderer. Keeps raw packets out of the main visual flow.

from __future__ import annotations

from typing import Any, Mapping


def render_rt_debug_packets(packets: Mapping[str, Any], st_api: Any) -> dict[str, Any]:
    with st_api.expander("RT debug packets", expanded=False):
        for name, packet in packets.items():
            st_api.caption(str(name))
            st_api.json(packet)
    return {"ok": True, "debug_packet_count": len(packets), "raw_packets_hidden_by_default": True, "read_only": True}
