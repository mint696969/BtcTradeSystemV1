# path: ./btcts_next/src/btcts/prediction/market_regime/tests/test_market_regime_shadow_runtime_preflight_once.py
# desc: MR-F8.8 orchestration tests for the read-only runtime preflight once boundary.

from __future__ import annotations

from types import MappingProxyType, SimpleNamespace

import json
import pytest

from btcts.prediction.market_regime.contracts import MarketRegimeCode
from btcts.prediction.market_regime.tools import shadow_runtime_preflight_once as module


def test_future_only_score_view_removes_current_horizon() -> None:
    report = {
        "market_regime_only": True,
        "horizon_count": 8,
        "horizons": [
            {"horizon_sec": value, "horizon_key": "current" if value == 0 else f"{value}s"}
            for value in (0, 300, 900, 1800, 3600, 21600, 43200, 86400)
        ],
    }
    result = module._future_only_signal_score_report(report)
    assert result["horizon_count"] == 7
    assert [row["horizon_sec"] for row in result["horizons"]] == [300, 900, 1800, 3600, 21600, 43200, 86400]
    assert report["horizon_count"] == 8


def test_future_only_score_view_requires_all_seven_horizons() -> None:
    with pytest.raises(ValueError, match="future_horizon_count_invalid"):
        module._future_only_signal_score_report({
            "horizons": [{"horizon_sec": 0}, {"horizon_sec": 300}],
        })


def test_runtime_once_orchestrates_read_only_components(monkeypatch, tmp_path) -> None:
    calls: list[str] = []
    source_snapshot = SimpleNamespace(ok=True)
    feature_bundle = SimpleNamespace(
        signals=(SimpleNamespace(name="current_l4_candle_window_generated_at", available=True, value="2026-07-15T00:00:00Z"),),
        available_signal_count=lambda: 42,
    )
    prediction_packet = SimpleNamespace(
        predictions=(SimpleNamespace(horizon_sec=0, regime_code=MarketRegimeCode.RANGE),)
    )
    shadow_packet = MappingProxyType({"forecasts": ()})
    runtime_bundle = MappingProxyType({"runtime_source_ready": True})
    preflight = MappingProxyType({"pair_count": 7, "pairs": ()})
    runtime_artifact = MappingProxyType({"horizon_count": 8, "horizons": ()})

    monkeypatch.setattr(module, "build_default_market_regime_parameter_set_registry", lambda: SimpleNamespace(active_parameter_set=lambda: object()))
    monkeypatch.setattr(module, "build_market_regime_source_snapshot", lambda root: calls.append("snapshot") or source_snapshot)
    monkeypatch.setattr(module, "build_market_regime_feature_bundle", lambda *args, **kwargs: calls.append("features") or feature_bundle)
    monkeypatch.setattr(module, "read_persisted_current_state", lambda root: calls.append("state") or {"regime_code": "RANGE"})
    monkeypatch.setattr(module, "classify_market_regime_feature_bundle", lambda *args, **kwargs: calls.append("classify") or prediction_packet)
    score_report = {
        "market_regime_only": True,
        "horizon_count": 8,
        "horizons": [
            {"horizon_sec": value, "horizon_key": "current" if value == 0 else f"{value}s"}
            for value in (0, 300, 900, 1800, 3600, 21600, 43200, 86400)
        ],
    }
    observed_future_reports: list[dict] = []
    monkeypatch.setattr(module, "score_market_regime_signals", lambda bundle, **kwargs: calls.append("score") or score_report)
    monkeypatch.setattr(
        module,
        "build_market_regime_future_shadow_packet",
        lambda **kwargs: calls.append("packet") or observed_future_reports.append(kwargs["signal_score_report"]) or shadow_packet,
    )
    monkeypatch.setattr(module, "future_origin_l4_candle_rows", lambda snapshot: ({"time_utc": "x"},) * 60)
    monkeypatch.setattr(module, "build_market_regime_origin_feature_runtime_bundle", lambda **kwargs: calls.append("runtime") or runtime_bundle)
    monkeypatch.setattr(
        module,
        "build_future_shadow_runtime_preflight_report",
        lambda **kwargs: calls.append("preflight") or observed_future_reports.append(kwargs["signal_score_report"]) or preflight,
    )
    monkeypatch.setattr(
        module,
        "build_market_regime_runtime_horizon_artifact",
        lambda **kwargs: calls.append("artifact") or runtime_artifact,
    )

    result = module.build_shadow_runtime_preflight_once(
        hot_root=tmp_path,
        generated_at="2026-07-15T00:00:00Z",
        shadow_candidate_id="candidate:shadow",
    )
    assert calls == ["snapshot", "features", "state", "classify", "runtime", "score", "packet", "preflight", "artifact"]
    assert len(observed_future_reports) == 2
    assert all(item["horizon_count"] == 7 for item in observed_future_reports)
    assert all([row["horizon_sec"] for row in item["horizons"]] == [300, 900, 1800, 3600, 21600, 43200, 86400] for item in observed_future_reports)
    assert result["pair_count"] == 7
    assert result["current_regime"] == "RANGE"
    assert result["runtime_horizon_artifact_built"] is True
    assert result["runtime_horizon_artifact_persisted"] is False
    assert result["runtime_horizon_artifact"]["horizon_count"] == 8
    assert result["writer_invoked"] is False
    assert result["writes_dhot"] is False


def test_cli_requires_preflight() -> None:
    with pytest.raises(SystemExit) as exc:
        module.main([
            "--hot-root", "D:/btc_ts_hot",
            "--generated-at", "2026-07-15T00:00:00Z",
            "--shadow-candidate-id", "candidate:shadow",
        ])
    assert exc.value.code == 2


def test_missing_candidate_fails_closed(tmp_path) -> None:
    with pytest.raises(ValueError, match="shadow_candidate_missing"):
        module.build_shadow_runtime_preflight_once(
            hot_root=tmp_path,
            generated_at="2026-07-15T00:00:00Z",
            shadow_candidate_id="",
        )


def test_canonical_utc_seconds_normalizes_fractional_and_offset_input() -> None:
    assert module._canonical_utc_seconds(
        "2026-07-15T17:38:36.987654+09:00",
        "generated_at",
    ) == "2026-07-15T08:38:36Z"


def test_canonical_utc_seconds_requires_timezone() -> None:
    with pytest.raises(ValueError, match="timestamp_timezone_missing:generated_at"):
        module._canonical_utc_seconds("2026-07-15T08:38:36", "generated_at")


def test_json_native_preserves_nested_mapping_proxy_and_pairs() -> None:
    payload = MappingProxyType({
        "generated_at": "2026-07-15T08:50:31Z",
        "pairs": (
            MappingProxyType({
                "pair_id": "pair:1",
                "candidate_count": 2,
                "trace_plan": MappingProxyType({
                    "trace_count": 2,
                    "trace_ids": ("trace:a", "trace:b"),
                    "persistence_plan": MappingProxyType({"would_write": False}),
                }),
            }),
        ),
    })
    native = module._json_native(payload)
    encoded = json.dumps(native)
    decoded = json.loads(encoded)
    assert isinstance(decoded, dict)
    assert isinstance(decoded["pairs"], list)
    assert decoded["pairs"][0]["candidate_count"] == 2
    assert decoded["pairs"][0]["trace_plan"]["trace_count"] == 2
    assert decoded["pairs"][0]["trace_plan"]["persistence_plan"]["would_write"] is False


def test_runtime_once_result_contains_json_native_preflight(monkeypatch, tmp_path) -> None:
    source_snapshot = SimpleNamespace(ok=True)
    feature_bundle = SimpleNamespace(
        signals=(SimpleNamespace(name="current_l4_candle_window_generated_at", available=True, value="2026-07-15T00:00:00Z"),),
        available_signal_count=lambda: 42,
    )
    prediction_packet = SimpleNamespace(
        predictions=(SimpleNamespace(horizon_sec=0, regime_code=MarketRegimeCode.RANGE),)
    )
    score_report = {
        "market_regime_only": True,
        "horizon_count": 8,
        "horizons": [{"horizon_sec": value} for value in (0, 300, 900, 1800, 3600, 21600, 43200, 86400)],
    }
    preflight = MappingProxyType({
        "pair_count": 7,
        "pairs": tuple(MappingProxyType({"pair_id": f"pair:{index}"}) for index in range(7)),
    })
    runtime_artifact = MappingProxyType({
        "horizon_count": 8,
        "horizons": tuple(MappingProxyType({"horizon_sec": value}) for value in (0, 300, 900, 1800, 3600, 21600, 43200, 86400)),
        "ui_inference_allowed": False,
        "ui_confidence_recalculation_allowed": False,
        "safety": MappingProxyType({"writes_dhot": False, "websocket_opened": False}),
    })
    monkeypatch.setattr(module, "build_default_market_regime_parameter_set_registry", lambda: SimpleNamespace(active_parameter_set=lambda: object()))
    monkeypatch.setattr(module, "build_market_regime_source_snapshot", lambda root: source_snapshot)
    monkeypatch.setattr(module, "build_market_regime_feature_bundle", lambda *args, **kwargs: feature_bundle)
    monkeypatch.setattr(module, "read_persisted_current_state", lambda root: {"regime_code": "RANGE"})
    monkeypatch.setattr(module, "classify_market_regime_feature_bundle", lambda *args, **kwargs: prediction_packet)
    monkeypatch.setattr(module, "score_market_regime_signals", lambda bundle, **kwargs: score_report)
    monkeypatch.setattr(module, "build_market_regime_future_shadow_packet", lambda **kwargs: MappingProxyType({"forecasts": ()}))
    monkeypatch.setattr(module, "future_origin_l4_candle_rows", lambda snapshot: ({"time_utc": "x"},) * 60)
    monkeypatch.setattr(module, "build_market_regime_origin_feature_runtime_bundle", lambda **kwargs: MappingProxyType({"runtime_source_ready": True}))
    monkeypatch.setattr(module, "build_future_shadow_runtime_preflight_report", lambda **kwargs: preflight)
    monkeypatch.setattr(module, "build_market_regime_runtime_horizon_artifact", lambda **kwargs: runtime_artifact)
    result = module.build_shadow_runtime_preflight_once(
        hot_root=tmp_path,
        generated_at="2026-07-15T00:00:00.987Z",
        shadow_candidate_id="candidate:shadow",
    )
    assert result["generated_at"] == "2026-07-15T00:00:00Z"
    assert isinstance(result["preflight_report"], dict)
    assert isinstance(result["preflight_report"]["pairs"], list)
    assert len(result["preflight_report"]["pairs"]) == 7
    assert isinstance(result["runtime_horizon_artifact"], dict)
    assert isinstance(result["runtime_horizon_artifact"]["horizons"], list)
    assert len(result["runtime_horizon_artifact"]["horizons"]) == 8
    assert result["runtime_horizon_artifact"]["ui_inference_allowed"] is False
    assert result["runtime_horizon_artifact"]["safety"]["websocket_opened"] is False
