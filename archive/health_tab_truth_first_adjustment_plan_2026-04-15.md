# path: ./archive/health_tab_truth_first_adjustment_plan_2026-04-15.md
# desc: Archived note, specification, report, or reference document.

# Health tab truth-first adjustment plan

更新日: 2026-04-15
位置づけ: `./tmp/` 成果物 / Health タブ表示是正の独立タスク方針メモ

---

## 1. タスクの目的
Health タブを、
**監視の定規として信用できる truth-first 表示**
へ寄せる。

ここでいう truth-first とは、
- 事実時系列は事実時系列として表示する
- current overlay は current overlay と明示する
- 擬似履歴を履歴グラフのように見せない
- 表示窓と入力窓の不整合をなくす

を意味する。

---

## 2. 現在確認できた問題
### A. 1時間表示なのに左側が欠ける
`health_data_service.py` の `build_recent_api_ws_series()` と continuity rail は
`audit.jsonl` の末尾 `max_lines=4000` だけを読む。

このため、collector が高頻度で長時間動いていると、
直近 4000 行が 1 時間未満しかカバーしないことがある。
その場合、1時間窓の前半 bucket は空のままになり、
画像のように左側が不自然に空白になる。

### B. Layer3 chart は履歴ではなく current overlay
`build_recent_layer3_series()` は `load_latest_market_state()` から現在値を 1 回読み、
全 bucket に同じ score を複写している。

したがってこれは「過去1時間の推移」ではなく、
**現在状態の横引き** である。

### C. rate overlay も履歴ではなく current overlay
`build_rate_limit_overlay()` も現在の rate state を全 bucket に複写している。

したがって utilization 系も「履歴グラフ」ではなく、
**current overlay** である。

---

## 3. truth-first 分類
### 事実時系列
- API / WS audit activity series
- continuity rail
- recent anomaly feed

### current overlay
- Layer3 state score line
- rate utilization / budget overlay

### 危険な擬似履歴
- current overlay を履歴グラフの形でそのまま line chart 表示している部分

---

## 4. 修正優先順位
### Priority 1
**表示窓と入力窓の整合を直す**
- 1時間表示なら、少なくとも1時間を十分カバーできる入力読み取りにする
- tail 4000 行固定で 1h を描く構造をやめるか、最低でも不足時の明示を入れる

### Priority 2
**current overlay を履歴と誤読させない**
- Layer3 line と rate overlay line の扱いを見直す
- line chart を維持するなら `current overlay` と明示する
- 可能なら current summary / badges / single-value strip へ寄せる

### Priority 3
**unfinished bucket の扱いを明確化する**
- 右端は current ではなく最後に確定した bucket であることを明示する
- in-progress bucket を表示しない仕様は維持してよいが、表現をより誤読しにくくする

---

## 5. 推奨実装方針
### Step 1
API / WS 系の 1h 窓は、tail 行数依存を弱める。
候補:
- 直近時刻から必要 window を満たすまで JSONL を遡る
- まず現実的には `max_lines` を range_key に応じて引き上げる
- 不足時は `coverage_warning` を返す

### Step 2
Layer3 / rate overlay は履歴線としてではなく、
current-state section へ寄せるか、少なくとも caption で overlay を明示する。

### Step 3
UI wording を修正する。
- 「1時間の推移」と誤読させる表現を避ける
- 「current overlay」「latest snapshot replicated」「unfinished bucket omitted」を明示する

---

## 6. done の定義
- 1h グラフの左側欠けが、入力不足によるものなら明示される
- 事実時系列と current overlay が見分けられる
- Health を監視の定規として読んだとき、どこが fact でどこが overlay か迷いにくい

---

## 7. 一言
このタスクは「見た目調整」ではない。
**Health を truth-first の監視ページへ戻すための是正タスク** として扱うべきである。
