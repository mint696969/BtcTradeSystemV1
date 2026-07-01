# path: ./btcts_next/src/btcts/prediction/market_regime/source_snapshot.py
# desc: Read-only source snapshot contracts for market-regime engine adapters. No UI, broker, scheduler, or artifact writes.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Mapping, Tuple

MARKET_REGIME_SOURCE_SNAPSHOT_VERSION = "prediction.market_regime.source_snapshot.ps_q27h.v1"


@dataclass(frozen=True)
class SourceAdapterSafetyFlags:
    read_only: bool = True
    non_executing: bool = True
    runtime_artifact_write_allowed: bool = False
    status_artifact_write_allowed: bool = False
    prediction_artifact_write_allowed: bool = False
    view_artifact_write_allowed: bool = False
    scheduler_enabled: bool = False
    producer_enabled: bool = False
    autotrade_trigger_allowed: bool = False
    broker_private_api_allowed: bool = False
    ledger_append_allowed: bool = False
    mode_apply_allowed: bool = False
    parameter_apply_allowed: bool = False
    would_send_to_broker: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class JsonSourceArtifact:
    relative_path: str
    exists: bool
    ok: bool
    data: Mapping[str, Any] = field(default_factory=dict)
    bytes_read: int = 0
    truncated: bool = False
    error: str | None = None
    safety: SourceAdapterSafetyFlags = field(default_factory=SourceAdapterSafetyFlags)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relative_path": self.relative_path,
            "exists": self.exists,
            "ok": self.ok,
            "data": dict(self.data),
            "bytes_read": int(self.bytes_read),
            "truncated": self.truncated,
            "error": self.error,
            "safety": self.safety.to_dict(),
        }


@dataclass(frozen=True)
class ForecastRecordsSnapshot:
    relative_path: str
    ok: bool
    record_count: int
    market_regime_record_count: int
    market_regime_horizons_sec: Tuple[int, ...] = ()
    market_regime_records: Tuple[Mapping[str, Any], ...] = ()
    scanned_lines: int = 0
    truncated: bool = False
    warnings: Tuple[str, ...] = ()
    safety: SourceAdapterSafetyFlags = field(default_factory=SourceAdapterSafetyFlags)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "relative_path": self.relative_path,
            "ok": self.ok,
            "record_count": int(self.record_count),
            "market_regime_record_count": int(self.market_regime_record_count),
            "market_regime_horizons_sec": list(self.market_regime_horizons_sec),
            "market_regime_records": [dict(record) for record in self.market_regime_records],
            "scanned_lines": int(self.scanned_lines),
            "truncated": self.truncated,
            "warnings": list(self.warnings),
            "safety": self.safety.to_dict(),
        }


@dataclass(frozen=True)
class NowcastSourceSnapshot:
    market_state: JsonSourceArtifact
    health: JsonSourceArtifact
    executions: JsonSourceArtifact
    daemon: JsonSourceArtifact
    safety: SourceAdapterSafetyFlags = field(default_factory=SourceAdapterSafetyFlags)

    @property
    def ok(self) -> bool:
        return self.market_state.ok and self.health.ok

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "market_state": self.market_state.to_dict(),
            "health": self.health.to_dict(),
            "executions": self.executions.to_dict(),
            "daemon": self.daemon.to_dict(),
            "safety": self.safety.to_dict(),
        }


@dataclass(frozen=True)
class MarketRegimeSourceSnapshot:
    hot_root: str
    latest_manifest: JsonSourceArtifact
    latest_prediction: JsonSourceArtifact
    forecast_records: ForecastRecordsSnapshot
    nowcast: NowcastSourceSnapshot
    missing_sources: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    logic_version: str = MARKET_REGIME_SOURCE_SNAPSHOT_VERSION
    safety: SourceAdapterSafetyFlags = field(default_factory=SourceAdapterSafetyFlags)

    @property
    def ok(self) -> bool:
        return self.latest_manifest.ok and self.forecast_records.ok and self.nowcast.ok

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "logic_version": self.logic_version,
            "hot_root": self.hot_root,
            "latest_manifest": self.latest_manifest.to_dict(),
            "latest_prediction": self.latest_prediction.to_dict(),
            "forecast_records": self.forecast_records.to_dict(),
            "nowcast": self.nowcast.to_dict(),
            "missing_sources": list(self.missing_sources),
            "warnings": list(self.warnings),
            "safety": self.safety.to_dict(),
        }
