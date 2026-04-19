# path: ./archive/PREDICTION_SYSTEM_BLUEPRINT_BTC_BITFLYER_V0_1_2026-04-16.md
# desc: Archived note, specification, report, or reference document.

# Prediction System Blueprint BTC / bitFlyer v0.1

更新日: 2026-04-16
位置づけ: `./tmp/` 正式仕様書候補 / Prediction Process Entry 実装前提 blueprint
対象: BTC / bitFlyer 単一路線で開始する予測体系全体と、その first mainline になる Scenario Prediction Core

---

## 1. この仕様書の目的
本仕様書は、今後の roadmap 作業を
**PredictionSummary の局所表示拡張** ではなく、
**予測体系全体の構築**
として進めるための実装前提を固定する文書である。

ここでいう予測は 1 本の predictor ではない。

- 現在の地合い判断
- 近未来 / 少し先の地合い予測
- 値動き方向予測
- 転換点予測
- 戦術切替予測
- 建玉管理予測
- 執行タイミング予測
- 外れ後の分析 / 修整 / シミュレーション / calibration

を階層的に扱う **Prediction System** である。

本仕様書は、その全体像と、今まさに着手するべき
**Scenario Prediction Core**
を明確にする。

---

## 2. 一言での設計思想
この予測体系の最重要思想は次である。

**「予測の精度」だけではなく、
「仮説の更新速度」と「外れた後の立て直し力」を最強化する。**

したがって本体系は、

- 毎回必ず当てること
- 固定ルールで機械的に損切りすること
- 1 本の predictor で全てを決めること

を目標にしない。

代わりに次を重視する。

- 読めない時は参加しない
- 地合い仮説の健康状態を読み続ける
- 仮説が崩れたらすぐ別シナリオへ切り替える
- 外れた理由を残し、次の補正へ戻す
- GPT / AI は神託役ではなく、分析・補正・調整役として参加する

---

## 3. active scope
### 現在の active 実装対象
- market: `BTC_JPY`
- venue: `bitFlyer`
- active runtime truth: `market_state` と関連 shared bundles

### 今はまだ広げないもの
- multi-venue 本実装
- cross-market 本実装
- macro / 景気 / 外部ニュース本実装
- actor / pro strategy hypothesis 本実装
- online learning automation 本実装
- full automated execution 本実装

### 重要原則
今は **BTC / bitFlyer の単一路線で完成度を上げる**。
ただし将来増やせるように、shape は

- additive
- optional
- versioned
- disabled-by-default

で切る。

---

## 4. Prediction System は 1 つではない
本体系では「予測プロセスは 1 つではない」と明示する。

### P1. Scenario Prediction
最上位。
- 現在地合い
- 近未来地合い
- 少し先の地合い
- 仮説継続 / 弱化 / 破綻
- シナリオ切替候補

### P2. Direction / Turning Point Prediction
Scenario の下で行う。
- 値動き方向
- 継続 vs 反転
- 転換点リスク

### P3. Tactic Prediction
Scenario / Direction を戦術へ落とす。
- no-trade
- scalp
- reversal
- hold / trend-follow

### P4. Position Management Prediction
建玉状況・注文状況を踏まえる。
- hold 継続
- reduce
- exit
- reset / re-entry wait
- scenario switch after miss

### P5. Execution Timing Prediction
最下位の micro timing。
- entry timing
- exit timing
- urgency
- passive / aggressive hint

### current first mainline
このうち、今もっとも重要で先に切るべきものは
**P1 Scenario Prediction**
である。

---

## 5. 主目的 / 従目的
### 主目的
- 現在地合いの判断
- 近未来 + 少し先の地合い予測
- 仮説破綻検知
- シナリオ切替の判断材料生成

### 従目的
- 値動き方向予測
- 転換点予測
- 戦術切替の判断材料生成
- ホールド / 撤退 / 仕切り直し判断材料生成

### 将来必要だが first mainline ではないもの
- 建玉状況・注文状況を重く含む full position management
- execution micro-timing の本格化
- full automated order optimization

重要なのは、これらが不要なのではなく、
**最初に実装する最上位 core の主目的ではない**
という点である。

---

## 6. horizon 設計
### official horizon set
- `now`
- `5m`
- `10m`
- `30m`
- `60m`

### active first implementation
- `5m`
- `10m`
- `30m`

### delayed but planned
- `60m`

### optional future
- `1m`

### horizon の意味
#### `now`
- current regime / hypothesis health の現在値

#### `5m`
- 直近の継続 / 崩れ / 初動の読み
- 不参加 / スキャ / 早期 caution に効く

#### `10m`
- 短期の方向性と転換兆候の読み
- 反転仕掛けか継続かの判断に効く

#### `30m`
- 地合い仮説の中核 horizon
- hold / reset / switch の判断に強く効く

#### `60m`
- 大局確認用の longer outlook
- 最初から主軸にしないが、後から追加する価値は高い

### 原則
時間軸は増やすほど強くなるわけではない。
**意味のある horizon だけを持つ。**

---

## 7. Scenario Prediction Core の責務
### 目的
現在地合いと未来地合いの仮説を、evidence-first に組み立てる。

### Core が返すべきもの
- current regime state
- current hypothesis health
- horizon 別 outlook (`5m`, `10m`, `30m`, later `60m`)
- continuation vs reversal balance
- turning-point risk
- invalidation hints
- scenario switch hints
- confidence / caution / evidence trace

### Core がまだ返さないもの
- final action recommendation
- final order placement decision
- final execution timing decision
- prose-heavy AI wording

### 一言
Scenario Core は「当たる predictor」より、
**仮説の健康診断と更新基盤**
として設計する。

---

## 8. current regime state model
initial coarse state は次を採用する。

- `continuation`
- `reversal_watch`
- `transition`
- `unstable`
- `no_trade`

### state の意味
#### `continuation`
継続優位。押し戻しがあっても主仮説は維持される状態。

#### `reversal_watch`
継続より反転兆候が強まりつつある状態。まだ反転確定ではない。

#### `transition`
旧仮説が崩れ、新しい地合いへ移りつつある状態。

#### `unstable`
ノイズ・矛盾・流動性悪化・evidence 競合により、強い仮説を置きづらい状態。

#### `no_trade`
観測上、参加優位が弱いか、参加コストが高いと判断する状態。

### 原則
state は最初から細かくしすぎない。
粗い state の方が replay / calibration / 実運用で強い。

---

## 9. tactic model
Prediction System の future 下位層として、初期戦術セットは次を仮定する。

- `no_trade`
- `scalp`
- `reversal`
- `hold_trend`

### 位置づけ
これは current mainline の first output ではなく、
Scenario / Direction の下で later に formalize する layer である。

### 重要原則
- 読めない時の不参加は戦術の一種であり、精度向上の一部である
- 戦術は current regime state と horizon 別 outlook から落とす
- fixed stop rule を主役にしない

---

## 10. hypothesis invalidation / rewrite model
本体系では、損切りや撤退を「固定価格ルール」だけではなく
**仮説破綻ベース**
で扱う。

### 最小状態遷移
- `stable`
- `caution_increase`
- `degraded`
- `invalidated`
- `scenario_switch_required`

### 読み方
#### `stable`
主仮説は継続している。

#### `caution_increase`
主仮説は維持されるが、警戒度が上がっている。

#### `degraded`
主仮説の優位がかなり弱っている。hold は縮小方向で考える。

#### `invalidated`
主仮説は破綻した。継続前提の保持をやめる。

#### `scenario_switch_required`
別シナリオの方が優勢になった。再構築へ進む。

### 原則
- 価格逆行だけで破綻と決めない
- 地合い仮説の崩れ方を見る
- どの evidence で崩れたかを trace できるようにする

---

## 11. evidence family
Prediction System の上流は、現時点で少なくとも次の family に分ける。

### active first families
#### E1. market state anchor evidence
- `market_summary`
- current shared read model

#### E2. liquidity / board history evidence
- 板厚
- 流動性偏り
- 壁の継続 / 崩れ
- support / resistance の変化
- short history window の遷移

#### E3. regime / turning-point evidence
- transition sign
- continuity weakening
- reversal watch signal
- turning-point pressure

### placeholder family (future)
#### E4. technical / sentiment evidence
- disabled-by-default slot

#### E5. external market context evidence
- disabled-by-default slot

#### E6. actor / strategy hypothesis evidence
- disabled-by-default slot

#### E7. position / order context evidence
- first mainline では軽量 slot に留める
- full position management layer で本格利用する

### 原則
- current UI convenience payload を primary truth にしない
- raw input を無秩序に増やさない
- evidence family は shared owner で分離する

---

## 12. Prediction System contract skeleton
### top-level layers
- `PredictionSystemInput`
- `PredictionScenarioOutput`
- `PredictionDirectionOutput`
- `PredictionTacticHint`
- `PredictionPositionHint`
- `PredictionExecutionHint`
- `PredictionEvidenceBundle`
- `PredictionEvidenceTrace`
- `PredictionCalibrationHint`

### first implementation で実体化するもの
- `PredictionSystemInput`
- `PredictionScenarioOutput`
- `PredictionEvidenceBundle`
- `PredictionEvidenceTrace`
- `PredictionCalibrationHint`

### まだ slot / placeholder でよいもの
- `PredictionDirectionOutput`
- `PredictionTacticHint`
- `PredictionPositionHint`
- `PredictionExecutionHint`

### contract 原則
- additive-first
- versioned
- horizon-separated
- evidence-first
- read-only first
- replayable first

---

## 13. Scenario Core first output draft
### identity
- `prediction_type`
- `prediction_version`
- `source_kind`
- `market_uid`
- `event_ts`
- `freshness`
- `is_stale`

### current state
- `current_regime_state`
- `current_hypothesis_health`
- `current_confidence`
- `current_caution_level`

### horizon outlooks
- `outlook_5m`
- `outlook_10m`
- `outlook_30m`
- later `outlook_60m`

各 outlook は最低でも次を持てる shape を想定する。
- `regime_bias`
- `continuation_likelihood`
- `reversal_likelihood`
- `turning_point_risk`
- `confidence`
- `caution_level`

### invalidation / rewrite
- `invalidation_state`
- `invalidation_signals`
- `scenario_switch_hint`

### evidence / diagnostics
- `evidence`
- `evidence_trace`
- `diagnostics`

---

## 14. PredictionSummary の位置づけ
現在 repo にある `PredictionSummary` は重要だが、本仕様書では次のように読む。

### current reading
- `PredictionSummary` は **transitional read model**
- Scenario Core 本体そのものではない
- `market_summary` anchor の first shared prediction slice として価値がある

### 今後の関係
- `PredictionSummary` は Scenario Core first implementation の一部 evidence / lightweight output として再配置可能
- ただし full Prediction System 全体を `PredictionSummary` に押し込めない

### 原則
- 既存 repo truth は活かす
- しかし将来の設計主語は `PredictionSummary` ではなく `Prediction System` に置く

---

## 15. GPT / AI の役割
### 初期の役割
- 売買 owner ではない
- 分析 / replay 比較 / calibration 提案 / 外れ要因整理の owner

### 主な仕事
- どの evidence を過信したかの整理
- 外れた仮説の共通パターン抽出
- horizon ごとの弱点分析
- tactic switch 遅延の分析
- calibration 候補の提案
- replay / simulation の要約

### 原則
GPT / AI は最初から神託役にしない。
**修整速度を上げる役** として参加させる。

---

## 16. 評価 / replay / calibration
Prediction System の成否は accuracy だけで見ない。

### 評価対象
- 地合い分類の安定性
- horizon 別 outlook の整合性
- direction precision / confidence 別成績
- turning-point alert precision / recall
- hypothesis invalidation 検知の早さ
- scenario switch 成功率
- hold 継続判断の妥当性
- 外れ後の再追従の速さ

### calibration 対象
- confidence の過大 / 過小
- 特定地合いでの過信
- 特定 horizon での弱さ
- invalidation 遅延
- scenario switch 遅延

### 原則
**当てる力** だけでなく、
**外れた後にどれだけ速く立て直せるか**
を重要評価指標にする。

---

## 17. 実装順
### Step 1
`ai_operator` advisory boundary cleanup

### Step 2
Prediction System contract skeleton 新設

### Step 3
active 3 evidence family 分離
- `market_summary anchor`
- `liquidity / board history`
- `regime / turning-point`

### Step 4
Scenario Prediction Core skeleton 実装
- active horizon = `5m / 10m / 30m`

### Step 5
replay evaluation / calibration prep の入口作成

### Step 6
WarRoom / advisory consumer を Scenario Core output consumer に寄せる

### Step 7
Direction / Tactic / Position / Execution 下位層へ段階的に展開する

---

## 18. non-goals
この blueprint の first mainline に混ぜないもの。

- multi-venue 本実装
- external market full integration
- actor / pro strategy full engine
- online learning automation
- full position management automation
- full execution automation
- prose-heavy AI prediction UI

理由:
いまここで広げると失敗しやすいから。

---

## 19. done 定義
この blueprint に沿う near-term done は次。

1. Prediction System contract skeleton がある
2. Scenario Prediction Core skeleton がある
3. active 3 evidence family が shared owner として分離されている
4. `5m / 10m / 30m` horizon の scenario outlook を返せる
5. invalidation / rewrite の最小 state を返せる
6. WarRoom / advisory は output consumer に留まる
7. replay / calibration への入口がある

---

## 20. 一言
ここから先は、PredictionSummary をどこへ表示するかを延々と広げる段ではない。
**BTC / bitFlyer 単一路線で、地合いを含むシナリオ予測を中核にした Prediction System を切り、その上に方向・転換点・戦術・建玉管理・執行予測を積み上げていく段**
として読むのが正しい。
