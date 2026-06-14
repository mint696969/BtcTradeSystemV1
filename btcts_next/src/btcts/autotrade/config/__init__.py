# path: ./btcts_next/src/btcts/autotrade/config/__init__.py
# desc: AutoTrade config package.

from __future__ import annotations

from .defaults import INITIAL_LOGIC_VERSION, INITIAL_PARAMETER_SET_ID, initial_parameter_set_v0_1, initial_registry
from .models import ParameterSet, ParameterSetRegistry, ParameterSetStatus

__all__ = [
    "INITIAL_LOGIC_VERSION",
    "INITIAL_PARAMETER_SET_ID",
    "ParameterSet",
    "ParameterSetRegistry",
    "ParameterSetStatus",
    "initial_parameter_set_v0_1",
    "initial_registry",
]
