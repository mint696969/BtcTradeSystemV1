# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_FORECASTABILITY_REMEDIATION_2026-07-12.md
# desc: MR-F5 remediation for session-context availability and multi-candidate future score ranking.

# Prediction System MarketRegime MR-F5 Forecastability Remediation

Updated: 2026-07-12 JST
Status: implementation prepared

## Boundary

- Add deterministic UTC session context as an explicit feature signal.
- Add a score vote from the existing current L4 candle regime hint.
- Preserve existing current-regime thresholds and future baseline abstention policy.
- No D-hot write, scheduler registration, live parameter apply, or UI change.
