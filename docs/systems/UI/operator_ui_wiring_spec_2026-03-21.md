# path: ./docs/systems/UI/operator_ui_wiring_spec_2026-03-21.md
# desc: operator UI wiring specification の概要

## 目的
本書は `docs/systems/UI/BTC-TS Operator UI 完全設計書 v1.md` を基準に、現行 `btcts_next/src/btcts/apps/operator_ui` の配線を機能単位で明文化した補助仕様書である。特に War Room を中心に、**どの機能がどのファイルを読み、どの helper/bridge/service を通るか**を詳述する。

---

## 1. UI 全体入口

### 1.1 アプリ入口
**所在**
- `btcts_next/src/btcts/apps/operator_ui/app.py`

**責務**
- Streamlit アプリの入口
- サイドバー、ページ選択、共通 session state の初期化
- 選択ページに応じて `views/*.py` の `render()` を呼ぶ

### 1.2 War Room 入口
**所在**
- `btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py`

**描画順**
1. `warroom_header.render()`
2. `warroom_alert_engine.render()`
3. `ai_operator_panel.render()`
4. `decision_log_panel.render()`
5. `watch_list_panel.render()`
6. `warroom_timeline.render()`
7. `market_regime_panel.render()`
8. `market_monitor.render()`
9. `liquidity_pressure_panel.render()`
10. `trade_flow_monitor.render()`
11. `ai_signal_panel.render()`
12. `strategy_state_panel.render()`
13. `risk_monitor_panel.render()`
14. `agent_panels.render()`
15. `ai_reasoning_panel.render()`
16. `ai_market_summary_panel.render()`
17. `ai_conversation_panel.render()`

---

## 2. UI のデータ系統

現行 UI は大きく 3 系統を読む。

### 2.1 live 系
**主ファイル**
- `btcts_next/src/btcts/apps/operator_ui/components/live_bridge.py`

**読むもの**
- `market_data` の canonical board/trade
- collector state/health/checkpoint/audit
- logs/audit.jsonl

**使い道**
- War Room の live canonical 優先表示
- Collector page の continuity / health / audit 表示

### 2.2 research / replay 系
**主ファイル**
- `btcts_next/src/btcts/apps/operator_ui/components/research_bridge.py`

**読むもの**
- 最新 replay payload
- 最新 research experiment artifact
- board/trade row の抽出
- replay 起点の metrics 化

**使い道**
- research 実験結果
- replay fallback
- regime / best_strategy / replay board/trade metrics

### 2.3 market_state 系
**主ファイル**
- `btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py`
- `btcts_next/src/btcts/apps/operator_ui/market_state_service.py`

**読むもの**
- `market_state/.../type=market.overview/.../part-00001.jsonl`

**使い道**
- 市場モニター系の freshness / age / source 系補助
- market overview の要約表示

---

## 3. War Room 機能別配線

### 3.1 War Room Situation
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py`

**主な読み元**
- `latest_live_board_metrics()` from `live_bridge.py`
- `recent_live_tradeflow_metrics()` from `live_bridge.py`
- `load_latest_experiment_payload()` from `research_bridge.py`
- fallback で `load_latest_replay_payload()` + row metrics

**役割**
- live board / trade と research experiment を合成し、
  - 市場レジーム
  - スプレッド状態
  - 圧力
  - 約定フロー
  - AI判断
  - リスク
  を上段 summary として表示

### 3.2 War Room Alerts
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/warroom_alert_engine.py`

**主な読み元**
- live canonical board / tradeflow
- research experiment
- 直近監査レイテンシ（audit 系）

**備考**
- 今回の作業で replay 固定文言から、`live_canonical / research_experiment / 直近監査レイテンシ` のような live 寄り表示へ寄せた
- live 条件に応じて alert 行の source を切り替える

### 3.3 AI Operator
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/ai_operator_panel.py`

**主な読み元**
- live canonical board / tradeflow from `live_bridge.py`
- research experiment from `research_bridge.py`
- operator context 生成は panel 内部
- AI 応答生成は `btcts_next/src/btcts/apps/operator_ui/ai_runtime.py` の `generate_answer()`
- decision 保存は `btcts_next/src/btcts/apps/operator_ui/decision_log_store.py`
- watch 保存は `btcts_next/src/btcts/apps/operator_ui/watch_store.py`

**現在の配線仕様**
- live 市場データがある場合は `is_live_market=True`
- 実行実態が fallback local のとき、表示上は `AIモード=live-local`
- 本文先頭は `local AI mode active: ...` に差し替え
- live 時は `Replayへ送る` を隠す
- `Watchに追加` は `append_watch()` を直接呼ぶ

### 3.4 AI Operator Decision Log
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/decision_log_panel.py`

**主な読み元**
- `btcts_next/src/btcts/apps/operator_ui/decision_log_store.py`

**役割**
- AI Operator の decision 保存先 JSONL を読み、最新数件を表示
- 保存先 caption もここで表示

### 3.5 Watch List
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/watch_list_panel.py`

**主な読み元**
- `btcts_next/src/btcts/apps/operator_ui/watch_store.py`

**役割**
- watch list JSONL の読み込み
- Replay / Research / 削除 / 全削除導線
- 現在は AI Operator 側の `append_watch()` により即時反映される

### 3.6 Situation Timeline
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/warroom_timeline.py`

**主な読み元**
- live canonical board / tradeflow from `live_bridge.py`
- research experiment from `research_bridge.py`
- fallback 時のみ replay payload

**今回の重要変更**
- `live_bridge._market_type_path()` が最新 available date を見るよう修正されたため、日付境界をまたいでも live ファイルを引ける
- live timeline がある場合は `Replay` ボタンを出さない
- caption は `live_canonical / research_experiment` に切り替わる

### 3.7 市場レジーム
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/market_regime_panel.py`

**主な読み元**
- `latest_live_board_metrics()` from `live_bridge.py`
- `load_latest_experiment_payload()` from `research_bridge.py`
- fallback: `load_latest_replay_payload()`

**役割**
- live board spread / imbalance から pressure を推定
- research regime で regime 名を補う

### 3.8 市場モニター
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/market_monitor.py`

**主な読み元**
- live canonical board from `live_bridge.py`
- market overview freshness/age from `market_state_bridge.py`
- fallback: replay board from `research_bridge.py`

**役割**
- best bid/ask, spread, bid/ask depth, imbalance を表示
- source / freshness / age / trust / boundary / series などを caption 化

### 3.9 流動性圧力
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/liquidity_pressure_panel.py`

**主な読み元**
- `latest_live_board_metrics()` from `live_bridge.py`
- fallback: replay board from `research_bridge.py`

**役割**
- bid/ask wall size と wall ratio を表示
- live canonical があればそちら優先

### 3.10 約定フロー
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/trade_flow_monitor.py`

**主な読み元**
- `recent_live_tradeflow_metrics()` from `live_bridge.py`
- fallback: replay tradeflow from `research_bridge.py`

**役割**
- buy volume / sell volume / delta / recent count を表示

### 3.11 AIシグナル
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/ai_signal_panel.py`

**主な読み元**
- live board + live tradeflow from `live_bridge.py`
- regime / best strategy from `research_bridge.py`
- fallback: replay board/tradeflow

**役割**
- spread / imbalance / delta / regime / best strategy を合成して簡易判断を出す

### 3.12 戦略状態
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/strategy_state_panel.py`

**主な読み元**
- `load_latest_experiment_payload()` from `research_bridge.py`

**役割**
- research artifact の summary, best_strategy, regime_report から戦略モードと信頼度を表示

### 3.13 Risk Monitor
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/risk_monitor_panel.py`

**主な読み元**
- live board / live tradeflow from `live_bridge.py`
- fallback: replay board / tradeflow from `research_bridge.py`
- `BTC_TS_LOGS_DIR/audit.jsonl`

**役割**
- spread, imbalance-delta conflict, latency から risk score を算出

### 3.14 Agent Panels
**コンポーネント**
- `btcts_next/src/btcts/apps/operator_ui/components/agent_panels.py`

**主な読み元**
- live board / live tradeflow from `live_bridge.py`
- research experiment from `research_bridge.py`
- `audit.jsonl`

**役割**
- Analyst AI / Strategy AI / Risk AI の 3 観点 summary

### 3.15 AI Reasoning / AI市場サマリー / AI会話
**所在**
- `btcts_next/src/btcts/apps/operator_ui/components/ai_reasoning_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/ai_market_summary_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/ai_conversation_panel.py`

**共通傾向**
- live canonical + research experiment を優先
- fallback として replay/research artifact を使う
- AI 会話パネルは UI の quick question / intent / style と `ai_runtime.py` を使う

---

## 4. Collector page の主な配線

Collector page 全体の中心は、**collector state / health / checkpoint / audit と origin continuity** を live bridge 経由で読むことにある。

### 4.1 主な読み元
**所在**
- `btcts_next/src/btcts/apps/operator_ui/components/live_bridge.py`
- `btcts_next/src/btcts/apps/operator_ui/views/collector_page.py`

**読むもの**
- `status.json`
- `daemon_health.json`
- `checkpoint.json`
- `origin_status.json`
- `audit.jsonl`

### 4.2 今回整理された表示
- `WS Continuity (origin_status)`
- `Origin Continuity Summary (status.json)`
- `Origin Continuity Audit Summary`
- freshness / age / stale 判定

これにより、Collector page は raw ログ画面ではなく、**collector_vnext の運用面を監視する live console** に近づいた。

---

## 5. docs 設計との差分

### 5.1 docs より実装が進んでいる点
- War Room が replay 専用ではなく、かなりの部分で `live_canonical` を優先する
- AI Operator が local fallback を含む実運用表示まで持っている
- Watch / Decision Log の永続化が UI 内で成立している

### 5.2 docs に追記した方がよい点
- `live_bridge` / `research_bridge` / `market_state_bridge` の三系統構造
- War Room 各パネルの source 優先順位
- `live canonical -> research supplement -> replay fallback` の原則
- date 境界で `live_bridge` が latest available date を見ること

---

## 6. 主要ファイル所在一覧

### UI 入口
- `btcts_next/src/btcts/apps/operator_ui/app.py`
- `btcts_next/src/btcts/apps/operator_ui/views/warroom_page.py`

### bridges / services / stores
- `btcts_next/src/btcts/apps/operator_ui/components/live_bridge.py`
- `btcts_next/src/btcts/apps/operator_ui/components/research_bridge.py`
- `btcts_next/src/btcts/apps/operator_ui/components/market_state_bridge.py`
- `btcts_next/src/btcts/apps/operator_ui/market_state_service.py`
- `btcts_next/src/btcts/apps/operator_ui/watch_store.py`
- `btcts_next/src/btcts/apps/operator_ui/decision_log_store.py`
- `btcts_next/src/btcts/apps/operator_ui/ai_runtime.py`

### War Room components
- `btcts_next/src/btcts/apps/operator_ui/components/warroom_header.py`
- `btcts_next/src/btcts/apps/operator_ui/components/warroom_alert_engine.py`
- `btcts_next/src/btcts/apps/operator_ui/components/ai_operator_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/decision_log_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/watch_list_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/warroom_timeline.py`
- `btcts_next/src/btcts/apps/operator_ui/components/market_regime_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/market_monitor.py`
- `btcts_next/src/btcts/apps/operator_ui/components/liquidity_pressure_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/trade_flow_monitor.py`
- `btcts_next/src/btcts/apps/operator_ui/components/ai_signal_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/strategy_state_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/risk_monitor_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/agent_panels.py`
- `btcts_next/src/btcts/apps/operator_ui/components/ai_reasoning_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/ai_market_summary_panel.py`
- `btcts_next/src/btcts/apps/operator_ui/components/ai_conversation_panel.py`

---

## 7. 今回の配線変更で特に重要な点
1. live canonical がある時は replay へ戻り過ぎない
2. origin continuity は `origin_status.json` と `status.json.origin_continuity` の両方で読める
3. AI Operator は live 市場時に `Replayへ送る` を隠し、`live-local` で表示を整える
4. Watch は panel 間 relay ではなく `append_watch()` 直接保存で安定化した
5. date 境界での live file 読み損ねは `latest available date` 解決で改善した
