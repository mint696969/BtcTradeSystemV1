# path: ./tools/test_providers_health.py
# desc: Provider(bitflyer) の最小スモーク（fetch_board / fetch_executions が HttpResult を返し、payload の形を確認）

from _btcts_bootstrap import ensure_btcts_on_syspath

ensure_btcts_on_syspath()

from btcts.collector.providers import bitflyer as bf


def main() -> int:
    print("[TEST] bitflyer board/executions")

    board = bf.fetch_board(product_code="BTC_JPY")
    execs = bf.fetch_executions(product_code="BTC_JPY", count=5)

    print("[OK] fetch_board -> HttpResult")
    print("[OK] fetch_executions -> HttpResult")
    print("  board.ok =", board.ok)
    print("  board.status_code =", board.status_code)
    print("  executions.ok =", execs.ok)
    print("  executions.status_code =", execs.status_code)

    assert board.ok, f"board not ok: status={board.status_code} error={board.error}"
    assert execs.ok, f"execs not ok: status={execs.status_code} error={execs.error}"

    b = board.payload or {}
    e = execs.payload or {}

    assert isinstance(b, dict), f"board.payload must be dict, got {type(b)}"
    assert isinstance(e, dict), f"execs.payload must be dict, got {type(e)}"

    items = e.get("items", [])
    assert isinstance(items, list), f"execs.payload['items'] must be list, got {type(items)}"

    # 典型キーが存在するか（API差分に強い緩めの条件）
    assert ("mid_price" in b) or ("bids" in b) or ("asks" in b), f"unexpected board keys: {list(b.keys())[:20]}"

    print(f"  executions.items len = {len(items)}")
    print("DONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
