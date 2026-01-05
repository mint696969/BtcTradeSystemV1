# path: ./btcts_next/src/btcts/ui/pages/collector.py
# desc: Collectorの起動/停止と status.json 表示。ENV/パス不整合を“原因が分かる形”で提示する最小運用UI。

from __future__ import annotations

import json
import os
import time
from typing import Any, Dict, Optional, Tuple

import streamlit as st
from btcts.core import env as ENV


def _env(k: str) -> str:
    return os.environ.get(k, "") or ""


def _status_path() -> Tuple[str, str]:
    """(data_dir, status.json path)"""
    try:
        data_dir = str(ENV.data_dir())
    except Exception:
        return "", ""
    return data_dir, os.path.join(data_dir, "collector", "status.json")


def _read_status_file() -> Tuple[Optional[Dict[str, Any]], str]:
    """(json or None, reason)"""
    data_dir, p = _status_path()
    if not data_dir:
        return None, "ENV.data_dir() is not resolved (BTC_TS_DATA_DIR is empty?)"

    if not os.path.exists(p):
        return None, f"status.json not found: {p}"

    try:
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f), ""
    except Exception as e:
        return None, f"status.json read failed: {type(e).__name__}: {e}"


def _expected_status_path_hint(data_dir: str) -> str:
    if not data_dir:
        return ""
    return os.path.join(data_dir, "collector", "status.json")


def render_collector_page() -> None:
    st.subheader("Collector Control")

    # Auto refresh（外部依存なしで確実に動く方式）
    ar1, ar2 = st.columns([1, 2])
    with ar1:
        auto = st.toggle("Auto refresh", value=False, key="collector_auto_refresh")
    with ar2:
        interval_sec = st.selectbox(
            "Interval (sec)",
            [1, 2, 3, 5, 10, 30, 60],
            index=3,  # 5秒
            key="collector_auto_refresh_sec",
        )

    # 遅延import：import時の副作用/重さを避ける
    from btcts.collector.control import start, status, stop

    # status.json パスの表示（ENVミスはここで即わかる）
    data_dir, st_path = _status_path()
    with st.expander("Paths (collector)", expanded=False):
        st.write(
            {
                "BTC_TS_DATA_DIR": data_dir,
                "status.json": st_path,
            }
        )

    # セッションキャッシュ（Refresh/Start/Stop でだけ更新）
    if "collector_status" not in st.session_state:
        st.session_state["collector_status"] = None
    if "collector_status_ts" not in st.session_state:
        st.session_state["collector_status_ts"] = 0.0
    if "collector_status_err" not in st.session_state:
        st.session_state["collector_status_err"] = ""

    def _refresh_status() -> None:
        try:
            st.session_state["collector_status"] = status()
            st.session_state["collector_status_err"] = ""
        except Exception as e:
            st.session_state["collector_status"] = None
            st.session_state["collector_status_err"] = f"status() failed: {type(e).__name__}: {e}"
        st.session_state["collector_status_ts"] = time.time()

    c1, c2, c3, c4 = st.columns([1, 1, 1, 2])

    with c1:
        if st.button("Start", use_container_width=True, key="collector_start"):
            stt = start()
            st.toast(f"start: {stt.mode} {stt.message}")
            _refresh_status()
            st.rerun()

    with c2:
        if st.button("Stop", use_container_width=True, key="collector_stop"):
            stt = stop()
            st.toast(f"stop: {stt.mode} {stt.message}")
            _refresh_status()
            st.rerun()

    with c3:
        if st.button("Refresh", use_container_width=True, key="collector_refresh"):
            _refresh_status()
            st.rerun()

    with c4:
        if st.session_state["collector_status"] is None and not st.session_state.get("collector_status_err"):
            # 初回表示だけ status() を叩く
            _refresh_status()

        err = st.session_state.get("collector_status_err", "")
        stt = st.session_state.get("collector_status")
        ts = st.session_state.get("collector_status_ts", 0.0)
        age = max(0.0, time.time() - ts) if ts else 0.0

        if err:
            st.caption(f"status(): ERROR (age={age:.1f}s)")
            st.error(err)
        elif stt is None:
            st.caption(f"status(): (no data) (age={age:.1f}s)")
        else:
            st.caption(f"status(): {stt.mode} / {stt.message} (age={age:.1f}s)")

    st.divider()

    st.write("status.json (raw)")
    js, reason = _read_status_file()

    if js is None:
        # ここは“原因が分かる”文言にする（妥協しない）
        if not data_dir:
            st.error("BTC_TS_DATA_DIR is empty. Set env and restart Streamlit.")
            st.code(
                "\n".join(
                    [
                        "reason: BTC_TS_DATA_DIR is empty",
                        f"expected: {_expected_status_path_hint(data_dir)}",
                        f"BTC_TS_DATA_DIR={_env('BTC_TS_DATA_DIR')}",
                        f"BTC_TS_LOGS_DIR={_env('BTC_TS_LOGS_DIR')}",
                        f"BTC_TS_CONFIG_DIR={_env('BTC_TS_CONFIG_DIR')}",
                    ]
                ),
                language="text",
            )

        else:
            st.warning("status.json is not available.")
            st.code(
                "\n".join(
                    [
                        f"reason: {reason}",
                        f"expected: {_expected_status_path_hint(data_dir)}",
                        f"BTC_TS_DATA_DIR={_env('BTC_TS_DATA_DIR')}",
                        f"BTC_TS_LOGS_DIR={_env('BTC_TS_LOGS_DIR')}",
                        f"BTC_TS_CONFIG_DIR={_env('BTC_TS_CONFIG_DIR')}",
                    ]
                ),
                language="text",
            )

    else:
        st.json(js)

    # 画面全体を描画し終えた後に更新をかける（押しボタン動作を邪魔しない）
    if st.session_state.get("collector_auto_refresh", False):
        sec = int(st.session_state.get("collector_auto_refresh_sec", 5))
        st.caption(f"Auto refresh: every {sec}s")
        time.sleep(max(1, sec))
        st.rerun()
