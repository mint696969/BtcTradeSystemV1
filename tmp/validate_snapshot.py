# path: ./tmp/validate_snapshot.py
# desc: スナップショットMarkdown検証（DEBUG/BOOST対応）。--require-boost-in-tailでtail中のBOOST含有も確認。

import re, sys, argparse, pathlib, datetime as dt

SECTION_HEADERS = {
    "header": r"^#\s*BtcTradeSystemV1\s+Handover\s*\((?P<mode>[A-Z]+)\)\s*$",
    "ts":     r"^-+\s*ts:\s*(?P<ts>[\d\-:TZ]+)\s*$",
    "roots":  r"^##\s*Roots\s*$",
    "env":    r"^##\s*Env\s*$",
    "mods":   r"^##\s*Loaded modules \(top 50\)\s*$",
    "tail":   r"^##\s*Recent dev_audit tail \(last 20\)\s*$",
    "howto":  r"^##\s*How to reproduce \(PowerShell\)\s*$",
}

def parse(md: str):
    lines = md.splitlines()
    ok, info = True, {}

    # 1) header & mode
    m = re.match(SECTION_HEADERS["header"], lines[0].strip() if lines else "")
    info["mode"] = (m and m.group("mode")) or None
    ok_header = bool(m)

    # 2) ts line（2行目想定、フォールバック検索あり）
    ts_line = None
    for i in range(1, min(6, len(lines))):
        m2 = re.match(SECTION_HEADERS["ts"], lines[i].strip())
        if m2:
            ts_line = m2.group("ts"); break
    ok_ts = False
    if ts_line:
        try:
            dt.datetime.fromisoformat(ts_line.replace("Z","+00:00"))
            ok_ts = True
        except Exception:
            ok_ts = False
    info["ts"] = ts_line

    # 3) セクション見出しの存在
    def has(pattern):
        r = re.compile(pattern)
        return any(r.match(x.strip()) for x in lines)
    ok_roots = has(SECTION_HEADERS["roots"])
    ok_env   = has(SECTION_HEADERS["env"])
    ok_mods  = has(SECTION_HEADERS["mods"])
    ok_tail  = has(SECTION_HEADERS["tail"])
    ok_howto = has(SECTION_HEADERS["howto"])

    # 4) Roots の中身（data_root/logs_root の行がある）
    roots_block = []
    if ok_roots:
        idx = next(i for i,l in enumerate(lines) if re.match(SECTION_HEADERS["roots"], l.strip()))
        for j in range(idx+1, len(lines)):
            if lines[j].startswith("## "): break
            roots_block.append(lines[j].strip())
    ok_data = any(x.startswith("- data_root: ") for x in roots_block)
    ok_logs = any(x.startswith("- logs_root: ") for x in roots_block)

    # 5) Env の中身（BTC_TS_MODE / PYTHONPATH_contains_repo）
    env_block = []
    if ok_env:
        idx = next(i for i,l in enumerate(lines) if re.match(SECTION_HEADERS["env"], l.strip()))
        for j in range(idx+1, len(lines)):
            if lines[j].startswith("## "): break
            env_block.append(lines[j].strip())
    ok_env_keys = all(any(x.startswith(f"- {k}:") for x in env_block)
                      for k in ("BTC_TS_MODE","PYTHONPATH_contains_repo"))

    # 6) modules（少なくとも1行 “- btc_trade_system” を含む）
    mods_block = []
    if ok_mods:
        idx = next(i for i,l in enumerate(lines) if re.match(SECTION_HEADERS["mods"], l.strip()))
        for j in range(idx+1, len(lines)):
            if lines[j].startswith("## "): break
            mods_block.append(lines[j].strip())
    ok_modline = any(x.startswith("- btc_trade_system") for x in mods_block)

    # 7) tail は “- {json}” 形式が 0〜20 行
    tail_block = []
    if ok_tail:
        idx = next(i for i,l in enumerate(lines) if re.match(SECTION_HEADERS["tail"], l.strip()))
        for j in range(idx+1, len(lines)):
            if lines[j].startswith("## "): break
            tail_block.append(lines[j].rstrip())
    ok_tail_lines = 0 <= sum(1 for x in tail_block if x.startswith("- ")) <= 20

    results = {
        "mode_header" : ok_header,
        "ts_iso8601"  : ok_ts,
        "has_roots"   : ok_roots and ok_data and ok_logs,
        "has_env"     : ok_env and ok_env_keys,
        "has_modules" : ok_mods and ok_modline,
        "has_tail"    : ok_tail and ok_tail_lines,
        "has_howto"   : ok_howto,
    }
    # tail ブロックも返して追加検証に使えるようにする
    info["tail_block"] = tail_block
    return results, info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", "-f", default="./tmp/snap_debug.md")
    ap.add_argument("--expect-mode", default="DEBUG")
    ap.add_argument("--require-boost-in-tail", action="store_true")
    args = ap.parse_args()

    p = pathlib.Path(args.file)
    if not p.exists():
        print(f"[NG] snapshot file not found: {p}")
        sys.exit(2)

    md = p.read_text(encoding="utf-8", errors="ignore")
    results, info = parse(md)

    # 期待モード一致
    expect = (args.expect_mode or "").upper()
    header_mode = (info.get("mode") or "").upper()
    mode_ok = (header_mode == expect)

    # オプション: tail に BOOST を含む行が最低1つ
    require_boost = bool(args.require_boost_in_tail)
    tail_boost_ok = True
    if require_boost:
        tail = info.get("tail_block") or []
        tail_boost_ok = any(("BOOST" in line) for line in tail)

    print("=== Snapshot Validation ===")
    print(f"file          : {p}")
    print(f"header.mode   : {header_mode}  (expect={expect})  -> {'OK' if mode_ok else 'NG'}")
    for k, v in results.items():
        print(f"{k:13}: {'OK' if v else 'NG'}")
    if require_boost:
        print(f"tail_has_BOOST: {'OK' if tail_boost_ok else 'NG'}")

    ok_all = mode_ok and all(results.values()) and (tail_boost_ok if require_boost else True)
    print(f"\nSUMMARY: {'PASS' if ok_all else 'FAIL'}")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
