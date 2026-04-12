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

from .health_digest import HealthDigest, HealthDigestBuildInput, build_health_digest
from .market_summary import MarketSummary, MarketSummaryBuildInput, build_market_summary

__all__ = [
    "HealthDigest",
    "HealthDigestBuildInput",
    "build_health_digest",
    "MarketSummary",
    "MarketSummaryBuildInput",
    "build_market_summary",
]