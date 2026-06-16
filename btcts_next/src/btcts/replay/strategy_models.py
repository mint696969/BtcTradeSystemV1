# path: ./btcts_next/src/btcts/replay/strategy_models.py
# desc: Data models for replay strategy sandbox trades and positions.

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class SandboxTrade:
    side: str
    entry_ts: str
    entry_price: float
    size: float
    reason: str
    exit_ts: Optional[str] = None
    exit_price: Optional[float] = None
    exit_reason: Optional[str] = None
    pnl: Optional[float] = None


@dataclass
class SandboxPosition:
    side: str
    entry_ts: str
    entry_price: float
    size: float
    reason: str


@dataclass
class SandboxResult:
    name: str
    trades: List[SandboxTrade] = field(default_factory=list)

    def closed_trades(self) -> List[SandboxTrade]:
        return [t for t in self.trades if t.exit_ts is not None and t.pnl is not None]