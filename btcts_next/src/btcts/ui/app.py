# path: ./btcts_next/src/btcts/ui/app.py
# desc: btcts_next 独立Streamlitアプリのエントリ。pages を束ね、最小の運用UIを提供する。

from __future__ import annotations

import os

import streamlit as st

from btcts.core import env as ENV
from btcts.core import paths as PATHS
from btcts.ui.pages.collector import render_collector_page
from btcts.ui.pages.health import render_health_page


def _env(k: str) -> str:
    return os.environ.get(k, "") or ""


def main() -> None:
    st.set_page_config(page_title="BTC TS Next", layout="wide")
    st.title("BTC TS Next")

    with st.expander("Paths (effective)", expanded=False):
        st.write(
            {
                # env raw
                "ENV.BTC_TS_DATA_DIR": _env("BTC_TS_DATA_DIR"),
                "ENV.BTC_TS_LOGS_DIR": _env("BTC_TS_LOGS_DIR"),
                "ENV.BTC_TS_CONFIG_DIR": _env("BTC_TS_CONFIG_DIR"),
                "ENV.BTC_TS_SECRETS_DIR": _env("BTC_TS_SECRETS_DIR"),
                "ENV.BTC_TS_DATASET_DIR": _env("BTC_TS_DATASET_DIR"),
                # resolved
                "repo_root": str(ENV.repo_root()),
                "data_dir": str(ENV.data_dir()),
                "logs_dir": str(ENV.logs_dir()),
                "config_dir": str(ENV.config_dir()),
                "schema_dir": str(PATHS.schema_dir()),
                "ui_config_dir": str(PATHS.config_dir()),
            }
        )

    tab1, tab2 = st.tabs(["Collector", "Health"])
    with tab1:
        render_collector_page()
    with tab2:
        render_health_page()


if __name__ == "__main__":
    main()
