# path: ./docs/strategy/PREDICTION_SYSTEM_MARKET_REGIME_MR_F5_TRANSITION_PRIOR_FORECASTABILITY_REMEDIATION_2026-07-12.md
# desc: MR-F5 shadow-only transition-prior remediation for single-positive-candidate future-score windows.

# Prediction System MarketRegime MR-F5 Transition-prior Forecastability Remediation

Updated: 2026-07-12 JST
Status: implementation prepared

## Boundary

- Apply a parameter-set-owned transition prior only when exactly one positive observed regime candidate exists.
- Select only an allowed adjacent transition from the origin state.
- Keep the prior score strictly below the observed top score.
- Preserve prior usage in forecast metadata.
- Keep shadow-only, canonical-isolated, scheduler-unregistered, no live parameter apply, and no auto promotion.
