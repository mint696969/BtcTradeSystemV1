# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F6_10_ORIGIN_FEATURE_PARAMETER_ANALYSIS_EVIDENCE_2026-07-14.md
# desc: Persists the read-only D-hot analysis evidence used to define MR-F6.10 shadow parameter candidates.

# Prediction System MarketRegime MR-F6.10 Origin Feature Parameter Analysis Evidence

Updated: 2026-07-14 JST
Status: accepted analysis evidence for shadow registry construction
Gate: MR_F6_MANDATORY_SIMPLE_BASELINE_COMPARISON

## Source and method

```text
source:
  D:\btc_ts_hot\data\derived\warroom\candles\exchange=bitflyer\symbol=FX_BTC_JPY\timeframe=60s\closed.jsonl

timestamp field:
  time_utc

epoch cross-check field:
  time

analysis window:
  2026-06-29T07:38:00Z .. 2026-07-13T23:05:00Z

source rows:
  20160

candle interval:
  60 seconds

contiguous segments:
  420

usable segments with at least 60 rows:
  71

largest gap:
  13680 seconds

longest contiguous segment:
  1402 rows
```

Rolling calculations never cross a timestamp gap.

## Rolling realized-volatility distribution

The calculation uses 60-row windows over contiguous one-minute candle segments and the same simple-return population standard deviation semantics as the current L4 candle-window feature path.

```text
sample count: 10516
min:   1.97539907 bps
p10:   3.79525581 bps
p25:   4.47257112 bps
p50:   5.51970101 bps
p75:   7.35462997 bps
p90:  10.04311125 bps
p95:  11.70704259 bps
max:  16.51271264 bps
```

## MA candidate evidence

```text
3 / 10 rows
  sample_count: 17161
  sign_change_rate: 0.12575758
  absolute separation bps p25/p50/p75/p90:
    1.61637973 / 3.57193974 / 6.72451604 / 11.11372955

5 / 20 rows
  sample_count: 14951
  sign_change_rate: 0.06334448
  absolute separation bps p25/p50/p75/p90:
    2.62291150 / 5.83163758 / 10.71570994 / 17.11616084

10 / 30 rows
  sample_count: 13341
  sign_change_rate: 0.03770615
  absolute separation bps p25/p50/p75/p90:
    3.22778340 / 6.93176122 / 12.04308526 / 18.87001871

15 / 60 rows
  sample_count: 10516
  sign_change_rate: 0.02063718
  absolute separation bps p25/p50/p75/p90:
    5.52766254 / 12.06399373 / 20.96950763 / 32.92286264
```

## Candidate construction decision

No single parameter set was selected. The shadow registry contains the Cartesian product of:

```text
MA pairs:
  3 / 10
  5 / 20
  10 / 30
  15 / 60

volatility bands:
  interquartile: p25 / p75
  central 80 percent: p10 / p90
```

This evidence does not authorize runtime selection, canonical replacement, automatic promotion, scheduler registration, or live parameter application.
