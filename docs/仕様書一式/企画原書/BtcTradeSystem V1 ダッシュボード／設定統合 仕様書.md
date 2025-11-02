# 📘 BtcTradeSystem V1 ダッシュボード／設定統合 仕様書

## 概要
本仕様は、ダッシュボード (`features/dash/dashboard.py`) と設定モーダル (`features/settings/modal_ui.py` / `settings.py`) を統合した最新構成を示す。歯車ボタン（⚙️）によって開く設定モーダルをハブとし、配色設定やデモアラート制御を統一管理する。

---

## 1️⃣ ダッシュボード構成 (`features/dash/dashboard.py`)
### 1.1 基本設計
- **目的**：Streamlit ベースの全機能ハブ。タブ構成・スタイル適用・モーダル設定の呼び出しを行う。
- **UI構成**：
  - ヘッダー（タイトル・アラートチップ・歯車）
  - メインタブ群（`main`, `health`, `audit`）
- **設定呼出し**：歯車クリック → `features/settings/modal_ui.settings_gear()` 呼出し。

### 1.2 機能要点
| 項目 | 内容 |
|------|------|
| **タブ制御** | `config/ui/tabs.yaml` / `tabs_def.yaml` により順序・初期タブ・有効化を制御 |
| **CSS適用** | `_inject_tokens()` と `_load_css()` により styles/*.css を順序読み込み |
| **配色同期** | `_inject_alert_palette_vars(settings.get_alert_palette())` により `dash.yaml` の色を :root に反映 |
| **デモアラート制御** | `_demo_alerts_changed()` および `_sync_demo_alerts_with_flag()` により Gear UI とヘッダーのチップを同期 |
| **モーダル起動** | `from btc_trade_system.features.settings.modal_ui import settings_gear` により統合 |

---

## 2️⃣ 設定モーダル (`features/settings/modal_ui.py`)
### 2.1 機能概要
歯車ボタン押下で開くダイアログ。初期タブに配色ピッカーを配置。

### 2.2 タブ構成
| タブ | 内容 |
|------|------|
| 初期設定 | `settings/settings.py.render()` 呼出し（配色・デフォルト・保存ボタン） |
| 健全性 | `settings_ui.render()` 呼出し（健全性監視UI） |
| 監査 | 将来拡張。監査ログ設定や保持期間調整を想定 |

### 2.3 動作仕様
- モーダルの開閉状態は `_SETTINGS_FLAG` により `st.session_state` で一時保持。
- 配色ピッカーの編集 → `dash.yaml` に即時保存／デフォルト復元は `dash_def.yaml` 読込。
- 監査ログ (`audit_dev/writer.py`) に保存／開閉イベントを記録。
- Streamlit バージョン差異により、`st.dialog()` / `st.experimental_dialog()` 両対応。

---

## 3️⃣ 配色設定処理 (`features/settings/settings.py`)
### 3.1 主関数 `render()`
| 操作 | 処理内容 |
|------|-----------|
| 適用（今回のみ） | :root のCSS変数更新のみ（yaml未保存） |
| デフォルト | `dash_def.yaml` の初期値を読み出しUIへ反映 |
| 保存 | `config/ui/dash.yaml` に配色を書込（atomic replace: `.tmp` → `.yaml`） |

### 3.2 関連ファイル
| ファイル | 用途 |
|----------|------|
| `config/ui/dash.yaml` | 現行配色定義（ユーザ保存用） |
| `config/ui/dash_def.yaml` | 既定配色定義（デフォルト復元用） |

---

## 4️⃣ 監査・開発支援ログ (`features/audit_dev/writer.py`)
- `W.emit(event, level, feature, payload)` により操作を JSONL で記録。
- 主なイベント：
  - `settings.open`, `settings.save_click`, `settings.close`
  - `settings.restore_default`, `settings.apply_once`
  - ファイル保存失敗時は `level=ERROR` で出力。

---

## 5️⃣ 内部データフロー
```mermaid
graph TD;
A[歯車クリック] --> B(Modal Dialog 起動);
B --> C{タブ選択};
C -->|初期設定| D[settings.render() → 配色ピッカー];
C -->|健全性| E[settings_ui.render()];
C -->|監査| F[未実装: ログ保持設定];
D --> G[dash.yaml へ保存];
D --> H[dash_def.yaml より復元];
D --> I[:root CSS変数更新];
```

---

## 6️⃣ 次期開発展開（提案）
- [ ] 「監査」タブに監査ログのローテーション／保持日数設定を追加。
- [ ] `ui_health.py` から健全性情報を設定タブに統合（view統一）。
- [ ] モーダル右下に「再読込」ボタンを追加し、UI反映を即時反映。

---

## 7️⃣ バージョン情報
| 要素 | 現行値 |
|------|--------|
| Streamlit | v1.38～v1.50 対応（dialog/experimental_dialog 吸収） |
| 対象モジュール | dashboard.py / modal_ui.py / settings.py / settings_ui.py |
| 構成確認日 | 2025-10-31 |

---

✅ **現状の完成度**：UI構造・保存・デフォルト復元・ダッシュボード統合すべて安定動作確認済み。
