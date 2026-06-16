# path: ./btcts_next/src/btcts/autotrade/ledger/__init__.py
# desc: AutoTrade ledger package.

from __future__ import annotations

from .abstention import AbstentionDiagnostic, MissedOpportunityRecord, classify_abstention
from .conversion import abstention_from_decision, outcome_from_decision
from .decision_log import ShadowDecisionRecord, append_decision_jsonl, build_shadow_decision_record
from .decision_status import (
    ShadowDecisionLedgerReadResult,
    ShadowDecisionLedgerSummary,
    read_shadow_decision_rows,
    summarize_shadow_decision_ledger,
)
from .observer_run_status import (
    ObserverRunLedgerSummary,
    ObserverRunRecord,
    append_observer_run_record,
    default_observer_run_ledger_path,
    read_observer_run_records,
    summarize_observer_run_ledger,
)
from .forecast_outcome_status import (
    ForecastOutcomeLedgerSummary,
    summarize_forecast_outcome_ledger,
)
from .forecast_resolution import (
    ActualMatch,
    ForecastOutcomeResolutionResult,
    append_forecast_outcome_link,
    default_forecast_outcome_ledger_path,
    find_actual_match_for_target,
    read_forecast_outcome_links,
    resolve_due_shadow_forecast_outcomes,
)
from .forecast_calibration import (
    ForecastCalibrationSummary,
    ForecastOutcomeLinkRecord,
    count_divergence_reasons,
    group_forecast_by_confidence,
    group_forecast_by_driver,
    group_forecast_by_parameter_set,
    link_forecast_outcome,
    summarize_forecast_links,
)
from .performance import (
    DecisionOutcomeRecord,
    PerformanceSummary,
    group_by_ground,
    group_by_parameter_set,
    group_by_reason_code,
    summarize_outcomes,
)

__all__ = [
    "AbstentionDiagnostic",
    "ActualMatch",
    "DecisionOutcomeRecord",
    "ForecastCalibrationSummary",
    "ForecastOutcomeLedgerSummary",
    "ForecastOutcomeLinkRecord",
    "ForecastOutcomeResolutionResult",
    "MissedOpportunityRecord",
    "ObserverRunLedgerSummary",
    "ObserverRunRecord",
    "PerformanceSummary",
    "ShadowDecisionLedgerReadResult",
    "ShadowDecisionLedgerSummary",
    "ShadowDecisionRecord",
    "abstention_from_decision",
    "append_decision_jsonl",
    "append_forecast_outcome_link",
    "append_observer_run_record",
    "build_shadow_decision_record",
    "classify_abstention",
    "count_divergence_reasons",
    "default_forecast_outcome_ledger_path",
    "default_observer_run_ledger_path",
    "find_actual_match_for_target",
    "group_by_ground",
    "group_by_parameter_set",
    "group_by_reason_code",
    "group_forecast_by_confidence",
    "group_forecast_by_driver",
    "group_forecast_by_parameter_set",
    "link_forecast_outcome",
    "outcome_from_decision",
    "read_forecast_outcome_links",
    "read_observer_run_records",
    "read_shadow_decision_rows",
    "resolve_due_shadow_forecast_outcomes",
    "summarize_forecast_links",
    "summarize_forecast_outcome_ledger",
    "summarize_observer_run_ledger",
    "summarize_outcomes",
    "summarize_shadow_decision_ledger",
]
