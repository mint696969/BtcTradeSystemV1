# path: ./btcts_next/src/btcts/autotrade/risk/models.py
# desc: AutoTrade risk gate result models.

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Tuple


@dataclass(frozen=True)
class RiskGateResult:
    allowed: bool
    executable: bool
    blocked_by: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
