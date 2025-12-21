# path: ./btcts_next/src/btcts/ui/app.py
# desc: btcts_next 独立Streamlitアプリのエントリ。pages を束ね、最小の運用UIを提供する。

from __future__ import annotations

import os

import streamlit as st

from btcts.ui.pages.collector import render_collector_page
from btcts.ui.pages.health import render_health_page


def _env(k: str) -> str:
    return os.environ.get(k, "") or ""


def main() -> None:
    st.set_page_config(page_title="BTC TS Next", layout="wide")
    st.title("BTC TS Next")

    with st.expander("Paths (env)", expanded=False):
        st.write(
            {
                "BTC_TS_DATA_DIR": _env("BTC_TS_DATA_DIR"),
                "BTC_TS_LOGS_DIR": _env("BTC_TS_LOGS_DIR"),
                "BTC_TS_CONFIG_DIR": _env("BTC_TS_CONFIG_DIR"),
                "BTC_TS_SECRETS_DIR": _env("BTC_TS_SECRETS_DIR"),
                "BTC_TS_DATASET_DIR": _env("BTC_TS_DATASET_DIR"),
            }
        )

    tab1, tab2 = st.tabs(["Collector", "Health"])
    with tab1:
        render_collector_page()
    with tab2:
        render_health_page()


if __name__ == "__main__":
    main()
