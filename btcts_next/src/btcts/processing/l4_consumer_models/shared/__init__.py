# path: ./btcts_next/src/btcts/processing/l4_consumer_models/shared/__init__.py
# desc: Shared bundle package for L4 consumer models.

"""
Shared L4 bundles.

Rules:
- reusable across multiple consumers
- wording-free
- layout-free
- widget-library-free
"""

from .active_event_reading import (
    ACTIVE_EVENT_STABLE_KEYS,
    build_active_event_compact_rows,
)
from .health_digest import HealthDigest, HealthDigestBuildInput, build_health_digest
from .market_summary import MarketSummary, MarketSummaryBuildInput, build_market_summary
from .prediction_summary import (
    PredictionSummary,
    PredictionSummaryBuildInput,
    build_prediction_summary,
)
from .prediction_system_contract import (
    PredictionCalibrationHint,
    PredictionEvidenceBundle,
    PredictionEvidenceTrace,
    PredictionScenarioHorizonOutput,
    PredictionScenarioOutput,
    PredictionSystemInput,
)
from .prediction_system_input import (
    PredictionSystemBuildInput,
    build_prediction_system_input,
)
from .prediction_scenario_builder import (
    PredictionScenarioBuildInput,
    build_prediction_scenario_output,
)
from .prediction_tactic_contract import (
    ScenarioTacticCandidate,
    ScenarioTacticProposalOutput,
    TacticParameterSetRef,
    TacticReviewRecord,
)
from .prediction_tactic_builder import (
    PredictionTacticBuildInput,
    build_prediction_tactic_proposal_output,
)
from .prediction_tactic_review_builder import (
    PredictionTacticReviewBuildInput,
    build_prediction_tactic_review_record,
)
from .prediction_tactic_operation_contract import (
    TacticOperationRecord,
)
from .prediction_tactic_operation_builder import (
    PredictionTacticOperationBuildInput,
    build_prediction_tactic_operation_record,
)
from .prediction_regime_turning_point import (
    PredictionRegimeTurningPointBuildInput,
    build_prediction_regime_turning_point,
)
from .prediction_liquidity_board_history import (
    PredictionLiquidityBoardHistoryBuildInput,
    build_prediction_liquidity_board_history,
)
from .prediction_calibration_hint_builder import (
    PredictionCalibrationBuildInput,
    build_prediction_calibration_hint,
)
from .prediction_replay_feedback import (
    PredictionReplayFeedbackBuildInput,
    build_prediction_replay_feedback,
)

__all__ = [
    "ACTIVE_EVENT_STABLE_KEYS",
    "build_active_event_compact_rows",
    "HealthDigest",
    "HealthDigestBuildInput",
    "build_health_digest",
    "MarketSummary",
    "MarketSummaryBuildInput",
    "build_market_summary",
    "PredictionSummary",
    "PredictionSummaryBuildInput",
    "build_prediction_summary",
    "PredictionCalibrationHint",
    "PredictionEvidenceBundle",
    "PredictionEvidenceTrace",
    "PredictionScenarioHorizonOutput",
    "PredictionScenarioOutput",
    "PredictionSystemInput",
    "PredictionSystemBuildInput",
    "build_prediction_system_input",
    "PredictionScenarioBuildInput",
    "build_prediction_scenario_output",
    "TacticParameterSetRef",
    "ScenarioTacticCandidate",
    "ScenarioTacticProposalOutput",
    "TacticReviewRecord",
    "TacticOperationRecord",
    "PredictionTacticBuildInput",
    "build_prediction_tactic_proposal_output",
    "PredictionTacticReviewBuildInput",
    "build_prediction_tactic_review_record",
    "PredictionTacticOperationBuildInput",
    "build_prediction_tactic_operation_record",
    "PredictionRegimeTurningPointBuildInput",
    "build_prediction_regime_turning_point",
    "PredictionLiquidityBoardHistoryBuildInput",
    "build_prediction_liquidity_board_history",
    "PredictionCalibrationBuildInput",
    "build_prediction_calibration_hint",
    "PredictionReplayFeedbackBuildInput",
    "build_prediction_replay_feedback",
    "RealDataValidationEvidenceSummary",
    "build_real_data_validation_evidence_summary",
    "real_data_validation_evidence_summary_to_snapshot",
]


from .prediction_direction_builder import (
    PredictionDirectionBuildInput,
    build_prediction_direction_input_from_scenario,
    build_prediction_direction_output,
    prediction_direction_output_to_snapshot,
)
from .real_data_validation_evidence import (
    RealDataValidationEvidenceSummary,
    build_real_data_validation_evidence_summary,
    real_data_validation_evidence_summary_to_snapshot,
)
