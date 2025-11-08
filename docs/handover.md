## Btc Ts-ライブ引継ぎ（固定）

※このキャンバスは引継ぎの内容以外書き込みを禁ずる
　大切な内容につきその他の目的で使用せず上書きは禁止です

## 目的

-日々の作業・課題・決定・次アクションを \*\*1 か所\*\に集約し、チャットをまたいだ瞬時の再開を可能にする。

## 記入フォーマット（必須）

```
## <YYYY-MM-DD <短い見出し
  - 作業メモ
    ...

  - 完了タスク
    ...

  - 次の候補タスク
    A) ...

    B) ...

  - 参照: PR/コミット/スクショ/ログ へのリンク or 要約
```

- 作業報告は末尾に追記していくこと。
- 無駄な改行は避け無駄に長くしない事。
- “意味のある粒度”で書く（誰でも追従できるように）。
- 決定事項は `docs/` の該当ファイル（計画/ADR 等）へ\*\*要約のみ\*\*反映。

---

##### 以下直近の作業報告

---

🧭 BtcTradeSystem V1 — 情報収集ドメイン 開発引き継ぎ書（Collector / Health 現行）

最終更新：2025-11-07

🎯 現在の開発段階
フェーズ 名称 状況 備考
Phase 1 Collector 基盤構築 ✅ 完了（基礎レイヤ） heartbeat → status 連携・レート制御の足場整備済み
Phase 2 Health システム ⚙️ 進行中（UI まで完了） 健全性 UI・設定 UI・status 反映は実装済、制御命令部分未実装
Phase 3 Ops-Audit 構築 ⏸ 未着手 Collector/Health の監査イベントを蓄積開始予定
✅ 完了済み項目（ロードマップ対照）
🧱 Collector 基盤構築（Phase 1）

collector_status.py：status.json の原子的更新／fsync 対応済み。

collector_rate.py：取引所ごと rate 制御（bucket 制御／burst 制限）導入。

collector_scheduler.py：周期制御・優先度スケジュール稼働確認。

collector_entry.py / ops/collector/entry.py：

start / status CLI 実装。

PID ロック／多重起動防止（--force 対応）。

endpoints_def.yaml：

唯一の正として collector endpoints を集中管理。

atomic 書込・defaults/current の混在禁止。

set_collector.py：

Streamlit 設定 UI（取引所・endpoint・rate 編集）。

commit() による安全保存＋監査出力実装。

UI 統合：

ダッシュボードタブなし設計（Collector はバックグラウンド専用）。

設定 UI から Collector 制御可能（後述拡張予定）。

動作確認：

heartbeat / status 両方が数秒単位で更新されることを確認済。

🩺 Health システム構築（Phase 2）

ui_health.py：

健全性カード／タイムライン表示／自動更新切替／閾値スロット UI 実装。

get_status() でヘッダー色を反映（normal/warn/crit）。

health_svc.py：status.json 読込・整形ロジック確立。

設定連携：

tabs.yaml + set_health.py 設計ルールにより、dashboard.py/settings.py 改変不要 で UI 追加完了。

UI 登録ルール仕様書作成済み（GPT 混乱防止仕様）。

⚙️ 進行中タスク
項目 内容 状況
bitFlyer 実 API 化 ダミー → 実ランナーへ差替（orderbook/trades） 着手前
RateController 拡張 各 exchange 毎に動的 burst 調整 設計検討中
Health⇄Collector 連携 Health による Collector 停止/slow_down 制御 未実装
set_collector の検証 UI 保存 →endpoints_def.yaml の diff 追跡 動作検証済（軽度）
dev_audit 監査 設定・heartbeat イベント出力 一部出力済み（粒度調整必要）
📋 次に行うこと（Phase 2〜3 ブリッジ）

bitflyer_public.py 実 API 化

REST/WS どちらでも heartbeat 更新を継続。

API キー認証・例外捕捉・再試行・429 抑制を collector_rate と統合。

Health→Collector 制御連携

health_actions.py に slow_down() / restart() / disable() 実装。

Health UI の閾値超過で collector 停止命令を発行。

Ops-Audit 導入

collector / health / settings のイベントを監査ファイル（dev_audit.jsonl）に一元出力。

ops_audit_writer.py と ui_ops_audit.py のプロトタイプ開始。

UI 拡張

health タブ下に “Collector 起動/停止” トグル + 稼働中プロセス数表示（開発モードのみ）。

ドキュメント整備

docs/ui_addition_spec.md 追加済仕様書をドキュメント化。

Collector/Health の Phase2 完了報告をハンドオフ仕様書に反映。

⚠️ 課題・注意点
区分 内容 対応予定
Windows ファイルロック heartbeat 原子的書込で一部タイミング競合発生 \_atomic_write_text() に retry/backoff 導入予定
typing 警告 Streamlit 型ヒントで pylance 警告 cast() 方式に統一で解消済み
PYTHONPATH 問題 PowerShell タブを分けると path 無効 起動時 Set-Location + PYTHONPATH を明示
Collector 停止 UI Health タブ下で開発中のみ有効化予定 st.toggle() 実装で制御
dev_audit 出力過多 minor イベントが多くノイズ化 イベントレベルで抑制機構を導入予定
🧾 今後の必須拡張（Phase3 以降見据え）

Ops-Audit 統合
→ 監査ログを Health/Collector/Settings に統合
→ DQ/Resource/Timeline レポート出力

学習連携前処理
→ status.json と trade 履歴を統合フォーマット化（AI 学習基盤用）

長時間運転テスト
→ 8〜12h 連続稼働＋ status 整合性検証

NAS 同期対応
→ Leader/Secondary 構成テストへ移行（Phase7 準備）

📚 ファイル改変禁止リスト
ファイル 理由
features/dash/dashboard.py タブ自動登録制。手動追加禁止。
features/settings/settings.py 設定セクション自動検出。手動編集禁止。
config/ui/tabs_def.yaml defaults 専用（ユーザー編集禁止）。
✅ 引き継ぎメモ（次 GPT 向け）

本プロジェクトは「Collector と Health の安定連携フェーズ」中。
既に UI 自動登録・設定反映・heartbeat/status 更新は安定稼働済。
次セッションでは bitFlyer API の実ランナー置換と、Health 制御連携から開始すること。
dashboard.py/settings.py の改変は禁止。
tabs.yaml と set\_\*.py のみでタブ追加可能。

---

# BtcTradeSystemV1 — 引き継ぎメモ（2025-11-08）

## 今日の作業

- **健全性タブ（features/settings/set_health.py）** の保存不具合を調査。
- 保存ボタン押下時の `apply_pending()` 呼び出し・dev_audit 出力・mtime 変化を確認。
- Streamlit のセッション管理 (`st.session_state`) を用いた dirty フラグ、pending データ構築ロジックを検証。
- 結果、保存処理が動作しているものの、UI 閉じ操作でも保存が走る、保存ボタン無反応、デフォルト復元不全といった複合バグを確認。
- 問題の根本が `features/settings/settings.py` のハンドラ実装にある可能性を特定。

## 次のタスク

1. **features/settings/settings.py の検証・修正**
   - 「保存」ボタン押下時のみ各タブの `on_save()` を呼ぶように明確化。
   - 「閉じる」「外部クリック」で保存されないよう、pending 破棄処理を追加。
   - `on_default()` 実行時の UI 再反映ロジックを統一。
2. **保存フロー統一テスト**
   - health / dash / audit / collector 全設定で `on_save()` → `settings_svc.save_yaml()` の動作確認。
   - dev_audit.jsonl に `"settings.*.update"` ログが正しく出るかを再確認。
3. **UI 動作確認**
   - 保存ボタンの活性化条件が正しいか（dirty フラグと連動）。
   - 外側クリックで保存されないこと。
   - デフォルト復元時に正しい初期値が表示されること。

## 気づいたこと・改善案

- 設定保存処理は個別タブごとに `on_save()` が存在するが、settings ハブ側が全タブ共通で管理しているため、**pending キー名の統一と破棄処理の共通化**が必要。
- `on_default()` が即書き込みを行う現仕様は UX 的に混乱を生む。→ UI 値のみ復元・保存で確定する方式に統一すべき。
- Streamlit のセッションがタブを跨いで dirty 状態を保持しているため、設定ハブでセッションキー初期化を明示的に行う必要あり。
- 今後の機能追加（collector, health, monitor など）でも同じ保存制御が再利用できるよう、**settings ハブを共通 I/F に整理**すべき。

---

本日の作業記録

設定 UI の統一化を完了

ui_common.py 新規作成（閉じる／デフォルト／保存＋確認ダイアログ＋即時反映、dirty 管理、未保存破棄を共通提供）。

set_dash.py / set_health.py / set_collector.py を共通フッターに統一。

「閉じる」で確実にモーダル終了（破棄＋ rerun）。「保存／デフォルト」は確認 → 実行 → 即時反映に統一。

保存挙動の是正

set_collector.py の commit() を修正。UI の順序を正としてそのまま保存し、削除も正しく反映。

表示と実体の整合

set_health.py 冒頭キャプションを settings_svc.get_paths() に揃え、**適用先（外部 CONFIG）／既定（def）**を明示。

各所の微修正（未使用 import 削除、重複関数除去、軽バリデーション）。

ダッシュボード側の安全化

dashboard.py：\_clamp_dashboard_order() で main 最左固定／collector・basic を Dash から非表示、initial 不整合の自動補正。

運用支援

監査ログの静音フィルタ（PowerShell 3 種）提示。

明日のタスク（不具合と修正方針・テスト）
P1: Collector 設定タブで初期化エラー

症状: st.session_state has no key "set.collector.add_names" エラー。
原因想定:

set_collector.py の初期描画で set.collector.add_names を setdefault していない。

あるいは settings.py（ハブ）でタブ切替時の初期化順より先に参照している箇所がある。

修正案（方針）:

render() の先頭で st.session_state.setdefault("set.collector.add_names", []) を一括初期化。

追加ポップオーバーや一時保持で参照する他のキーも同様に setdefault をそろえる（例：set.collector.pending）。

依存が複数箇所にある場合は、ui_common.py に「prefix キー群の初期化ヘルパ」を追加し、set_collector.py 冒頭で 1 行呼び出しに統一。

テスト:

Dashboard 起動 → 設定 →「コレクター」タブを開く。

エラーが出ないこと。新規追加ポップオーバーが開くこと。

取引所追加 → 保存 →endpoints_def.yaml に反映（順序／削除も）。

P1: 健全性ビューで「Health 情報の取得に失敗」

症状: ヘルス画面冒頭に失敗トースト。
原因想定（優先順）:

config/ui/health.yaml / monitoring.yaml の欠落または形式不整合（デフォルト反映不足）。

health_svc.py のロード時パス分解が settings_svc.get_paths() と不整合。

収集側のデータが未生成／参照パス不一致で eval() が空／例外。

修正案（方針）:

settings_svc.reset_to_default("health") / ("monitoring") を一度実行して正準ファイルを外部 CONFIG へ強制展開。

health_svc.py で参照する既定パスを def/current 一本化（settings_svc.get_paths() を使う）。

依存データ（例：data/collector/status.json 等）必須の場合、空でも動作するフォールバックロジック（空時は“データなし”扱いで落とさない）。

テスト:

設定 → 健全性 →「デフォルト」実行 → 反映後にダッシュへ戻り、エラーが消えること。

閾値変更 → 保存 → カード／タイムラインの見た目が更新。

ログに settings.write.health / settings.write.monitoring が出る。

P2: 保存直後に視覚反映が遅れるケース

症状: 「閉じる」で反映されず、再度設定を開くと反映している。
原因想定:

_exec_\* 実行内の例外で UI.render_section_controls() の mark_dirty()+rerun が到達しない。

ハブ(settings.py)の \_\_settings_dirty 監視が、特定条件で早期 return。

修正案（方針）:

\_exec_save/\_exec_default に try/except を入れて必ず UI 側の処理完了まで到達させる。

settings.py の dirty 検知 →st.rerun() のブロックを一番最後に残し、先に別の rerun/return が走らないよう整序。

テスト:

各タブで保存／デフォルト後、即ヘッダやタブ構成が変わること。

例外を意図的に発生させた場合でも（色値に不正入力等）、UI が固まらないこと。

気づき・課題

初期化と参照の順序

st.session_state は参照前に必ず初期化（setdefault）を徹底。今回の collector のように、追加 UI のポップオーバーで未初期化キーを即参照しがち。

def/current の一本化

settings_svc.get_paths(area) を単一ソースとし、\*\_svc.py 側のハードコードを徐々に排除。

監査の静音運用

本番運用を見据え、今日の PowerShell フィルタを tools/audit_tail_settings.ps1 として常設すると便利。

UI ガイド文

collector のカードに追加した一文（削除の確定方法）、効果的。各タブでも誤操作ポイントに 1 行説明を置くと事故が減る。
