# path: ./btcts_next/src/btcts/apps/operator_ui/ai_runtime.py
# desc: Operator UI の AI 会話応答を local / external-http で切り替え、短期市場メモリを扱う実行層。

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Dict

from btcts.apps.operator_ui.ui_text import get_text


AI_EXTERNAL_ENABLED = os.getenv("BTCTS_AI_EXTERNAL_ENABLED", "0") == "1"
AI_EXTERNAL_URL = os.getenv("BTCTS_AI_EXTERNAL_URL", "").strip()
AI_EXTERNAL_TIMEOUT_SEC = float(os.getenv("BTCTS_AI_EXTERNAL_TIMEOUT_SEC", "8"))
AI_EXTERNAL_FALLBACK_TO_LOCAL = os.getenv("BTCTS_AI_EXTERNAL_FALLBACK_TO_LOCAL", "1") == "1"


def compose_effective_prompt(
    *,
    lang: str,
    prompt: str,
    intent: str,
    style: str,
) -> str:

    if lang == "ja":
        return f"[意図:{intent}] [スタイル:{style}] {prompt}".strip()

    return f"[intent:{intent}] [style:{style}] {prompt}".strip()

def summarize_memory_trend(lang: str, memory: list[Dict[str, float]]) -> str:

    if len(memory) < 2:
        return get_text(lang, "ai_memory_empty")

    latest = memory[0]
    prev = memory[1]

    spread_diff = latest["spread"] - prev["spread"]
    imbalance_diff = latest["imbalance"] - prev["imbalance"]
    delta_diff = latest["delta"] - prev["delta"]
    wall_ratio_diff = latest["wall_ratio"] - prev["wall_ratio"]

    score = 0

    if abs(spread_diff) < 200:
        score += 0
    elif spread_diff < 0:
        score += 1
    else:
        score -= 1

    if abs(delta_diff) > 0.15:
        score += 1 if delta_diff > 0 else -1

    if abs(imbalance_diff) > 0.08:
        score += 1 if imbalance_diff > 0 else -1

    if score >= 2:
        trend = get_text(lang, "ai_memory_trend_improving")
    elif score <= -2:
        trend = get_text(lang, "ai_memory_trend_worsening")
    else:
        trend = get_text(lang, "ai_memory_trend_stable")

    if lang == "ja":
        return (
            f"市場状態メモリ判定: {trend}。"
            f" スプレッド変化 {spread_diff:+.1f},"
            f" 板バランス変化 {imbalance_diff:+.3f},"
            f" 約定デルタ変化 {delta_diff:+.3f},"
            f" 壁比率変化 {wall_ratio_diff:+.3f}"
        )

    return (
        f"Market memory trend: {trend}. "
        f"Spread change {spread_diff:+.1f}, "
        f"Imbalance change {imbalance_diff:+.3f}, "
        f"Delta change {delta_diff:+.3f}, "
        f"Wall ratio change {wall_ratio_diff:+.3f}"
    )


def build_local_answer(lang: str, prompt: str, state: dict, memory: list[Dict[str, float]] | None = None) -> str:

    spread = state["spread"]
    imbalance = state["imbalance"]
    delta = state["delta"]
    wall_ratio = state["wall_ratio"]

    memory_comment = ""
    if memory:
        memory_comment = "\n\n" + summarize_memory_trend(lang, memory)

    if lang == "ja":

        if prompt == get_text(lang, "ai_conversation_q1"):
            return (
                f"現在の市場は、板バランス {imbalance:.3f}、約定デルタ {delta:.3f}、"
                f"スプレッド {spread:.1f} の状態です。"
                "板とフローの向きが一致しているかを見ながら継続性を判断する局面です。"
                f"{memory_comment}"
            )

        if prompt == get_text(lang, "ai_conversation_q2"):
            if imbalance < -0.2 and delta < 0:
                return (
                    "はい。板・約定ともに売り優勢で、ショート側の継続を警戒する局面です。"
                    f"{memory_comment}"
                )
            return (
                "現時点ではショート優勢は未確定です。板か約定のどちらかがまだ逆行しています。"
                f"{memory_comment}"
            )

        if prompt == get_text(lang, "ai_conversation_q3"):
            if wall_ratio < -0.2 and delta > 0:
                return (
                    "売り壁は見えている一方で買いフローが入っています。吸収の可能性があり、フェイク壁の疑いがあります。"
                    f"{memory_comment}"
                )
            if wall_ratio < -0.2 and delta < 0:
                return (
                    "売り壁と売りフローが一致しています。本物の壁として機能している可能性が高いです。"
                    f"{memory_comment}"
                )
            return (
                "現時点では壁の確度は中立です。継続観測が必要です。"
                f"{memory_comment}"
            )

        if prompt == get_text(lang, "ai_conversation_q4"):
            if abs(imbalance) > 0.2 and abs(delta) > 0.2:
                return (
                    "準備寄りです。板と約定の偏りが強く、ブレイク継続の可能性があります。"
                    f"{memory_comment}"
                )
            return (
                "待機寄りです。まだ確証が弱く、無理に追わない方が安全です。"
                f"{memory_comment}"
            )

        if prompt.strip():
            return (
                f"入力内容を受け取りました: 「{prompt}」。"
                f" 現在の市場は板バランス {imbalance:.3f}、約定デルタ {delta:.3f}、"
                f"スプレッド {spread:.1f}、壁比率 {wall_ratio:.3f} です。"
                " この質問に対しては、板とフローの一致度を優先して解釈するのが妥当です。"
                f"{memory_comment}"
            )

        return get_text(lang, "ai_conversation_placeholder")

    if prompt == get_text(lang, "ai_conversation_q1"):
        return (
            f"Current market state: orderbook imbalance {imbalance:.3f}, "
            f"trade delta {delta:.3f}, spread {spread:.1f}. "
            f"This is a continuation check phase.{memory_comment}"
        )

    if prompt == get_text(lang, "ai_conversation_q2"):
        if imbalance < -0.2 and delta < 0:
            return f"Yes. Both orderbook and trade flow support short continuation.{memory_comment}"
        return f"Not confirmed yet. One side is still offsetting the other.{memory_comment}"

    if prompt == get_text(lang, "ai_conversation_q3"):
        if wall_ratio < -0.2 and delta > 0:
            return f"Sell wall is visible, but buyers are absorbing it. It may be a fake wall.{memory_comment}"
        if wall_ratio < -0.2 and delta < 0:
            return f"Sell wall and sell flow agree. It is more likely a real wall.{memory_comment}"
        return f"Wall conviction is neutral for now.{memory_comment}"

    if prompt == get_text(lang, "ai_conversation_q4"):
        if abs(imbalance) > 0.2 and abs(delta) > 0.2:
            return f"Prepare for breakout. Bias and flow are both strong.{memory_comment}"
        return f"Wait for confirmation. Current edge is still weak.{memory_comment}"

    if prompt.strip():
        return (
            f"Received prompt: '{prompt}'. "
            f"Current state is imbalance {imbalance:.3f}, delta {delta:.3f}, "
            f"spread {spread:.1f}, wall ratio {wall_ratio:.3f}. "
            f"Interpretation should prioritize alignment between orderbook and trade flow.{memory_comment}"
        )

    return get_text(lang, "ai_conversation_placeholder")


def _external_payload(
    lang: str,
    prompt: str,
    state: Dict[str, float],
    memory: list[Dict[str, float]] | None = None,
) -> dict:
    return {
        "lang": lang,
        "prompt": prompt,
        "market_state": {
            "spread": state["spread"],
            "imbalance": state["imbalance"],
            "delta": state["delta"],
            "wall_ratio": state["wall_ratio"],
        },
        "market_memory": memory or [],
    }


def build_external_http_answer(
    lang: str,
    prompt: str,
    state: Dict[str, float],
    memory: list[Dict[str, float]] | None = None,
) -> str:

    if not AI_EXTERNAL_ENABLED:
        raise RuntimeError(get_text(lang, "ai_runtime_external_disabled"))

    if not AI_EXTERNAL_URL:
        raise RuntimeError(get_text(lang, "ai_runtime_external_url_missing"))

    payload = _external_payload(lang, prompt, state, memory)

    request = urllib.request.Request(
        AI_EXTERNAL_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=AI_EXTERNAL_TIMEOUT_SEC) as response:
            raw = response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"{get_text(lang, 'ai_runtime_external_http_error')}: {e.code} / {body}"
        ) from e
    except urllib.error.URLError as e:
        raise RuntimeError(
            f"{get_text(lang, 'ai_runtime_external_network_error')}: {e.reason}"
        ) from e
    except TimeoutError as e:
        raise RuntimeError(get_text(lang, "ai_runtime_external_timeout")) from e

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            f"{get_text(lang, 'ai_runtime_external_bad_response')}: {raw[:200]}"
        ) from e

    answer = parsed.get("answer")

    if not isinstance(answer, str) or not answer.strip():
        raise RuntimeError(get_text(lang, "ai_runtime_external_answer_missing"))

    return answer.strip()


def generate_answer(
    *,
    mode: str,
    lang: str,
    prompt: str,
    state: Dict[str, float],
    note: str = "",
    memory: list[Dict[str, float]] | None = None,
    intent: str = "",
    style: str = "",
) -> tuple[str, str]:

    runtime_source = "local"

    effective_prompt = compose_effective_prompt(
        lang=lang,
        prompt=prompt,
        intent=intent,
        style=style,
    )

    if mode == "external":
        try:
            answer = build_external_http_answer(lang, effective_prompt, state, memory)
            runtime_source = "external"
        except Exception as e:
            if AI_EXTERNAL_FALLBACK_TO_LOCAL:
                answer = (
                    f"{get_text(lang, 'ai_runtime_fallback_prefix')}: {e}\n\n"
                    f"{build_local_answer(lang, effective_prompt, state, memory)}"
                )
                runtime_source = "fallback-local"
            else:
                raise
    else:
        answer = build_local_answer(lang, effective_prompt, state, memory)

    if note.strip():
        answer = (
            f"{answer}\n\n"
            f"{get_text(lang, 'ai_conversation_note_prefix')}: {note.strip()}"
        )

    return answer, runtime_source


def supported_modes() -> list[str]:
    return ["local", "external"]


def default_mode() -> str:
    return "external"