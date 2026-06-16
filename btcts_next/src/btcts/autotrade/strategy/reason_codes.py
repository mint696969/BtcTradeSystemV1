# path: ./btcts_next/src/btcts/autotrade/strategy/reason_codes.py
# desc: Shared AutoTrade reason-code constants.

from __future__ import annotations

STALE_INPUT = "stale_input"
TEMPORAL_FLOW_UNUSABLE = "temporal_flow_unusable"
TRADE_UNUSABLE = "trade_unusable"
LIQUIDITY_UNUSABLE = "liquidity_unusable"
LOW_CONFIDENCE = "low_confidence"
FORECAST_ALIGNED_SELL = "forecast_aligned_sell"
FORECAST_ALIGNED_BUY = "forecast_aligned_buy"
SELL_GROUND = "sell_ground"
BUY_GROUND = "buy_ground"
MIXED_GROUND = "mixed_ground"
UNKNOWN_GROUND = "unknown_ground"
WATCH_THRESHOLD_MET = "watch_threshold_met"
ENTRY_THRESHOLD_MET = "entry_threshold_met"
RISK_ENTRY_BLOCKED_STALE = "risk_entry_blocked_stale"
RISK_ENTRY_BLOCKED_LOW_QUALITY = "risk_entry_blocked_low_quality"
RISK_NO_REAL_ORDERS_IN_SHADOW = "risk_no_real_orders_in_shadow"
