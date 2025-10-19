# path: ./tmp/audit_smoke.py
# desc: 監査スモークテスト（err/transition/大きいpayloadを生成）— 実運転コードは触らない

import os, time
from btc_trade_system.common.audit import audit, audit_err, set_context

# ★ モードはここで指定（UI未連動のためテスト時だけ強制）
os.environ["BTC_TS_MODE"] = "DEBUG"  # DEBUG で出やすくする。終わったら外してOK

# トレース束ね（一連のイベントに同じIDを付与）
set_context(trace_id="SMOKE-TRACE-001", actor="tester", site="local", session="S-TEST", task="audit.smoke")

# 1) 失敗系（endpoint/code/elapsed_ms を fields 経由で出す）
audit_err(
    "smoke.err.demo",
    feature="collector",
    endpoint="/api",
    code=504,
    elapsed_ms=1234,
    cause="NET_BLOCK",
)

# 2) 遷移（to=WARN → should_emit許可）
audit(
    "collector.status.transition",
    feature="collector",
    level="INFO",
    payload={"hint": "simulated transition"},
    from_state="OK",
    to="WARN",
    cause="RATE_LIMIT",
)

# 3) 大きい payload（要約と _truncated を確認）
big_payload = {"k": "x" * (10 * 1024)}  # 10KB
audit(
    "smoke.payload.big",
    feature="audit",
    level="INFO",
    payload=big_payload,
)

print("done")
