# path: ./docs/architecture/LAYER_RESPONSIBILITY_RUNTIME_SPEC_2026-04-04.md
# desc: Runtime responsibility spec for the layered vNext architecture.
# BTC Trade System vNext レイヤ責務・実行配置仕様書

更新日: 2026-04-04
位置づけ: 現行実装ベースの再構成仕様書 / docs 再配置用ドラフト
対象: `btcts_next/src/btcts/`

---

## 1. この仕様書の目的
本仕様書は、現行 repository の実装状態を基準に、BTC Trade System vNext のレイヤ責務を整理し直したものである。

主目的は次の4つ。

1. L1 / L2 / L3 / L4 の責務を、実装と運用の両面から明確化する
2. 「何を元に、何を付与して、どこへ書くか」をレイヤ別に固定する
3. 現行実装が理想構造のどこまで到達しているかを明示する
4. docs 再配置時の新しい基準仕様書として使える形にする

本仕様書は、2026-04-04 時点の repository 実体に基づく。
会話上の期待ではなく、現行コード構造を優先する。

---

## 2. 結論の先取り
現行 vNext は、責務分離の方向としては次の形で整理されている。

```text
L1 取得・接続・生イベント捕捉
L2 事実の正規化・構造再構成・canonical 化
L3 市場意味の解釈
L4 consumer 向け共有モデル化
```

ただし、2026-04-04 時点の現行実装は次の状態である。

- L1/L2 の実運転主系は `collector_vnext/` にある
- L2 の正規 ownership は `ingestion/l2_canonical/` に分離済み
- L3 の正規 ownership は `processing/l3_market_semantics/` に分離済み
- L4 は思想・方針は確立済みだが、専用 package はまだ未展開
- 現行の実運転確認で白が付いているのは主に collector 側、つまり L1/L2 寄りの運転経路である

要するに、

- 構造分離は成立している
- L1/L2/L3 の ownership は概ね確定している
- L4 は次フェーズの設計対象である

---

## 3. レイヤ全体像

### 3.1 理想依存方向

```text
L1 Capture
  ↓
L2 Canonical / Structural Truth
  ↓
Features
  ↓
L3 Market Semantics
  ↓
L4 Consumer Models
  ↓
Consumers
```

補助系として、

- orchestration は「どう動かすか」を担当する
- platform は共通基盤を担当する
- market_engine/execution は L3 を利用して runtime / replay を動かす

という構造をとる。

### 3.2 一言まとめ

```text
L1 は取得。
L2 は事実の整形。
L3 は意味。
L4 は利用向けの共通モデル化。
```

---

## 4. レイヤ別の詳細仕様

# 4.1 L1 Capture

## 4.1.1 責務
L1 は、市場データを壊さず取得し続ける責務を持つ。

L1 の本質は「接続して受け取り続けること」である。
ここではまだ市場意味は作らない。

### L1 が担当するもの
- REST / WebSocket 接続
- subscribe / recv / retry / reconnect
- rate control 連携
- provider 差分吸収の入口
- raw payload の受領
- session / stream continuity の運転上の維持
- acquisition health の更新
- stop / restart に協調するための最低限の状態管理

### L1 が担当しないもの
- pressure / wall / absorption などの意味判断
- orderbook の意味的評価
- market regime
- UI summary
- consumer 専用整形

## 4.1.2 L1 は何を元に何を付与するか
### 入力
- 取引所 API/WS から来る生データ
- 接続設定
- symbol / exchange / channel 情報
- runtime session 情報

### 付与するもの
- 受信時刻
- provider 名
- transport 種別
- channel / endpoint 情報
- session_id / stream_session_id
- 生メッセージに対する最低限の envelope 情報

### 出力
- raw event
- lane state
- health / status 更新情報

## 4.1.3 L1 はどこに何を書くか
現行 collector_vnext 系では、L1 は主に以下へ書く。

### データ書き込み
- `data/collector_raw/.../*.jsonl`
  - 生イベントを raw record として保存

### 状態書き込み
- `state/unified_origin_status.json`
- `state/unified_executions_status.json`
- `state/unified_daemon_status.json`
- `state/unified_daemon_health.json`
- `state/unified_checkpoint.json` の一部更新

### 監査出力
- `audit.emit(...)` 経由の JSONL 監査ログ
- supervisor / daemon の状態遷移ログ

## 4.1.4 現行実装上の主な担当場所
2026-04-04 時点で L1 責務を強く持つのは主に以下。

- `btcts/collector_vnext/providers/bitflyer_rest.py`
- `btcts/collector_vnext/providers/bitflyer_ws.py`
- `btcts/collector_vnext/providers/bitflyer_ws_board.py`
- `btcts/collector_vnext/unified_ws_board_lane.py`
- `btcts/collector_vnext/unified_ws_executions_lane.py`
- `btcts/collector_vnext/rate_runtime.py`
- `btcts/collector_vnext/unified_daemon.py`
- `btcts/collector_vnext/unified_watchdog.py`

## 4.1.5 現在の構造上の注意
理想構造上は `ingestion/l1_capture/` を明示的に持つのが望ましいが、現時点では L1 の実動部分は `collector_vnext/` に置かれている。

つまり現状は、

- 理念上の L1 は定義済み
- 物理配置としては collector_vnext 側に実装が残っている

という状態である。

---

# 4.2 L2 Canonical

## 4.2.1 責務
L2 は、生データを「下流が安全に使える事実の形」にする責務を持つ。

L2 の本質は「意味を加えず、事実を構造化すること」である。

### L2 が担当するもの
- raw -> canonical transform
- event type 正規化
- sequence / event id / source id の付与
- snapshot / diff の構造的整合支援
- orderbook の構造再構成
- tradeflow の構造集約
- gap / resync のための structural support
- canonical record contract の維持

### L2 が担当しないもの
- buy pressure / sell pressure の判定
- wall が強い / 弱いの意味づけ
- absorption / sweep の意味イベント化
- trust / broken / provisional の意味判断
- UI や monitoring 向けの説明文生成

## 4.2.2 L2 は何を元に何を付与するか
### 入力
- L1 が受け取った raw payload
- provider / venue 差分の情報
- session / sequence 情報
- structural rule

### 付与するもの
- canonical schema に沿った field
- event_type
- source_event_id / source_sequence
- continuity 用の構造情報
- snapshot / diff を扱うための再構成前提情報
- trade aggregation の構造的単位

### 出力
- canonical orderbook event
- canonical trade event
- L2 structural state

## 4.2.3 L2 はどこに何を書くか
現行 collector_vnext 系の実運転では、L2 は主に以下へ書く。

### canonical データ
- `data/market_data/.../*.jsonl`
  - canonical 化済みの board snapshot / board diff / market trade

### state
- `state/unified_checkpoint.json`
- `state/unified_status.json`
- `state/unified_health.json`

注記:
`unified_status.json` や `unified_health.json` は厳密には L2 専用ではなく runtime summary も含むが、現実運用では L1/L2 の稼働状態を示す主要出力でもある。

## 4.2.4 現行実装上の正規 ownership
L2 の正規 ownership は以下。

- `btcts/ingestion/event_types.py`
- `btcts/ingestion/l2_canonical/orderbook/book_state.py`
- `btcts/ingestion/l2_canonical/orderbook/book_apply.py`
- `btcts/ingestion/l2_canonical/orderbook/book_rebuilder.py`
- `btcts/ingestion/l2_canonical/tradeflow/trade_aggregator.py`

## 4.2.5 現行実運転とのマッピング
現行の collector 実動系では、L2 相当の一部がまだ `collector_vnext/transforms/` と `collector_vnext/events.py` に存在する。

- `collector_vnext/transforms/raw_to_canonical.py`
- `collector_vnext/transforms/raw_to_canonical_trades.py`
- `collector_vnext/transforms/ws_board_to_canonical.py`
- `collector_vnext/transforms/ws_trade_to_canonical.py`

したがって、現状は次のように整理するのが正確である。

- L2 の conceptual / ownership は `ingestion/l2_canonical/`
- L2 の実運転導線には `collector_vnext/transforms/` がまだ存在する

これは責務の逆流ではなく、移行完了後の runtime 実装がまだ collector 側に残っている状態として扱う。

---

# 4.3 Features

## 4.3.1 責務
Features は、中立で再利用可能な計算結果を提供する。

まだ市場意味は定義しない。
ここで作るのは「観測量」であって「解釈」ではない。

### 例
- imbalance
- depth summary
- volume summary
- buy/sell volume
- trade delta
- orderbook feature vector

## 4.3.2 Features は何を元に何を付与するか
### 入力
- L2 canonical event
- L2 structural state

### 付与するもの
- 中立特徴量
- 再利用可能な数値集約
- まだ意味ラベルを持たない集計値

### 出力
- orderbook features
- tradeflow features

## 4.3.3 現行実装上の場所
- `btcts/processing/features/orderbook/book_features.py`
- `btcts/processing/features/tradeflow/trade_features.py`

## 4.3.4 どこに書くか
2026-04-04 時点では、Features 専用の永続出力先は強く固定されていない。
主な役割は「下流の L3 や consumer が参照する中間計算」である。

必要に応じて将来、shared な feature store へ出す可能性はあるが、現時点では package ownership の確立が先である。

---

# 4.4 L3 Market Semantics

## 4.4.1 責務
L3 は、市場状態に意味を与える唯一の正本層である。

ここで初めて、

- pressure
- wall semantics
- pull
- absorption
- sweep
- continuity semantics
- trust semantics
- boundary interpretation
- zone shaping

などを定義する。

### L3 が担当するもの
- 市場意味の解釈
- threshold / policy に基づく意味付け
- continuity / trust / boundary semantics
- orderbook / tradeflow / microstructure の解釈
- shared market meaning の owner

### L3 が担当しないもの
- UI wording
- Streamlit 向け表示形
- replay 専用表示モデル
- monitoring 通知 wording
- daemon / scheduler / watchdog logic

## 4.4.2 L3 は何を元に何を付与するか
### 入力
- L2 canonical event
- L2 structural state
- Features の中立量
- venue/profile policy

### 付与するもの
- semantic event
- market meaning label
- trust / continuity interpretation
- liquidity pressure / wall / sweep / absorption などの意味情報
- zone / regime 的な共有意味

### 出力
- shared semantic state
- shared semantic event
- L4 や execution が利用可能な意味モデル

## 4.4.3 現行実装上の正規 ownership
- `btcts/processing/l3_market_semantics/orderbook/*`
- `btcts/processing/l3_market_semantics/tradeflow/*`
- `btcts/processing/l3_market_semantics/microstructure/*`
- `btcts/processing/l3_market_semantics/continuity/*`
- `btcts/processing/l3_market_semantics/continuity/models/*`
- `btcts/processing/l3_market_semantics/zone/*`

## 4.4.4 どこに書くか
2026-04-04 時点では、L3 は ownership は確立済みだが、collector の常時運転経路で独立永続出力として全面運用されているとはまだ言い切れない。

したがって、現時点の正確な書き方は次である。

- L3 は「市場意味の正規 owner」である
- ただし現行の再起動・live 取得検証で白が付いたのは主に L1/L2 側である
- L3 の常時運転出力をどこへ確定保存するかは、consumer bridge / L4 設計と一体で詰める段階にある

## 4.4.5 現在の理解上の最重要点
L3 は「データをどう書くか」より先に、「意味の owner をどこに置くか」を固定する層である。

つまり、L3 の最優先責務は保存先の確定ではなく、

- どこで意味を定義するか
- どこを truth owner にするか
- どの consumer も同じ意味を再利用できるようにするか

を固定することである。

---

# 4.5 L4 Consumer Models

## 4.5.1 責務
L4 は、L3 の共有意味を consumer ごとに使いやすい形へ整える層である。

ただし、L4 は second L3 になってはならない。
L4 は truth owner ではなく、truth の整形層である。

### L4 が担当するもの
- shared-first な consumer 向け read model
- timeline-ready bundle
- monitoring-ready digest
- operator UI 向け panel input model
- replay / AI / execution 向け適応モデル

### L4 が担当しないもの
- 新しい市場意味の創出
- raw/canonical reconstruction
- L3 を差し置いた interpretation
- daemon / runtime 制御

## 4.5.2 L4 は何を元に何を付与するか
### 入力
- L3 semantic state / event
- 必要に応じて L2 canonical / feature summary
- consumer contract

### 付与するもの
- consumer ごとの read model
- shared digest
- UI / monitoring / replay / AI / execution に適した shape

### 出力
- shared consumer model
- thin adapter model

## 4.5.3 現行実装上の状態
2026-04-04 時点では、L4 は思想と設計方針は定義済みだが、専用 package はまだ本格展開されていない。

したがって現状は、

- L4 は next phase の主要設計対象
- 一部の consumer 向け整形は `apps/operator_ui/` や `market_engine/market_state/` 側に散在している
- これを将来 `processing/l4_consumer_models/` へ shared-first に再編する

という位置づけである。

## 4.5.4 どこに書くか
現時点で L4 の正規永続出力は未固定。
今後、consumer bridge 統一と合わせて次を詰める。

- shared outputs をどこに保存するか
- consumer 専用出力をどこまで薄くするか
- market_state や UI state とどう接続するか

---

## 5. 現行フォルダ構造へのマッピング

### 5.1 現在の主要 ownership

```text
btcts_next/src/btcts/
  collector_vnext/                  実運転中の L1/L2 寄り runtime と orchestration
  ingestion/l2_canonical/           L2 の正規 ownership
  processing/features/              中立特徴量
  processing/l3_market_semantics/   L3 の正規 ownership
  market_engine/execution/          execution layer
  market_engine/profiles/           venue / policy layer
  apps/operator_ui/                 現行 consumer 実装
```

### 5.2 読み方
- `collector_vnext/` は「全部 owner」ではない
- `collector_vnext/` は現行 live runtime として L1/L2 寄りを担っている
- L3 の truth owner は `processing/l3_market_semantics/`
- execution の owner は `market_engine/execution/`
- consumer の owner は `apps/operator_ui/` など

---

## 6. 現行 live runtime で実際に確認できたこと
2026-04-04 の live 確認で、次は実測で白が付いている。

### 確認済み
- Unified Supervisor ボタンから restart request が通る
- watchdog が request を受けて daemon を切り替える
- 新 daemon が立ち上がる
- board WS が `LIVE` へ戻る
- executions WS が `LIVE` へ戻る
- raw / canonical 出力が継続する

### この確認が示すもの
- 現行実運転主系は `collector_vnext` ベースで動いている
- これは新構造移行後の collector 系であり、旧 legacy 直運転ではない
- 白が付いたのは主に L1/L2 寄りの live runtime 経路である

### まだ別途詰めるべきもの
- L3 単独運転 / consumer bridge との接続検証
- L4 shared-first 設計
- docs と tools の完全整合

---

## 7. レイヤ境界の判断表

### L1 かどうか
- その処理は取得・接続・維持のためか
- その処理は provider / websocket / rest / retry の都合か
- その処理は市場意味をまだ作っていないか

yes が多ければ L1。

### L2 かどうか
- その処理は事実を canonical にしているだけか
- その処理は構造的再構成だけか
- その処理は意味ラベルを作っていないか

yes が多ければ L2。

### L3 かどうか
- その処理は市場の意味を与えているか
- その処理は threshold / policy / interpretation を含むか
- その処理は trust / continuity / pressure / sweep を定義しているか

1つでも強く yes なら L3 候補。

### L4 かどうか
- その処理は consumer に使いやすい形へ整えているか
- その処理は truth を再定義せず shape だけ変えているか
- その処理は複数 consumer で shared 化できそうか

yes が多ければ L4。

---

## 8. 現時点の運用用要約

### L1
市場から受け取る。raw と運転状態を書く。

### L2
raw を canonical にする。構造を整える。canonical と checkpoint を書く。

### Features
L2 を元に中立特徴量を作る。まだ意味は付けない。

### L3
L2 と Features を元に市場意味を付与する。意味の owner になる。

### L4
L3 を元に UI / replay / monitoring / AI / execution 向けに shared-first で整形する。

---

## 9. 今後のロードマップとの接続
本仕様書に基づく次アクションは次の順で進める。

1. docs 再配置
2. lightweight verification 固定
3. tools / runbook 整理
4. L4 shared-first 設計
5. consumer bridge 統一

---

## 10. 最終原則

### 原則1
L1 は取得責務であり、意味を持たない。

### 原則2
L2 は事実の構造化責務であり、意味を持たない。

### 原則3
L3 は市場意味の唯一の正本層である。

### 原則4
L4 は truth を作らず、truth を使いやすくする。

### 原則5
collector の live runtime が動いていることと、L3/L4 の設計完了は同義ではない。
両者は分けて検証する。

---

## 11. 一言でまとめると

```text
L1 は取る。
L2 は整える。
L3 は意味を与える。
L4 は使いやすくする。
```

この順序を壊さないことが、vNext の長期保守性そのものである。
