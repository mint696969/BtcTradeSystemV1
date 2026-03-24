# path: ./btcts_next/src/btcts/collector_vnext/exploration_config.py
# desc: Exploration Runtime 用の venue別設定を読み出し、collector 側で扱いやすい形へ正規化する。

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

from btcts.settings import svc as settings_svc


def _as_float(value, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default


def _as_int(value, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _as_bool(value, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _as_str_list(value, default: List[str]) -> List[str]:
    if not isinstance(value, list):
        return list(default)

    out: List[str] = []
    for item in value:
        text = str(item).strip()
        if text:
            out.append(text)

    return out or list(default)


def _env_override_int(name: str, current: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return current
    try:
        return int(raw)
    except Exception:
        return current


def _env_override_float(name: str, current: float) -> float:
    raw = os.getenv(name, "").strip()
    if not raw:
        return current
    try:
        return float(raw)
    except Exception:
        return current


def _as_float_list(value, default: List[float]) -> List[float]:
    if not isinstance(value, list):
        return list(default)

    out: List[float] = []
    for item in value:
        try:
            out.append(float(item))
        except Exception:
            continue

    return out if out else list(default)


@dataclass(frozen=True)
class ExplorationLimits:
    window_300s: int = 500
    window_60s_ip: int = 500


@dataclass(frozen=True)
class ExplorationControl:
    target_utilization: float = 0.95
    warn_utilization: float = 0.95
    hard_cap_utilization: float = 0.98

    crit_floor_ratio: float = 0.50
    crit_trigger_429_count: int = 2
    crit_trigger_window_sec: int = 30
    crit_cooldown_sec: int = 60

    recovery_start_after_sec: int = 180
    recovery_step_count: int = 5
    recovery_step_interval_sec: int = 180
    recovery_policy: str = "time_based"
    recovery_curve: str = "linear"
    recovery_steps: List[float] = field(default_factory=list)


@dataclass(frozen=True)
class ExplorationRequestClassConfig:
    enabled: bool = True
    weight: float = 1.0
    min_share: float = 0.0


@dataclass(frozen=True)
class ExplorationExchangeConfig:
    exchange: str
    enabled: bool
    limits: ExplorationLimits
    control: ExplorationControl
    request_priority: List[str] = field(default_factory=list)
    request_classes: Dict[str, ExplorationRequestClassConfig] = field(default_factory=dict)


@dataclass(frozen=True)
class ExplorationRuntimeConfig:
    exchanges: Dict[str, ExplorationExchangeConfig] = field(default_factory=dict)

    def enabled_exchanges(self) -> Dict[str, ExplorationExchangeConfig]:
        return {
            exchange: cfg
            for exchange, cfg in self.exchanges.items()
            if cfg.enabled
        }

    def get_exchange(self, exchange: str) -> ExplorationExchangeConfig | None:
        return self.exchanges.get(exchange)


def _normalize_request_classes(raw: dict) -> Dict[str, ExplorationRequestClassConfig]:
    if not isinstance(raw, dict):
        return {}

    out: Dict[str, ExplorationRequestClassConfig] = {}
    for request_class, item in raw.items():
        if not isinstance(item, dict):
            continue

        out[str(request_class)] = ExplorationRequestClassConfig(
            enabled=_as_bool(item.get("enabled"), True),
            weight=max(0.0, _as_float(item.get("weight"), 1.0)),
            min_share=max(0.0, min(1.0, _as_float(item.get("min_share"), 0.0))),
        )

    return out


def _normalize_exchange(exchange: str, raw: dict) -> ExplorationExchangeConfig:
    if not isinstance(raw, dict):
        raw = {}

    raw_limits = raw.get("limits") if isinstance(raw.get("limits"), dict) else {}
    raw_control = raw.get("control") if isinstance(raw.get("control"), dict) else {}
    raw_request_classes = (
        raw.get("request_classes") if isinstance(raw.get("request_classes"), dict) else {}
    )

    request_priority = _as_str_list(
        raw.get("request_priority"),
        ["board_snapshot", "rest_trades"],
    )
    request_classes = _normalize_request_classes(raw_request_classes)

    for request_class in request_priority:
        if request_class not in request_classes:
            request_classes[request_class] = ExplorationRequestClassConfig()

    target_utilization = max(
        0.0,
        min(1.0, _as_float(raw_control.get("target_utilization"), 0.95)),
    )
    warn_utilization = max(
        0.0,
        min(1.0, _as_float(raw_control.get("warn_utilization"), 0.95)),
    )
    hard_cap_utilization = max(
        0.0,
        min(1.0, _as_float(raw_control.get("hard_cap_utilization"), 0.98)),
    )
    crit_floor_ratio = max(
        0.0,
        min(1.0, _as_float(raw_control.get("crit_floor_ratio"), 0.50)),
    )
    crit_trigger_429_count = max(
        1,
        _as_int(raw_control.get("crit_trigger_429_count"), 2),
    )
    crit_trigger_window_sec = max(
        1,
        _as_int(raw_control.get("crit_trigger_window_sec"), 30),
    )
    crit_cooldown_sec = max(
        0,
        _as_int(raw_control.get("crit_cooldown_sec"), 60),
    )
    recovery_start_after_sec = max(
        0,
        _as_int(raw_control.get("recovery_start_after_sec"), 180),
    )
    recovery_step_count = max(
        1,
        _as_int(raw_control.get("recovery_step_count"), 5),
    )
    recovery_step_interval_sec = max(
        1,
        _as_int(raw_control.get("recovery_step_interval_sec"), 180),
    )
    recovery_curve = str(raw_control.get("recovery_curve") or "linear").strip() or "linear"
    recovery_steps = _as_float_list(raw_control.get("recovery_steps"), [])

    # test-only env overrides (do not change schema defaults)
    crit_cooldown_sec = max(
        0,
        _env_override_int("BTCTS_EXPLORATION_TEST_CRIT_COOLDOWN_SEC", crit_cooldown_sec),
    )
    recovery_start_after_sec = max(
        0,
        _env_override_int(
            "BTCTS_EXPLORATION_TEST_RECOVERY_START_AFTER_SEC",
            recovery_start_after_sec,
        ),
    )
    recovery_step_count = max(
        1,
        _env_override_int(
            "BTCTS_EXPLORATION_TEST_RECOVERY_STEP_COUNT",
            recovery_step_count,
        ),
    )
    recovery_step_interval_sec = max(
        1,
        _env_override_int(
            "BTCTS_EXPLORATION_TEST_RECOVERY_STEP_INTERVAL_SEC",
            recovery_step_interval_sec,
        ),
    )

    return ExplorationExchangeConfig(
        exchange=str(exchange),
        enabled=_as_bool(raw.get("enabled"), True),
        limits=ExplorationLimits(
            window_300s=max(1, _as_int(raw_limits.get("window_300s"), 500)),
            window_60s_ip=max(1, _as_int(raw_limits.get("window_60s_ip"), 500)),
        ),
        control=ExplorationControl(
            target_utilization=target_utilization,
            warn_utilization=warn_utilization,
            hard_cap_utilization=hard_cap_utilization,
            crit_floor_ratio=crit_floor_ratio,
            crit_trigger_429_count=crit_trigger_429_count,
            crit_trigger_window_sec=crit_trigger_window_sec,
            crit_cooldown_sec=crit_cooldown_sec,
            recovery_start_after_sec=recovery_start_after_sec,
            recovery_step_count=recovery_step_count,
            recovery_step_interval_sec=recovery_step_interval_sec,
            recovery_policy=str(raw_control.get("recovery_policy") or "time_based").strip() or "time_based",
            recovery_curve=recovery_curve,
            recovery_steps=recovery_steps,
        ),
        request_priority=request_priority,
        request_classes=request_classes,
    )


def load_exploration_runtime_config() -> ExplorationRuntimeConfig:
    try:
        raw = settings_svc.load_effective("exploration_runtime")
    except Exception:
        raw = {}

    raw_exchanges = raw.get("exchanges") if isinstance(raw, dict) else {}
    if not isinstance(raw_exchanges, dict):
        raw_exchanges = {}

    exchanges: Dict[str, ExplorationExchangeConfig] = {}
    for exchange, item in raw_exchanges.items():
        exchanges[str(exchange)] = _normalize_exchange(str(exchange), item)

    return ExplorationRuntimeConfig(exchanges=exchanges)