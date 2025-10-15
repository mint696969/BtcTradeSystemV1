# path: ./tools/audit_smoke.py
# desc: 監査出力の動作確認（文脈セット→INFO/ERRORを1行ずつ記録）

import sys, pathlib, traceback
# リポジトリ直下（…/BtcTradeSystemV1）を sys.path 先頭に追加
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from btc_trade_system.common.audit import set_context, audit_ok, audit_err

def main():
    try:
        from btc_trade_system.common import paths
        from btc_trade_system.common.audit import set_context, audit_ok, audit_err

        # logs ディレクトリを確実に用意
        paths.ensure_dirs()
        log_path = paths.logs_dir() / "audit.jsonl"

        set_context(actor="mint777", site="main-pc", session="S-20251014",
                    task="audit.smoke", mode="PROD")
        audit_ok("smoke.start", feature="audit", payload={"msg": "hello"})
        audit_err("smoke.err.demo", feature="audit",
                  endpoint="/demo", code=418, latency_ms=123)

        print("WROTE:", str(log_path))
    except Exception:
        traceback.print_exc()
        raise

if __name__ == "__main__":
    main()
