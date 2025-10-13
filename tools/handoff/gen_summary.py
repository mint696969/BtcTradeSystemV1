# path: tools/handoff/gen_summary.py
# desc: 有効設定の実効値サマリーをMarkdown化
from __future__ import annotations
import argparse, pathlib, datetime as dt

def yload(p: pathlib.Path) -> dict:
    if not p.exists(): return {}
    try:
        import yaml
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--v1", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--logs", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    root = pathlib.Path(a.v1) / "btc_trade_system"
    cfg  = root / "config"
    ui   = cfg / "ui"
    deflt= cfg / "ui_defaults"

    health = yload(ui / "health.yaml") or yload(deflt / "health.yaml")
    mon    = yload(ui / "monitoring.yaml") or yload(deflt / "monitoring.yaml")

    order = []
    if isinstance(health, dict):
        order = health.get("order") or []

    lines = []
    lines.append(f"# Handoff Summary ({dt.datetime.utcnow().isoformat()}Z)")
    lines.append("")
    lines.append("## 実効設定")
    lines.append("### カード順")
    lines.append("- " + ", ".join(order) if order else "- (未設定)")
    lines.append("")
    lines.append("### 閾値（health.age_sec / latency_ms）")
    try:
        hs = health.get("age_sec", {})
        lm = health.get("latency_ms", {})
        lines.append(f"- age_sec warn={hs.get('warn')} crit={hs.get('crit')}")
        lines.append(f"- latency_ms warn={lm.get('warn')} crit={lm.get('crit')}")
    except Exception:
        lines.append("- (health未設定)")

    lines.append("")
    lines.append("### SLO (monitoring.slo)")
    try:
        slo = mon.get("slo", {})
        for k,v in slo.items():
            lines.append(f"- {k}: {v}")
    except Exception:
        lines.append("- (monitoring未設定)")

    lines.append("")
    lines.append("## 実体ストレージ")
    lines.append(f"- DATA: {a.data}")
    lines.append(f"- LOGS: {a.logs}")
    pathlib.Path(a.out).write_text("\n".join(lines), encoding="utf-8")

if __name__ == "__main__":
    main()
