# path: ./tmp/test_modules_resolve.py
# desc: 実行時に import される snapshot_compose の実体と公開関数を確認
import inspect
from btc_trade_system.features.audit_dev import snapshot_compose as sc
names = dir(sc)
print("snapshot_compose.file =", getattr(sc, "__file__", "<none>"))
print("has ensure_errors_summary_in_text =", "ensure_errors_summary_in_text" in names)
print("has build_tail_block              =", "build_tail_block" in names)
if "build_tail_block" in names:
    head = (sc.build_tail_block(mode="DEBUG", last_n=20) or "").splitlines()[:1]
    print("tail_block_preview =", head[0] if head else "<empty>")
