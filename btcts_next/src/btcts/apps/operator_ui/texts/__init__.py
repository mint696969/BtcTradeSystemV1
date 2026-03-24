# path: ./btcts_next/src/btcts/apps/operator_ui/texts/__init__.py
# desc: Aggregate split Operator UI text dictionaries into a single TEXTS mapping.

from __future__ import annotations

from btcts.apps.operator_ui.texts.ai_panels import AI_PANELS_TEXTS
from btcts.apps.operator_ui.texts.collector import COLLECTOR_TEXTS
from btcts.apps.operator_ui.texts.common import COMMON_TEXTS
from btcts.apps.operator_ui.texts.health import HEALTH_TEXTS
from btcts.apps.operator_ui.texts.research_replay import RESEARCH_REPLAY_TEXTS
from btcts.apps.operator_ui.texts.warroom import WARROOM_TEXTS


def _merge_lang(*parts: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    out = {"en": {}, "ja": {}}
    for lang in ("en", "ja"):
        merged: dict[str, str] = {}
        for part in parts:
            merged.update(part.get(lang, {}))
        out[lang] = merged
    return out


TEXTS = _merge_lang(
    COMMON_TEXTS,
    COLLECTOR_TEXTS,
    HEALTH_TEXTS,
    WARROOM_TEXTS,
    AI_PANELS_TEXTS,
    RESEARCH_REPLAY_TEXTS,
)