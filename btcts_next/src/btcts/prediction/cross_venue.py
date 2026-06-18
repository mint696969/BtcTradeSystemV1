# path: ./btcts_next/src/btcts/prediction/cross_venue.py
# desc: Non-executing cross-venue and Spot-FX basis contracts over already-provided venue snapshots.

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, Mapping, Tuple

from .source_quality import SourceQualityStatus

LOGIC_VERSION = "prediction_cross_venue_basis.s127.v1"


@dataclass(frozen=True)
class VenueReferencePrice:
    source_id: str
    venue: str
    symbol: str
    price: float
    event_ts: str | None = None
    source_family: str = "provided_venue_snapshot"
    market_role: str = "reference"
    usable: bool = True
    quality_blockers: Tuple[str, ...] = ()
    public_data_only: bool = True
    execution_enabled: bool = False
    read_only: bool = True
    non_executing: bool = True

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["quality_blockers"] = list(self.quality_blockers)
        return data


@dataclass(frozen=True)
class SpotFxBasisSummary:
    fx_price: float | None = None
    spot_price: float | None = None
    basis: float | None = None
    basis_pct: float | None = None
    premium_discount_state: str = "unknown"
    blockers: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["blockers"] = list(self.blockers)
        return data


@dataclass(frozen=True)
class LeadLagSkeleton:
    leading_venue: str | None = None
    lagging_venue: str | None = None
    confidence: str = "unknown"
    method: str = "snapshot_dispersion_only"
    notes: Tuple[str, ...] = ("requires time-series source later",)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["notes"] = list(self.notes)
        return data


@dataclass(frozen=True)
class CrossVenueReferenceSummary:
    logic_version: str = LOGIC_VERSION
    generated_at: str | None = None
    venue_count: int = 0
    usable_venue_count: int = 0
    reference_price: float | None = None
    min_price: float | None = None
    max_price: float | None = None
    max_deviation_pct: float | None = None
    agreement_state: str = "unknown"
    venue_prices: Tuple[VenueReferencePrice, ...] = ()
    spot_fx_basis: SpotFxBasisSummary = SpotFxBasisSummary()
    lead_lag: LeadLagSkeleton = LeadLagSkeleton()
    blockers: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()
    read_only: bool = True
    non_executing: bool = True
    would_call_external_api: bool = False
    would_collect_public_source: bool = False
    would_write_runtime_artifact: bool = False
    would_send_to_broker: bool = False

    @property
    def usable(self) -> bool:
        return not self.blockers

    def to_dict(self) -> Dict[str, Any]:
        return {
            "logic_version": self.logic_version,
            "generated_at": self.generated_at,
            "venue_count": self.venue_count,
            "usable_venue_count": self.usable_venue_count,
            "reference_price": self.reference_price,
            "min_price": self.min_price,
            "max_price": self.max_price,
            "max_deviation_pct": self.max_deviation_pct,
            "agreement_state": self.agreement_state,
            "venue_prices": [item.to_dict() for item in self.venue_prices],
            "spot_fx_basis": self.spot_fx_basis.to_dict(),
            "lead_lag": self.lead_lag.to_dict(),
            "blockers": list(self.blockers),
            "warnings": list(self.warnings),
            "usable": self.usable,
            "read_only": self.read_only,
            "non_executing": self.non_executing,
            "would_call_external_api": self.would_call_external_api,
            "would_collect_public_source": self.would_collect_public_source,
            "would_write_runtime_artifact": self.would_write_runtime_artifact,
            "would_send_to_broker": self.would_send_to_broker,
        }


def _iso_now(now: datetime | None) -> str:
    dt = now.astimezone(timezone.utc) if now else datetime.now(timezone.utc)
    return dt.replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _float_or_none(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except Exception:
        return None


def _quality_for(source_id: str, source_quality_by_id: Mapping[str, SourceQualityStatus] | None) -> SourceQualityStatus | None:
    if not source_quality_by_id:
        return None
    return source_quality_by_id.get(source_id)


def _normalize_snapshots(
    snapshots: Iterable[Mapping[str, Any]],
    source_quality_by_id: Mapping[str, SourceQualityStatus] | None,
) -> tuple[list[VenueReferencePrice], list[str], list[str]]:
    prices: list[VenueReferencePrice] = []
    blockers: list[str] = []
    warnings: list[str] = []
    for raw in snapshots:
        source_id = str(raw.get("source_id") or "").strip()
        venue = str(raw.get("venue") or "").strip()
        symbol = str(raw.get("symbol") or "").strip()
        price = _float_or_none(raw.get("price") or raw.get("last_price") or raw.get("mid_price"))
        if not source_id or not venue or not symbol or price is None or price <= 0:
            warnings.append("venue_snapshot_invalid_or_incomplete")
            continue
        quality = _quality_for(source_id, source_quality_by_id)
        quality_blockers = tuple(quality.blockers) if quality else ()
        usable = bool(quality.usable if quality else True)
        if not usable:
            warnings.append("venue_snapshot_quality_blocked")
        prices.append(
            VenueReferencePrice(
                source_id=source_id,
                venue=venue,
                symbol=symbol,
                price=price,
                event_ts=str(raw.get("event_ts") or raw.get("ts") or "") or None,
                source_family=str(raw.get("source_family") or "provided_venue_snapshot"),
                market_role=str(raw.get("market_role") or "reference"),
                usable=usable,
                quality_blockers=quality_blockers,
                public_data_only=bool(raw.get("public_data_only", True)),
                execution_enabled=False,
            )
        )
    if not prices:
        blockers.append("venue_reference_snapshots_missing_or_unusable")
    if not [item for item in prices if item.usable]:
        blockers.append("usable_venue_reference_prices_missing")
    return prices, blockers, warnings


def _spot_fx_basis(prices: list[VenueReferencePrice]) -> SpotFxBasisSummary:
    fx = next((p for p in prices if p.usable and (p.market_role == "bitflyer_fx" or p.symbol.upper() == "FX_BTC_JPY")), None)
    spot = next((p for p in prices if p.usable and (p.market_role == "bitflyer_spot" or p.symbol.upper() == "BTC_JPY") and p.venue.lower() == "bitflyer"), None)
    blockers: list[str] = []
    if fx is None:
        blockers.append("bitflyer_fx_reference_missing")
    if spot is None:
        blockers.append("bitflyer_spot_reference_missing")
    if fx is None or spot is None or spot.price == 0:
        return SpotFxBasisSummary(blockers=tuple(blockers))
    basis = fx.price - spot.price
    basis_pct = basis / spot.price
    if basis_pct > 0.001:
        state = "fx_premium"
    elif basis_pct < -0.001:
        state = "fx_discount"
    else:
        state = "near_parity"
    return SpotFxBasisSummary(fx.price, spot.price, basis, round(basis_pct, 8), state, tuple(blockers))


def _lead_lag_skeleton(usable: list[VenueReferencePrice]) -> LeadLagSkeleton:
    if len(usable) < 2:
        return LeadLagSkeleton()
    sorted_prices = sorted(usable, key=lambda item: item.price)
    return LeadLagSkeleton(leading_venue=sorted_prices[-1].venue, lagging_venue=sorted_prices[0].venue, confidence="low")


def build_cross_venue_reference_summary(
    snapshots: Iterable[Mapping[str, Any]],
    *,
    source_quality_by_id: Mapping[str, SourceQualityStatus] | None = None,
    now: datetime | None = None,
    agreement_warn_deviation_pct: float = 0.003,
) -> CrossVenueReferenceSummary:
    venue_prices, blockers, warnings = _normalize_snapshots(snapshots, source_quality_by_id)
    usable = [item for item in venue_prices if item.usable]
    reference_price: float | None = None
    min_price: float | None = None
    max_price: float | None = None
    max_deviation_pct: float | None = None
    agreement = "unknown"
    if usable:
        values = [item.price for item in usable]
        reference_price = sum(values) / len(values)
        min_price = min(values)
        max_price = max(values)
        if reference_price > 0:
            max_deviation_pct = max(abs(max_price - reference_price), abs(reference_price - min_price)) / reference_price
        if max_deviation_pct is None:
            agreement = "unknown"
        elif max_deviation_pct <= agreement_warn_deviation_pct:
            agreement = "confirmed"
        else:
            agreement = "divergent"
            warnings.append("cross_venue_price_divergence")
    return CrossVenueReferenceSummary(
        generated_at=_iso_now(now),
        venue_count=len(venue_prices),
        usable_venue_count=len(usable),
        reference_price=reference_price,
        min_price=min_price,
        max_price=max_price,
        max_deviation_pct=round(max_deviation_pct, 8) if max_deviation_pct is not None else None,
        agreement_state=agreement,
        venue_prices=tuple(venue_prices),
        spot_fx_basis=_spot_fx_basis(venue_prices),
        lead_lag=_lead_lag_skeleton(usable),
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(warnings)),
    )
