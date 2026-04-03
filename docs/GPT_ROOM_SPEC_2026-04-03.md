# path: ./docs/GPT_ROOM_SPEC_2026-04-03.md
# desc: Specification document for gpt_room structure and operating rules.
# gpt_room 仕様書

更新日: 2026-04-03
対象: `C:\BtcTradeSystem\tmp\gpt_room`
目的: GPT が継続的に開発を再開・引継ぎできるようにするための記憶領域仕様を定義する。

---

## 1. 概要
`gpt_room` は GPT の記憶正本である。

ここは作業台ではない。
作業台は `tmp/` 全体であり、`gpt_room` は引継ぎ・判断・現在地・再開導線を保持するためだけに使う。

この仕様書の目的は、次の2点を固定することにある。
- 何を `gpt_room` に置いてよいか
- どのような構造で置くべきか

---

## 2. 基本原則
### 2.1 正本原則
- `gpt_room` は GPT の記憶正本である
- 会話は正本ではない
- GPT名・担当名・スレ名ベースの部屋を作らない
- 記憶は「誰が書いたか」ではなく「何の記憶か」で整理する

### 2.2 作業台分離原則
- `gpt_room` を一時作業場として使ってはならない
- 一時成果物・切り分け用ファイル・実験ファイルは `tmp/` 側へ置く
- `gpt_room` は再開と引継ぎに必要な情報だけに絞る

### 2.3 再開性優先
- 次の GPT が最短で現状把握できることを最優先とする
- root 直下は入口専用に保つ
- 現在・資料・過去を明確に分ける

---

## 3. 正規構造
`gpt_room` の正規構造は次の通り。

### 3.1 root 直下
番号付きの不変入口ファイルだけを置く。

- `01_GAME_STRATEGY_PHILOSOPHY.md`
- `02_START_HERE.md`
- `03_README.md`
- `04_ROOM_MAP.md`
- `05_PRINCIPLES.md`
- `06_WORKING_PROTOCOL.md`
- `07_RULES_OPERATIONS.md`
- `08_STATUS.md`
- `09_FOCUS.json`
- `10_DECISIONS.md`
- `11_STATE.json`

### 3.2 `memory/`
今の作業に直接効く現行記憶。

想定サブ構造:
- `memory/handoffs/`
- `memory/roadmaps/`
- `memory/notes/`
- `memory/risks/`
- `memory/worklog/`
- `memory/idea/`

### 3.3 `reference/`
記憶ではないが、必要時に参照価値のある資料。

想定サブ構造:
- `reference/runbook/`
- `reference/_generated/`
- 技術資料・導入資料

### 3.4 `history/`
役目を終えた過去資産。

想定サブ構造:
- `history/handoffs/`
- `history/roadmaps/`
- `history/notes/`
- `history/risks/`
- `history/worklog/`

---

## 4. 各層の責務
### 4.1 root 直下
root 直下は入口であり、倉庫ではない。

置いてよいもの:
- 哲学
- 原則
- 利用規約
- 作業プロトコル
- 現在地
- 判断
- 地図
- 内部状態

置いてはいけないもの:
- 日付付き単発メモ
- 技術資料
- 生成物
- パッチ案
- 一時調査メモ

### 4.2 memory
`memory/` は active memory である。

置くもの:
- 現行 handoff
- 現行 roadmap
- 現行 note / risk / worklog
- 今すぐではないが忘れたくない着想 (`idea/`)

### 4.3 reference
`reference/` は資料であり、現行記憶ではない。

置くもの:
- runbook
- GPT補助生成物
- 技術資料
- 導入資料

### 4.4 history
`history/` は完了したもの・古いが再参照価値のあるものを置く。

---

## 5. `memory/idea/` の仕様
`memory/idea/` は着想の一時バッファである。

用途:
- 今すぐ着手しないが忘れると困るアイデア
- 次章候補
- 後で roadmap 化したい改善案
- 後で risk / note 化したい気づき

禁止:
- 永久保管庫化
- 未整理メモの墓場化

運用:
- 節目ごとに `roadmaps / notes / risks / history / delete` のいずれかへ必ず仕分ける

---

## 6. 読書順仕様
次の GPT は root 直下の番号付きファイルを番号順に読むこと。

標準順序:
1. `01_GAME_STRATEGY_PHILOSOPHY.md`
2. `02_START_HERE.md`
3. `03_README.md`
4. `04_ROOM_MAP.md`
5. `05_PRINCIPLES.md`
6. `06_WORKING_PROTOCOL.md`
7. `07_RULES_OPERATIONS.md`
8. `08_STATUS.md`
9. `09_FOCUS.json`
10. `10_DECISIONS.md`
11. `11_STATE.json`

その後、必要に応じて `memory/`, `reference/`, `history/` を読む。

---

## 7. ライフサイクル仕様
### 新しく生まれた情報
- 現行作業に効く → `memory/`
- 資料として残す → `reference/`
- 役目を終えた → `history/`
- 着想段階 → `memory/idea/`

### handoff の扱い
- 現行スレの handoff は `memory/handoffs/`
- 次 GPT が再開し、もう active でないと確認できたら `history/handoffs/`

### roadmap の扱い
- 現行 roadmap は `memory/roadmaps/`
- 完了したら `history/roadmaps/`

---

## 8. 禁止事項
- `gpt_room` を一時作業場として使うこと
- root 直下へ日付付き単発ファイルを増やすこと
- GPT名・担当名・スレ名ベースのフォルダを作ること
- 既存カテゴリで足りるのに新カテゴリを増やすこと
- 現在・資料・過去の責務を混ぜること

---

## 9. 今回の運用到達点
2026-04-03 時点で、`gpt_room` は以下の方針で再編済みである。
- root 直下は番号付き不変入口に統一
- `memory / reference / history` の責務分離を完了
- `reference/_generated/` を GPT補助生成物の正規置き場に決定
- 次 GPT は「root 直下を番号順に読む」だけで初動できる状態にした

---

## 10. 一言でまとめると
`gpt_room` は GPT の記憶領域であり、
- root は入口
- `memory/` は現在
- `reference/` は資料
- `history/` は過去
として運用する。

この構造を守ること自体が、次 GPT への最大の引継ぎである。
