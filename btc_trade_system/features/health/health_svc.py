# path: ./btc_trade_system/features/health/health_svc.py
# desc: collector の status.json を読み、OK/WARN/CRIT を判定して UI/通知向けサマリを返す共通サービス。

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone, timedelta  # ← 追加

from btc_trade_system.features.settings import settings_svc as _SET
from btc_trade_system.features.health.health_order import load_order as _load_order

DEFAULT_WARN = 3.0
DEFAULT_CRIT = 10.0

@dataclass
class ItemView:
    exchange: str
    topic: str
    last_ok: Optional[str]
    age_sec: float
    cause: Optional[str]
    retries: int
    notes: Optional[str]
    level: str  # "OK" | "WARN" | "CRIT"

@dataclass
class HealthSummary:
    updated_at: Optional[str]
    items: List[ItemView]
    counts: Dict[str, int]  # {'OK': n1, 'WARN': n2, 'CRIT': n3}

# == パス解決 ==

def _data_dir() -> Path:
    p = os.environ.get("BTC_TS_DATA_DIR") or os.environ.get("DATA")
    if p:
        return Path(p)
    # 開発フォールバック：リポ直下 data/
    return Path(__file__).resolve().parents[3] / "data"

def _status_path() -> Path:
    return _data_dir() / "collector" / "status.json"

def _history_path() -> Path:
    """
    collector_status が書き出す health_history.jsonl のパスを返す。
    """
    return _data_dir() / "collector" / "health_history.jsonl"

# == 設定読取り ==
# 既存の _load_thresholds() を丸ごと置換
def _load_thresholds() -> Tuple[float, float, List[str], bool]:
    """
    (warn, crit, order, enable_rate_soft_warn) を返す。
    - warn/crit は settings_svc.load_yaml("monitoring") の後勝ちマージ結果から取得
    - order は health_order.load_order() に委譲
    - enable_rate_soft_warn は thresholds.rate.enable_soft_warn (bool) から取得
    """
    mon = _SET.load_yaml("monitoring") or {}

    # 期待パス: thresholds.default.age_sec.{warn, crit}
    thr = (((mon.get("thresholds") or {}).get("default") or {}).get("age_sec") or {})
    warn = float(thr.get("warn", DEFAULT_WARN))
    crit = float(thr.get("crit", DEFAULT_CRIT))

    # rate 系の注意喚起（soft_limit）を出すかどうか
    rate_thr = ((mon.get("thresholds") or {}).get("rate") or {})
    enable_rate_soft_warn = bool(rate_thr.get("enable_soft_warn", True))

    try:
        order = list(_load_order())
    except Exception:
        order = []

    return warn, crit, order, enable_rate_soft_warn

def _judge_level(age_sec: float, warn: float, crit: float) -> str:
    if age_sec >= crit:
        return "CRIT"
    if age_sec >= warn:
        return "WARN"
    return "OK"

def _build_rate_items(raw_status: dict, enable_soft_warn: bool) -> List[ItemView]:
    """
    status.json の 'rate' セクションから rate_limit 由来の健全性情報を組み立てる。

    - hard_limit が True の場合: level=CRIT, cause='rate_hard'（常に有効）
    - soft_limit が True の場合:
        * enable_soft_warn=True  のとき: level=WARN, cause='rate_soft'
        * enable_soft_warn=False のとき: アイテムを作らない
    - 両方 False の場合: その exchange については rate アイテムを作らない
    """
    items: List[ItemView] = []
    rate = raw_status.get("rate") or {}
    if not isinstance(rate, dict):
        return items

    for ex, info in rate.items():
        if not isinstance(info, dict):
            continue
        hard = bool(info.get("hard_limit"))
        soft = bool(info.get("soft_limit"))
        if not (hard or soft):
            # レート的には特に問題なし
            continue

        # 詳細は notes に軽く載せておく（tokens / penalty 等）
        tokens = info.get("tokens")
        penalty = info.get("penalty")
        notes = f"tokens={tokens}, penalty={penalty}"

        if hard:
            # 429 / Retry-After 由来のペナルティは常に CRIT として扱う
            level = "CRIT"
            cause = "rate_hard"
        elif soft and enable_soft_warn:
            # レート制御中の注意喚起（ON/OFF は設定で制御）
            level = "WARN"
            cause = "rate_soft"
        else:
            # soft_limit だが soft_warn を無効化している場合など
            continue

        items.append(ItemView(
            exchange=str(ex),
            topic="rate",
            last_ok=None,
            age_sec=0.0,  # rate 由来なので age_sec は 0 として扱う
            cause=cause,
            retries=0,
            notes=notes,
            level=level,
        ))

    return items

# == 健全性判定（再利用向け） ==

def eval_with_thresholds(snapshot: dict, thresholds: Tuple[float, float]) -> dict:
    """
    与えられた snapshot(dict) に warn/crit を適用し、各要素へ level を付与して返す。
    thresholds = (warn, crit)
    戻り値: {"items": [...], "counts": {...}}
    """
    warn, crit = thresholds
    items = []
    counts = {"OK": 0, "WARN": 0, "CRIT": 0}

    for it in snapshot.get("items", []):
        age = float(it.get("age_sec", 0.0))
        level = _judge_level(age, warn, crit)
        it["level"] = level
        items.append(it)
        counts[level] = counts.get(level, 0) + 1

    return {"items": items, "counts": counts, "updated_at": snapshot.get("updated_at")}

def read_health_history_window(window_sec: int) -> List[dict]:
    """
    collector/health_history.jsonl から、直近 window_sec 秒ぶんのスナップショットを読み出す。

    戻り値は、
      [{"ts": "...", "items": [...], "rate": {...}}, ...] の昇順（古い→新しい）。
    ここでは level 判定は行わず、“status.json 相当の生データ列” を返す。
    UI 側で read_health() と同じロジックを適用してタイムライン描画に利用する前提。
    """
    if window_sec <= 0:
        return []

    path = _history_path()
    if not path.exists():
        return []

    # cutoff を ISO8601Z 文字列で求めておき、辞書順比較でフィルタする。
    now_utc = datetime.now(timezone.utc)
    cutoff = now_utc - timedelta(seconds=window_sec)
    cutoff_iso = cutoff.replace(microsecond=0).isoformat().replace("+00:00", "Z")

    rows: List[dict] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    obj = json.loads(ln)
                except Exception:
                    # 壊れた行はスキップ
                    continue
                ts = obj.get("ts")
                if not isinstance(ts, str):
                    continue
                # history 側も iso_now() 互換の ISO8601Z 形式なので、文字列比較で十分
                if ts < cutoff_iso:
                    continue
                rows.append(obj)
    except Exception:
        # 読み取り失敗時は空リストを返す（UI 側で「履歴なし」として扱う）
        return []

    # 念のため ts 昇順でソートして返す
    rows.sort(key=lambda r: r.get("ts") or "")
    return rows

def _build_rate_state_from_row(raw_status: dict, enable_soft_warn: bool) -> Dict[str, str]:
    """
    1スナップショット分の 'rate' セクションから、
    取引所ごとの rate 状態（none/soft/hard）を求める。

    - hard_limit=True                  -> "hard"
    - soft_limit=True & enable_soft_warn=True -> "soft"
    - それ以外                         -> "none"
    """
    state: Dict[str, str] = {}
    rate = raw_status.get("rate") or {}
    if not isinstance(rate, dict):
        return state

    for ex, info in rate.items():
        if not isinstance(info, dict):
            continue
        hard = bool(info.get("hard_limit"))
        soft = bool(info.get("soft_limit"))
        if hard:
            state[str(ex)] = "hard"
        elif soft and enable_soft_warn:
            state[str(ex)] = "soft"
        # それ以外は "none" 扱い（辞書に登録しない）

    return state


def read_health_timeline(window_sec: int) -> Dict[str, List[Dict[str, Any]]]:
    """
    health_history.jsonl から直近 window_sec 秒ぶんの履歴を読み、
    UI がタイムライン描画にそのまま使える形へ整形して返す。

    戻り値の構造:
        {
          "bitflyer/board": [
             {"ts": "...", "exchange": "bitflyer", "topic": "board",
              "level": "OK", "age_sec": 1.0, "rate": "none|soft|hard"},
             ...
          ],
          "binance/rate": [...],
          ...
        }

    * level は warn/crit しきい値に従って算出
    * rate は同一スナップショット内の 'rate' セクションから exchange 単位で決定
    """
    if window_sec <= 0:
        return {}

    # 履歴（生スナップショット列）を取得
    history_rows = read_health_history_window(window_sec)
    if not history_rows:
        return {}

    warn, crit, _order, enable_rate_soft_warn = _load_thresholds()

    timeline: Dict[str, List[Dict[str, Any]]] = {}

    for row in history_rows:
        ts = row.get("ts")
        if not isinstance(ts, str):
            continue

        rate_state = _build_rate_state_from_row(row, enable_rate_soft_warn)

        row_items = row.get("items") or []
        for it in row_items:
            if not isinstance(it, dict):
                continue
            ex = str(it.get("exchange"))
            topic = str(it.get("topic"))
            if not ex or not topic:
                continue

            age = float(it.get("age_sec", 0.0))
            level = _judge_level(age, warn, crit)
            key = f"{ex}/{topic}"

            entry: Dict[str, Any] = {
                "ts": ts,
                "exchange": ex,
                "topic": topic,
                "level": level,                    # "OK" | "WARN" | "CRIT"
                "age_sec": age,
                "rate": rate_state.get(ex, "none") # "none" | "soft" | "hard"
            }
            timeline.setdefault(key, []).append(entry)

    return timeline

# == パブリックI/F ==

def read_health() -> HealthSummary:
    """
    collector/status.json を読み、OK/WARN/CRIT を付けた一覧と件数を返す。
    UI/ヘッダー/通知から共通利用することを想定。
    """
    p = _status_path()
    if not p.exists():
        return HealthSummary(updated_at=None, items=[], counts={"OK": 0, "WARN": 0, "CRIT": 0})

    raw = json.loads(p.read_text(encoding="utf-8-sig"))
    warn, crit, order, enable_rate_soft_warn = _load_thresholds()

    items: List[ItemView] = []
    # 1) collector の items セクション（従来どおり age_sec ベースの評価）
    raw_items = raw.get("items") or []
    for it in raw_items:
        age = float(it.get("age_sec", 0.0))
        items.append(ItemView(
            exchange=str(it.get("exchange")),
            topic=str(it.get("topic")),
            last_ok=it.get("last_ok"),
            age_sec=age,
            cause=it.get("cause"),
            retries=int(it.get("retries", 0)),
            notes=it.get("notes"),
            level=_judge_level(age, warn, crit),
        ))

    # 2) rate セクション由来のアイテムを追加（soft/hard limit）
    rate_items = _build_rate_items(raw, enable_rate_soft_warn)
    items.extend(rate_items)

    # 並び順：設定 order > exchange/topic
    def _key(iv: ItemView):
        k = f"{iv.exchange}/{iv.topic}"
        return (0, order.index(k)) if (order and k in order) else (1, iv.exchange, iv.topic)

    items.sort(key=_key)

    counts = {"OK": 0, "WARN": 0, "CRIT": 0}
    for iv in items:
        counts[iv.level] = counts.get(iv.level, 0) + 1

    return HealthSummary(
        updated_at=raw.get("updated_at"),
        items=items,
        counts=counts,
    )

# --- compat shim for legacy imports -----------------------------------------
def evaluate(snapshot, thresholds):
    """
    互換I/F: 旧UIが import していた evaluate を提供する。
    実体は eval_with_thresholds のエイリアス。
    """
    return eval_with_thresholds(snapshot, thresholds)
