# path: ./btcts_next/src/btcts/prediction/warroom_plain_candle_server.py
# desc: Compatibility shim. Canonical WarRoom chart data server lives in L4 consumer model operator_ui runtime.

from __future__ import annotations

from btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server import *  # noqa: F401,F403
from btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server import (
    WARROOM_CHART_DATA_SERVER_CANONICAL_MODULE,
    WARROOM_CHART_DATA_SERVER_LAYER,
    WARROOM_CHART_DATA_SERVER_VERSION,
    WARROOM_PLAIN_CANDLE_SERVER_VERSION,
)

WARROOM_PLAIN_CANDLE_SERVER_COMPAT_MODULE = "btcts.prediction.warroom_plain_candle_server"
WARROOM_PLAIN_CANDLE_SERVER_COMPAT_ONLY = True


if __name__ == "__main__":
    from btcts.processing.l4_consumer_models.operator_ui.warroom_chart_data_server import main

    raise SystemExit(main())
