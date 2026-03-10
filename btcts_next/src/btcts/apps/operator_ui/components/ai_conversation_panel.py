# path: ./btcts_next/src/btcts/apps/operator_ui/components/ai_conversation_panel.py
# desc: orderbook / trades の最新状態から定型質問に対するローカル要約回答を返す WarRoom 会話パネル

import streamlit as st
import json
from pathlib import Path
from btcts.apps.operator_ui.ui_text import get_text
from btcts.apps.operator_ui.ai_runtime import (
    default_mode,
    generate_answer,
    supported_modes,
)
from btcts.apps.operator_ui.ai_memory_store import (
    append_memory,
    load_recent_memory,
)

ORDERBOOK_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\orderbook")
TRADES_DIR = Path(r"E:\btc_ts\data\collector\bitflyer\trades")


def _read_latest_jsonl(dir_path):

    if not dir_path.exists():
        return None

    files = sorted(dir_path.glob("*.jsonl"))

    if not files:
        return None

    latest = files[-1]

    with open(latest, "rb") as f:

        f.seek(0, 2)
        size = f.tell()

        block = 4096
        data = b""

        while size > 0:

            step = min(block, size)
            size -= step
            f.seek(size)

            data = f.read(step) + data

            if data.count(b"\n") >= 2:
                break

        line = data.splitlines()[-1]

    return json.loads(line)


def _analyze_state():

    ob = _read_latest_jsonl(ORDERBOOK_DIR)
    tr = _read_latest_jsonl(TRADES_DIR)

    if not ob or not tr:
        return None

    bids = ob.get("bids", [])
    asks = ob.get("asks", [])
    items = tr.get("items", [])

    if not bids or not asks or not items:
        return None

    best_bid = ob.get("best_bid", bids[0]["price"])
    best_ask = ob.get("best_ask", asks[0]["price"])
    spread = ob.get("spread", best_ask - best_bid)

    bid_vol = sum(b["size"] for b in bids[:10])
    ask_vol = sum(a["size"] for a in asks[:10])
    total = bid_vol + ask_vol
    imbalance = 0 if total == 0 else (bid_vol - ask_vol) / total

    buy_vol = sum(x["size"] for x in items if x.get("side") == "BUY")
    sell_vol = sum(x["size"] for x in items if x.get("side") == "SELL")
    delta = buy_vol - sell_vol

    top_bid_wall = max(b["size"] for b in bids[:10])
    top_ask_wall = max(a["size"] for a in asks[:10])
    wall_total = top_bid_wall + top_ask_wall
    wall_ratio = 0 if wall_total == 0 else (top_bid_wall - top_ask_wall) / wall_total

    return {
        "spread": spread,
        "imbalance": imbalance,
        "delta": delta,
        "wall_ratio": wall_ratio,
    }


def render():

    lang = st.session_state.get("ui_lang", "en")

    if "ai_conversation_history" not in st.session_state:
        st.session_state.ai_conversation_history = []
    if "ai_market_memory" not in st.session_state:
        st.session_state.ai_market_memory = load_recent_memory(max_items=8)

    if "ai_runtime_mode" not in st.session_state:
        st.session_state.ai_runtime_mode = default_mode()

    st.markdown(f"### {get_text(lang, 'ai_conversation_title')}")

    options = [
        get_text(lang, "ai_conversation_q1"),
        get_text(lang, "ai_conversation_q2"),
        get_text(lang, "ai_conversation_q3"),
        get_text(lang, "ai_conversation_q4"),
    ]

    mode_options = supported_modes()

    selected_mode = st.selectbox(
        get_text(lang, "ai_runtime_mode"),
        mode_options,
        index=mode_options.index(st.session_state.ai_runtime_mode),
        key="ai_runtime_mode_selector",
    )
    st.session_state.ai_runtime_mode = selected_mode

    prompt = st.selectbox(
        get_text(lang, "ai_conversation_prompt"),
        options,
        index=0,
        key="ai_conversation_prompt_selector",
    )

    intent_options = [
        get_text(lang, "ai_conversation_intent_explain"),
        get_text(lang, "ai_conversation_intent_decide"),
        get_text(lang, "ai_conversation_intent_risk"),
        get_text(lang, "ai_conversation_intent_wall"),
    ]

    style_options = [
        get_text(lang, "ai_conversation_style_concise"),
        get_text(lang, "ai_conversation_style_normal"),
        get_text(lang, "ai_conversation_style_deep"),
    ]

    c_intent, c_style = st.columns(2)

    intent = c_intent.selectbox(
        get_text(lang, "ai_conversation_intent"),
        intent_options,
        index=0,
        key="ai_conversation_intent_selector",
    )

    style = c_style.selectbox(
        get_text(lang, "ai_conversation_style"),
        style_options,
        index=1,
        key="ai_conversation_style_selector",
    )

    custom_prompt = st.text_input(
        get_text(lang, "ai_conversation_custom_prompt"),
        value="",
        key="ai_conversation_custom_prompt_input",
    )

    note = st.text_area(
        get_text(lang, "ai_conversation_note"),
        value="",
        height=80,
        key="ai_conversation_note_input",
    )

    c_btn1, c_btn2 = st.columns(2)

    send_clicked = c_btn1.button(
        get_text(lang, "ai_conversation_send"),
        key="ai_conversation_send_button",
    )

    clear_clicked = c_btn2.button(
        get_text(lang, "ai_conversation_clear"),
        key="ai_conversation_clear_button",
    )

    if clear_clicked:
        st.session_state.ai_conversation_history = []
        st.session_state.ai_market_memory = load_recent_memory(max_items=8)
        st.success(get_text(lang, "ai_conversation_clear_done"))

    state = _analyze_state()

    st.markdown(f"**{get_text(lang, 'ai_conversation_result')}**")

    if not state:
        st.warning(get_text(lang, "ai_summary_missing_data"))
        return

    latest_memory_entry = {
        "spread": float(state["spread"]),
        "imbalance": float(state["imbalance"]),
        "delta": float(state["delta"]),
        "wall_ratio": float(state["wall_ratio"]),
    }

    memory = st.session_state.ai_market_memory

    if not memory or any(
        abs(latest_memory_entry[k] - memory[0][k]) > 1e-9
        for k in latest_memory_entry
    ):
        st.session_state.ai_market_memory = append_memory(
            latest_memory_entry,
            max_items_hint=8,
        )
        
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(get_text(lang, "ai_conversation_state_spread"), round(state["spread"], 1))
    c2.metric(get_text(lang, "ai_conversation_state_imbalance"), round(state["imbalance"], 3))
    c3.metric(get_text(lang, "ai_conversation_state_delta"), round(state["delta"], 3))
    c4.metric(get_text(lang, "ai_conversation_state_wall_ratio"), round(state["wall_ratio"], 3))

    final_prompt = custom_prompt.strip() if custom_prompt.strip() else prompt
    effective_prompt = f"[{intent} / {style}] {final_prompt}"
    st.caption(f"{get_text(lang, 'ai_conversation_effective_prompt')}: {effective_prompt}")

    if send_clicked:
        answer, runtime_source = generate_answer(
            mode=st.session_state.ai_runtime_mode,
            lang=lang,
            prompt=final_prompt,
            state=state,
            note=note,
            memory=st.session_state.ai_market_memory,
            intent=intent,
            style=style,
        )

        st.session_state.ai_conversation_history.insert(
            0,
            {
                "mode": st.session_state.ai_runtime_mode,
                "runtime_source": runtime_source,
                "intent": intent,
                "style": style,
                "prompt": final_prompt,
                "answer": answer,
            },
        )

        st.session_state.ai_conversation_history = st.session_state.ai_conversation_history[:8]

    if st.session_state.ai_conversation_history:
        latest = st.session_state.ai_conversation_history[0]
        st.info(latest["answer"])
        st.caption(
            f"{get_text(lang, 'ai_runtime_source')}: "
            f"{latest.get('runtime_source', latest.get('mode', 'local'))}"
        )
    else:
        st.info(get_text(lang, "ai_conversation_placeholder"))

    st.markdown(f"**{get_text(lang, 'ai_conversation_history')}**")

    if st.session_state.ai_conversation_history:
        for item in st.session_state.ai_conversation_history:
            st.markdown(
                f"**{get_text(lang, 'ai_conversation_user')}** "
                f"({item['mode']} / {item.get('runtime_source', item['mode'])}) "
                f"[{item.get('intent', '-')}"
                f" / {item.get('style', '-')}]"
                f": {item['prompt']}"
            )
            st.markdown(f"**{get_text(lang, 'ai_conversation_ai')}**: {item['answer']}")
            st.markdown("---")
    else:
        st.caption(get_text(lang, "ai_conversation_empty_history"))

    st.markdown(f"**{get_text(lang, 'ai_memory_title')}**")

    if st.session_state.ai_market_memory:
        latest = st.session_state.ai_market_memory[0]

        c1, c2, c3, c4 = st.columns(4)
        c1.metric(get_text(lang, "ai_memory_spread_change"), round(latest["spread"], 1))
        c2.metric(get_text(lang, "ai_memory_imbalance_change"), round(latest["imbalance"], 3))
        c3.metric(get_text(lang, "ai_memory_delta_change"), round(latest["delta"], 3))
        c4.metric(get_text(lang, "ai_memory_wall_ratio_change"), round(latest["wall_ratio"], 3))
    else:
        st.caption(get_text(lang, "ai_memory_empty"))

    st.caption(get_text(lang, "ai_memory_persistent_hint"))

    st.divider()