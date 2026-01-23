# path: ./btcts_next/src/btcts/settings/svc.py
# desc: settings の公開口（svcのみ公開…という方針を維持しつつ、YAMLローダを“正準I/F”として一本化）

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from btcts.core import io, paths


# -----------------------------------------------------------------------------
# 重要な設計方針（固定）
# - schema: btcts_next/config/schema/*.yaml（リポに含める／配布物）
# - current: <BTC_TS_CONFIG_DIR or btcts_next/config/ui>/*.yaml（運用で変わる）
# - save は「schema既定値との差分のみを current に保存」
# - 差分が空なら current ファイルは削除（= default に戻す）
# - 余計なキーは保存前に除去（schema準拠）
# -----------------------------------------------------------------------------


@dataclass(frozen=True)
class SettingRef:
    name: str
    current_path: Path
    schema_path: Path


# logical name -> schema filename stem
# ここは「迷子防止の正準表」。追加する場合は必ずここに追記する。
SCHEMA_MAP: Dict[str, str] = {
    # settings
    "exchanges": "exchanges_def",
    "collector": "collector_def",
    "endpoints": "endpoints_def",
    "monitoring": "monitoring_def",
    "health": "health_def",
    "rate_control": "rate_control_def",
    # ui/dash
    "dash": "dash_def",
    "tabs": "tabs_def",
}


def resolve(name: str) -> SettingRef:
    n = (name or "").strip()
    if not n:
        raise ValueError("name is empty")
    schema_stem = SCHEMA_MAP.get(n)
    if not schema_stem:
        raise KeyError(f"unknown setting name: {n}")
    return SettingRef(
        name=n,
        current_path=paths.ui_yaml_path(n),
        schema_path=paths.schema_yaml_path(schema_stem),
    )


def _read_yaml_allow_header(path: Path) -> Dict[str, Any]:
    """先頭が '# path:' '# desc:' の2行でも確実に読める YAML 読み取り。"""
    if not path.exists():
        return {}

    # まずは既存 io.read_yaml を試す（通るならそれでOK）
    try:
        obj = io.read_yaml(path, default={}) or {}
        return obj if isinstance(obj, dict) else {}
    except Exception:
        pass

    # フォールバック：先頭コメント行を除去して safe_load
    try:
        import yaml  # type: ignore
    except Exception:
        return {}

    try:
        txt = path.read_text(encoding="utf-8")
        lines = txt.splitlines()
        # '# path:' '# desc:' を想定して最大2行スキップ
        while lines and lines[0].lstrip().startswith("#"):
            lines.pop(0)
            if len(lines) < 1:
                break
            # 最大2行で止めたいので、2行目まで見たら抜ける
            if len(lines) >= 0 and (len(txt.splitlines()) - len(lines)) >= 2:
                break
        body = "\n".join(lines).strip()
        if not body:
            return {}
        obj = yaml.safe_load(body)  # type: ignore
        return obj if isinstance(obj, dict) else {}
    except Exception:
        return {}

# -----------------------------------------------------------------------------
# schema helpers
# -----------------------------------------------------------------------------


def _schema_defaults(schema: Any) -> Dict[str, Any]:
    """schema から既定値 dict を抽出する。

    対応形（柔軟に吸収）：
    - {defaults: {...}}
    - {default: {...}}

    ※ 将来スキーマが拡張されてもここで吸収する。
    """
    if not isinstance(schema, dict):
        return {}
    d = schema.get("defaults")
    if isinstance(d, dict):
        return d
    d = schema.get("default")
    if isinstance(d, dict):
        return d
    return {}


def _schema_allowed_keys(schema: Any) -> Optional[set]:
    """schema から許可キー集合を抽出する（抽出不能なら None）。"""
    if not isinstance(schema, dict):
        return None
    # 1) 明示：keys: [..]
    keys = schema.get("keys")
    if isinstance(keys, (list, tuple)):
        return {str(x) for x in keys}

    # 2) fields: {k: {...}}
    fields = schema.get("fields")
    if isinstance(fields, dict):
        return {str(k) for k in fields.keys()}

    # 3) defaults から推定
    defaults = _schema_defaults(schema)
    if defaults:
        return {str(k) for k in defaults.keys()}

    return None


def _filter_to_schema(obj: Any, allowed: Optional[set]) -> Any:
    """余計なキーを除去（allowed が None なら何もしない）。"""
    if allowed is None:
        return obj
    if not isinstance(obj, dict):
        return obj
    return {k: obj[k] for k in obj.keys() if k in allowed}


# -----------------------------------------------------------------------------
# merge / diff
# -----------------------------------------------------------------------------


def _deep_merge(base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
    """dict の深いマージ（overlay 優先）。"""
    out: Dict[str, Any] = dict(base)
    for k, v in overlay.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)  # type: ignore[arg-type]
        else:
            out[k] = v
    return out


def _deep_diff(current: Dict[str, Any], defaults: Dict[str, Any]) -> Dict[str, Any]:
    """defaults と異なる部分のみを抽出する（dictのみ対応）。"""
    diff: Dict[str, Any] = {}
    for k, v in current.items():
        if k not in defaults:
            diff[k] = v
            continue
        dv = defaults.get(k)
        if isinstance(v, dict) and isinstance(dv, dict):
            sub = _deep_diff(v, dv)
            if sub:
                diff[k] = sub
        else:
            if v != dv:
                diff[k] = v
    return diff


def _header_lines(ref: SettingRef) -> str:
    # 物理パスは環境により変わるため、論理パスで固定する。
    return (
        f"# path: btcts://config/ui/{ref.name}.yaml\n"
        f"# desc: current override for '{ref.name}' (diff only)\n"
    )


# -----------------------------------------------------------------------------
# public API
# -----------------------------------------------------------------------------


def load_effective(name: str) -> Dict[str, Any]:
    """schema defaults + current diff を合成した実効値を返す。"""
    ref = resolve(name)
    schema = io.read_yaml(ref.schema_path, default={}) or {}
    defaults = _schema_defaults(schema)
    allowed = _schema_allowed_keys(schema)

    cur = _read_yaml_allow_header(ref.current_path) or {}
    # current 先頭のコメント行は safe_load では無視される想定

    cur = _filter_to_schema(cur, allowed)
    defaults = _filter_to_schema(defaults, allowed)

    if not isinstance(defaults, dict):
        defaults = {}
    if not isinstance(cur, dict):
        cur = {}

    return _deep_merge(defaults, cur)


def save_yaml(name: str, obj: Dict[str, Any]) -> Tuple[Path, bool]:
    """実効値 obj を受け取り、schema defaults との差分のみを current に保存する。

    戻り値: (current_path, saved)
    - saved=True: ファイルを書いた
    - saved=False: 差分ゼロのため削除した（= default に戻した）
    """
    ref = resolve(name)
    schema = io.read_yaml(ref.schema_path, default={}) or {}
    defaults = _schema_defaults(schema)
    allowed = _schema_allowed_keys(schema)

    if not isinstance(obj, dict):
        raise TypeError("obj must be dict")

    obj_f = _filter_to_schema(obj, allowed)
    defaults_f = _filter_to_schema(defaults, allowed) if isinstance(defaults, dict) else {}

    diff = _deep_diff(obj_f, defaults_f)

    if not diff:
        # default に戻す（current を消す）
        ref.current_path.unlink(missing_ok=True)
        return ref.current_path, False

    # 差分のみ保存（ヘッダを付与してから YAML 本文）
    # YAML dump は io.write_yaml を使うが、ヘッダを付けるため text を合成して atomic write。
    body = _yaml_dump(diff)
    text = _header_lines(ref) + body
    io.atomic_write_text(ref.current_path, text)
    return ref.current_path, True


def reset_to_default(name: str) -> Path:
    """current を削除し default に戻す。"""
    ref = resolve(name)
    ref.current_path.unlink(missing_ok=True)
    return ref.current_path


def get_paths(name: str) -> Dict[str, str]:
    """表示/監査用にパス情報を返す。"""
    ref = resolve(name)
    return {
        "name": ref.name,
        "current": str(ref.current_path),
        "schema": str(ref.schema_path),
    }


# -----------------------------------------------------------------------------
# yaml dump (header付き保存用)
# -----------------------------------------------------------------------------


def _yaml_dump(obj: Any) -> str:
    """YAML本文を文字列化（末尾改行あり）。"""
    # core/io.py の write_yaml はファイル書き込み前提なので、ここで dump だけ行う。
    try:
        import yaml  # type: ignore
    except Exception as e:
        raise RuntimeError("PyYAML is required") from e

    text = yaml.safe_dump(obj, allow_unicode=True, sort_keys=False)  # type: ignore
    if not text.endswith("\n"):
        text += "\n"
    return text

def exchanges_ready() -> tuple[bool, list[str], dict]:
    """
    Collector Start 可否判定（仕様書: ready/reasons）。

    戻り:
      - ready: Start可能か
      - reasons: Start不可の理由（ユーザー向け文字列）
      - details: 取引所ごとの判定詳細（UI表示用）

    判定方針（Collector範囲で安全側・最小）:
      - exchanges.yaml は schema どおり {exchanges:{...}} を正とする（誤形式は通さない）
      - enabled=true の取引所が 1つ以上あること
      - enabled 取引所に rate.max_rps > 0 があること（現状schemaの正準）
      - public収集では secrets は必須にしない（private機能は将来拡張で判定追加）
    """
    reasons: list[str] = []
    details: dict = {}

    # 1) exchanges の実効値を取得
    try:
        cfg = load_effective("exchanges")  # schema + current の実効値
    except Exception as e:
        return False, [f"exchanges 設定の読み込みに失敗: {e}"], {}

    if not isinstance(cfg, dict):
        return False, ["exchanges 設定が不正（dict ではありません）"], {}

    ex_map = cfg.get("exchanges")
    if not isinstance(ex_map, dict):
        return False, ["exchanges 設定が不正（'exchanges' が未設定/不正）"], {}

    startable_ids: list[str] = []

    for ex_id, ex in ex_map.items():
        if not isinstance(ex, dict):
            details[str(ex_id)] = {"ready": False, "reasons": ["設定が不正（dict ではありません）"]}
            continue

        enabled = bool(ex.get("enabled", False))
        if not enabled:
            details[ex_id] = {"ready": False, "reasons": ["disabled（enabled=false）"]}
            continue

        ex_reasons: list[str] = []

        rate = ex.get("rate") if isinstance(ex.get("rate"), dict) else {}
        max_rps = rate.get("max_rps")

        if not isinstance(max_rps, (int, float)) or float(max_rps) <= 0:
            ex_reasons.append("rate.max_rps が未設定/不正（> 0 が必須）")

        ex_ready = len(ex_reasons) == 0
        details[ex_id] = {"ready": ex_ready, "reasons": ex_reasons}

        if ex_ready:
            startable_ids.append(ex_id)

    if not ex_map:
        reasons.append("exchanges が未設定（取引所が1件もありません）")
    if not startable_ids:
        reasons.append("Start可能な取引所がありません（enabled / rate.max_rps を確認してください）")

    ready = len(reasons) == 0
    return ready, reasons, details
