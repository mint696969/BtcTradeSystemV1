# path: ./btcts_next/src/btcts/prediction/market_regime/artifact_contracts.py
# desc: Pure market-regime artifact contracts for latest.json/latest_cards.json/latest_read_model.json/status/run manifest. No filesystem writes, UI imports, scheduler, broker, or AutoTrade behavior.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Sequence, Tuple

from .contracts import MarketRegimePredictionPacket, MarketRegimeSafetyFlags

MARKET_REGIME_ARTIFACT_CONTRACT_VERSION = "prediction.market_regime.artifact_contracts.2026_07_08.v1"
MARKET_REGIME_ARTIFACT_FAMILY = "prediction/market_regime"
MARKET_REGIME_LATEST_SCHEMA_VERSION = "market_regime_latest.2026_07_08.v1"
MARKET_REGIME_LATEST_CARDS_SCHEMA_VERSION = "market_regime_latest_cards.2026_07_08.v1"
MARKET_REGIME_LATEST_READ_MODEL_SCHEMA_VERSION = "market_regime_latest_read_model.2026_07_08.v1"
MARKET_REGIME_STATUS_SCHEMA_VERSION = "market_regime_status.2026_07_08.v1"
MARKET_REGIME_RUN_MANIFEST_SCHEMA_VERSION = "market_regime_run_manifest.2026_07_08.v1"
MARKET_REGIME_TRACE_SCHEMA_VERSION = "market_regime_trace.2026_07_08.v1"
MARKET_REGIME_OUTCOME_SCHEMA_VERSION = "market_regime_outcome.2026_07_08.v1"

LATEST_JSON_RELPATH = "prediction/market_regime/latest.json"
LATEST_CARDS_JSON_RELPATH = "prediction/market_regime/latest_cards.json"
LATEST_READ_MODEL_JSON_RELPATH = "prediction/market_regime/latest_read_model.json"
STATUS_JSON_RELPATH = "prediction/market_regime/status.json"

_REQUIRED_CARD_KEYS = ("horizon", "regime_code", "regime_label", "confidence_percent", "freshness_badge")
_FORBIDDEN_RAW_KEYS = (
    "raw_candles",
    "raw_orderbook",
    "raw_trades",
    "raw_executions",
    "raw_market_payload",
    "raw_source_payload",
)


@dataclass(frozen=True)
class MarketRegimeArtifactSafety:
    read_only: bool = True
    display_only: bool = True
    non_executing: bool = True
    ui_render_invokes_classifier: bool = False
    ui_render_reads_raw_market_source: bool = False
    runtime_artifact_write_allowed_by_contract: bool = False
    status_artifact_write_allowed_by_contract: bool = False
    prediction_artifact_write_allowed_by_contract: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    order_intent_submitted: bool = False
    ledger_append_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketRegimeArtifactRefs:
    latest_json: str = LATEST_JSON_RELPATH
    latest_cards_json: str = LATEST_CARDS_JSON_RELPATH
    latest_read_model_json: str = LATEST_READ_MODEL_JSON_RELPATH
    status_json: str = STATUS_JSON_RELPATH
    run_manifest_json: str = ""
    trace_part_jsonl: str = ""
    outcome_part_jsonl: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class MarketRegimeLatestCardsArtifact:
    generated_at: str
    run_id: str
    cards: Tuple[Mapping[str, Any], ...]
    prediction_id: str = ""
    parameter_set_id: str = "market_regime_engine_parameter_set.v1"
    signal_registry_version: str = "market_regime_signal_registry.2026_07_08.v1"
    horizon_weight_version: str = "market_regime_horizon_weight.2026_07_08.v1"
    outcome_rule_version: str = "market_regime_outcome_rule.2026_07_08.v1"
    schema_version: str = MARKET_REGIME_LATEST_CARDS_SCHEMA_VERSION
    artifact_family: str = MARKET_REGIME_ARTIFACT_FAMILY
    artifact_kind: str = "latest_cards"
    prediction_family_id: str = "market_regime"
    source_refs: Mapping[str, Any] = field(default_factory=dict)
    compact_summary: Mapping[str, Any] = field(default_factory=dict)
    safety: MarketRegimeArtifactSafety = field(default_factory=MarketRegimeArtifactSafety)

    @property
    def horizon_count(self) -> int:
        return len(self.cards)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_family": self.artifact_family,
            "artifact_kind": self.artifact_kind,
            "prediction_family_id": self.prediction_family_id,
            "generated_at": self.generated_at,
            "run_id": self.run_id,
            "prediction_id": self.prediction_id,
            "parameter_set_id": self.parameter_set_id,
            "signal_registry_version": self.signal_registry_version,
            "horizon_weight_version": self.horizon_weight_version,
            "outcome_rule_version": self.outcome_rule_version,
            "horizon_count": self.horizon_count,
            "cards": [dict(card) for card in self.cards],
            "source_refs": dict(self.source_refs),
            "compact_summary": dict(self.compact_summary),
            "safety": self.safety.to_dict(),
        }


@dataclass(frozen=True)
class MarketRegimeLatestArtifact:
    generated_at: str
    run_id: str
    prediction_packet: Mapping[str, Any]
    refs: MarketRegimeArtifactRefs = field(default_factory=MarketRegimeArtifactRefs)
    schema_version: str = MARKET_REGIME_LATEST_SCHEMA_VERSION
    artifact_family: str = MARKET_REGIME_ARTIFACT_FAMILY
    artifact_kind: str = "latest"
    prediction_family_id: str = "market_regime"
    safety: MarketRegimeArtifactSafety = field(default_factory=MarketRegimeArtifactSafety)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_family": self.artifact_family,
            "artifact_kind": self.artifact_kind,
            "prediction_family_id": self.prediction_family_id,
            "generated_at": self.generated_at,
            "run_id": self.run_id,
            "prediction_packet": dict(self.prediction_packet),
            "refs": self.refs.to_dict(),
            "safety": self.safety.to_dict(),
        }


@dataclass(frozen=True)
class MarketRegimeReadModelArtifact:
    generated_at: str
    run_id: str
    horizons: Tuple[Mapping[str, Any], ...]
    schema_version: str = MARKET_REGIME_LATEST_READ_MODEL_SCHEMA_VERSION
    artifact_family: str = MARKET_REGIME_ARTIFACT_FAMILY
    artifact_kind: str = "latest_read_model"
    prediction_family_id: str = "market_regime"
    explanation_note: str = "card percent is market-regime reading confidence, not win rate"
    source_contribution_summary: Mapping[str, Any] = field(default_factory=dict)
    conflict_summary: Mapping[str, Any] = field(default_factory=dict)
    invalidation_summary: Mapping[str, Any] = field(default_factory=dict)
    safety: MarketRegimeArtifactSafety = field(default_factory=MarketRegimeArtifactSafety)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_family": self.artifact_family,
            "artifact_kind": self.artifact_kind,
            "prediction_family_id": self.prediction_family_id,
            "generated_at": self.generated_at,
            "run_id": self.run_id,
            "explanation_note": self.explanation_note,
            "horizons": [dict(horizon) for horizon in self.horizons],
            "source_contribution_summary": dict(self.source_contribution_summary),
            "conflict_summary": dict(self.conflict_summary),
            "invalidation_summary": dict(self.invalidation_summary),
            "safety": self.safety.to_dict(),
        }


@dataclass(frozen=True)
class MarketRegimeStatusArtifact:
    generated_at: str
    status: str
    latest_run_id: str = ""
    latest_cards_available: bool = False
    latest_read_model_available: bool = False
    trace_ledger_available: bool = False
    outcome_resolver_available: bool = False
    schema_version: str = MARKET_REGIME_STATUS_SCHEMA_VERSION
    artifact_family: str = MARKET_REGIME_ARTIFACT_FAMILY
    artifact_kind: str = "status"
    prediction_family_id: str = "market_regime"
    safety: MarketRegimeArtifactSafety = field(default_factory=MarketRegimeArtifactSafety)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_family": self.artifact_family,
            "artifact_kind": self.artifact_kind,
            "prediction_family_id": self.prediction_family_id,
            "generated_at": self.generated_at,
            "status": self.status,
            "latest_run_id": self.latest_run_id,
            "latest_cards_available": self.latest_cards_available,
            "latest_read_model_available": self.latest_read_model_available,
            "trace_ledger_available": self.trace_ledger_available,
            "outcome_resolver_available": self.outcome_resolver_available,
            "safety": self.safety.to_dict(),
        }


@dataclass(frozen=True)
class MarketRegimeRunManifestArtifact:
    generated_at: str
    run_id: str
    refs: MarketRegimeArtifactRefs
    schema_version: str = MARKET_REGIME_RUN_MANIFEST_SCHEMA_VERSION
    artifact_family: str = MARKET_REGIME_ARTIFACT_FAMILY
    artifact_kind: str = "run_manifest"
    prediction_family_id: str = "market_regime"
    engine_version: str = "market_regime_engine.v1"
    safety: MarketRegimeArtifactSafety = field(default_factory=MarketRegimeArtifactSafety)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "artifact_family": self.artifact_family,
            "artifact_kind": self.artifact_kind,
            "prediction_family_id": self.prediction_family_id,
            "generated_at": self.generated_at,
            "run_id": self.run_id,
            "engine_version": self.engine_version,
            "refs": self.refs.to_dict(),
            "safety": self.safety.to_dict(),
        }


def artifact_relative_paths() -> Dict[str, str]:
    return MarketRegimeArtifactRefs().to_dict()


def build_market_regime_latest_artifact(*, packet: MarketRegimePredictionPacket, run_id: str) -> Dict[str, Any]:
    return MarketRegimeLatestArtifact(
        generated_at=packet.generated_at,
        run_id=run_id,
        prediction_packet=packet.to_dict(),
    ).to_dict()


def build_market_regime_latest_cards_artifact(
    *,
    generated_at: str,
    run_id: str,
    cards: Sequence[Mapping[str, Any]],
    prediction_id: str = "",
    parameter_set_id: str = "market_regime_engine_parameter_set.v1",
    source_refs: Mapping[str, Any] | None = None,
    compact_summary: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    return MarketRegimeLatestCardsArtifact(
        generated_at=generated_at,
        run_id=run_id,
        prediction_id=prediction_id,
        parameter_set_id=parameter_set_id,
        cards=tuple(dict(card) for card in cards),
        source_refs=dict(source_refs or {}),
        compact_summary=dict(compact_summary or {}),
    ).to_dict()


def build_market_regime_latest_read_model_artifact(
    *,
    generated_at: str,
    run_id: str,
    horizons: Sequence[Mapping[str, Any]],
    source_contribution_summary: Mapping[str, Any] | None = None,
    conflict_summary: Mapping[str, Any] | None = None,
    invalidation_summary: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    return MarketRegimeReadModelArtifact(
        generated_at=generated_at,
        run_id=run_id,
        horizons=tuple(dict(horizon) for horizon in horizons),
        source_contribution_summary=dict(source_contribution_summary or {}),
        conflict_summary=dict(conflict_summary or {}),
        invalidation_summary=dict(invalidation_summary or {}),
    ).to_dict()


def build_market_regime_status_artifact(*, generated_at: str, status: str, latest_run_id: str = "", trace_ledger_available: bool = False, outcome_resolver_available: bool = False) -> Dict[str, Any]:
    return MarketRegimeStatusArtifact(
        generated_at=generated_at,
        status=status,
        latest_run_id=latest_run_id,
        latest_cards_available=bool(latest_run_id),
        latest_read_model_available=bool(latest_run_id),
        trace_ledger_available=bool(trace_ledger_available),
        outcome_resolver_available=bool(outcome_resolver_available),
    ).to_dict()


def build_market_regime_run_manifest_artifact(*, generated_at: str, run_id: str, refs: MarketRegimeArtifactRefs | None = None) -> Dict[str, Any]:
    return MarketRegimeRunManifestArtifact(
        generated_at=generated_at,
        run_id=run_id,
        refs=refs or MarketRegimeArtifactRefs(),
    ).to_dict()


def _has_forbidden_raw_keys(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            if str(key) in _FORBIDDEN_RAW_KEYS:
                return True
            if _has_forbidden_raw_keys(nested):
                return True
    elif isinstance(value, list):
        return any(_has_forbidden_raw_keys(item) for item in value)
    return False


def validate_market_regime_latest_cards_artifact(payload: Mapping[str, Any]) -> Dict[str, Any]:
    failures: list[str] = []
    if payload.get("schema_version") != MARKET_REGIME_LATEST_CARDS_SCHEMA_VERSION:
        failures.append("schema_version_mismatch")
    if payload.get("artifact_family") != MARKET_REGIME_ARTIFACT_FAMILY:
        failures.append("artifact_family_mismatch")
    if payload.get("artifact_kind") != "latest_cards":
        failures.append("artifact_kind_mismatch")
    if payload.get("prediction_family_id") != "market_regime":
        failures.append("prediction_family_id_mismatch")
    cards = payload.get("cards")
    if not isinstance(cards, list) or not cards:
        failures.append("cards_missing_or_empty")
        cards = []
    for index, card in enumerate(cards):
        if not isinstance(card, Mapping):
            failures.append(f"card_{index}_not_mapping")
            continue
        for key in _REQUIRED_CARD_KEYS:
            if key not in card:
                failures.append(f"card_{index}_missing_{key}")
        confidence = card.get("confidence_percent")
        if not isinstance(confidence, int) or confidence < 0 or confidence > 99:
            failures.append(f"card_{index}_confidence_percent_out_of_range")
    if int(payload.get("horizon_count") or -1) != len(cards):
        failures.append("horizon_count_mismatch")
    safety = payload.get("safety") if isinstance(payload.get("safety"), Mapping) else {}
    for key in (
        "ui_render_invokes_classifier",
        "ui_render_reads_raw_market_source",
        "autotrade_trigger_allowed",
        "broker_private_api_allowed",
        "order_intent_submitted",
        "ledger_append_allowed",
        "would_send_to_broker",
    ):
        if safety.get(key) is not False:
            failures.append(f"safety_{key}_not_false")
    if _has_forbidden_raw_keys(payload):
        failures.append("forbidden_raw_payload_key_present")
    return {
        "ok": not failures,
        "validator_version": MARKET_REGIME_ARTIFACT_CONTRACT_VERSION,
        "failure_count": len(failures),
        "failures": failures,
        "card_count": len(cards),
    }
