# path: ./tmp/audit_smoke.py
# desc: 監査ゲートの出力差を簡易確認（安全・無副作用）

import os, time
from btc_trade_system.common import audit

def one_round(tag: str):
    audit.audit_ok(f"smoke.{tag}.start", feature="audit", payload={"msg":"hello"})
    audit.audit_warn("smoke.retry", feature="collector", payload={"cause":"RATE_LIMIT"}, retries=2)
    audit.audit_err("smoke.err.demo", feature="collector", payload={"code":504, "endpoint":"/api"})
    audit.audit_ok(f"smoke.{tag}.stop", feature="audit")

print("writing...")
for m in ["PROD","DEBUG","DIAG"]:
    os.environ["BTC_TS_MODE"] = m
    one_round(m)
    time.sleep(0.05)
print("done.")
