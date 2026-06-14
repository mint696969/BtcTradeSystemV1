# path: ./btcts_next/src/btcts/autotrade/execution/__init__.py
# desc: AutoTrade execution package. Contracts only; no broker client import.

from __future__ import annotations

from .command_ledger import (
    CommandLedgerRecord,
    append_command_ledger_record,
    build_command_ledger_record,
    default_command_ledger_path,
    read_command_ledger,
    validate_and_append_command,
)
from .command_request import CommandRequest, CommandType, CommandValidationResult, validate_command_request
from .command_status import CommandLedgerReadResult, CommandLedgerSummary, read_command_ledger_rows, summarize_command_ledger
from .dry_run import DryRunExecutionResult, evaluate_armed_dry_run_intent
from .intents import OrderIntent, OrderSide, OrderType, build_order_intent_from_decision
from .mode_change_request import (
    ModeChangeCommandRequestResult,
    build_mode_change_command_request_record,
    submit_mode_change_command_request,
)
from .mode_command_applier import (
    ModeChangeCommandApplyPreview,
    ModeChangeCommandApplyResult,
    ModeChangeCommandReadinessApplyPreview,
    ModeChangeCommandReadinessApplyResult,
    apply_latest_mode_change_command_once,
    apply_latest_mode_change_command_once_with_readiness_recheck,
    preview_latest_mode_change_command_apply,
    preview_latest_mode_change_command_apply_with_readiness_recheck,
)
from .mode_state import (
    DEFAULT_MODE_STATE,
    ModeStateReadResult,
    ModeStateRecord,
    ModeStateSummary,
    append_mode_state_record,
    build_mode_state_record_from_command,
    current_mode_state,
    default_mode_state_ledger_path,
    read_mode_state_records,
    summarize_mode_state,
)
from .order_state import PaperOrder, PaperOrderStatus, create_paper_order, paper_order_id_for_intent
from .order_preview import BitflyerFxOrderRequestPreview, OrderPreviewResult, build_bitflyer_fx_manual_order_preview, build_bitflyer_fx_order_request_preview
from .paper_intent import PaperOrderIntentBuildResult, build_fx_paper_order_intent_from_service_input, validate_execution_market_service_input_for_paper
from .reconciliation import FxReconciliationResult, reconcile_fx_private_state_with_paper
from .live_readiness_contract import FxLiveReadinessContractResult, evaluate_fx_live_readiness_contract

__all__ = [
    "BitflyerFxOrderRequestPreview",
    "OrderPreviewResult",
    "build_bitflyer_fx_manual_order_preview",
    "build_bitflyer_fx_order_request_preview",
    "FxReconciliationResult",
    "reconcile_fx_private_state_with_paper",
    "FxLiveReadinessContractResult",
    "evaluate_fx_live_readiness_contract",
    "CommandLedgerReadResult",
    "CommandLedgerRecord",
    "CommandLedgerSummary",
    "CommandRequest",
    "CommandType",
    "CommandValidationResult",
    "DryRunExecutionResult",
    "ModeChangeCommandApplyPreview",
    "ModeChangeCommandApplyResult",
    "ModeChangeCommandReadinessApplyPreview",
    "ModeChangeCommandReadinessApplyResult",
    "ModeChangeCommandRequestResult",
    "ModeStateReadResult",
    "ModeStateRecord",
    "ModeStateSummary",
    "OrderIntent",
    "OrderSide",
    "OrderType",
    "PaperOrder",
    "PaperOrderStatus",
    "PaperOrderIntentBuildResult",
    "DEFAULT_MODE_STATE",
    "append_command_ledger_record",
    "apply_latest_mode_change_command_once",
    "apply_latest_mode_change_command_once_with_readiness_recheck",
    "preview_latest_mode_change_command_apply",
    "preview_latest_mode_change_command_apply_with_readiness_recheck",
    "append_mode_state_record",
    "build_command_ledger_record",
    "build_mode_change_command_request_record",
    "build_mode_state_record_from_command",
    "build_order_intent_from_decision",
    "build_fx_paper_order_intent_from_service_input",
    "create_paper_order",
    "current_mode_state",
    "default_command_ledger_path",
    "default_mode_state_ledger_path",
    "evaluate_armed_dry_run_intent",
    "paper_order_id_for_intent",
    "read_command_ledger",
    "read_command_ledger_rows",
    "read_mode_state_records",
    "submit_mode_change_command_request",
    "summarize_command_ledger",
    "summarize_mode_state",
    "validate_and_append_command",
    "validate_command_request",
    "validate_execution_market_service_input_for_paper",
]
