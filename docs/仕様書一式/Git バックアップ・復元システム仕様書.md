# Git バックアップ・復元システム仕様書（BtcTradeSystemV1）

---

## 目的

本仕様書は、`BtcTradeSystemV1` における Git ベースのバックアップおよび復元ポイント（Restore Point, RP）管理の仕組みを整理したものです。リポジトリ全体の安定性を担保し、誤操作による破損を防ぎながら、日常的な差分保存・検証・フルバックアップを安全に運用することを目的とします。

---

## 構成ファイル一覧

| 種別                 | ファイルパス                       | 説明                                          |
| -------------------- | ---------------------------------- | --------------------------------------------- |
| 差分バックアップ生成 | `scripts/git/git_rp_make.ps1`      | 復元ポイント作成および差分 ZIP 生成スクリプト |
| 復元ポイント一覧     | `scripts/git/git_rp_list.ps1`      | `rp-*`タグとフルバックアップの一覧表示        |
| ハンドオフ生成       | `scripts/handoff/make_handoff.ps1` | 開発引き継ぎ用の ZIP 出力（Git 情報含む）     |

---

## 保存ディレクトリ構造

バックアップはすべてリポジトリ外に保存される。

```
BtcTradeSystemV1_git/
├─ git_rp/           # 差分（Restore Point）保存先
│   └─ rp-YYYYMMDD_HHmmss/
│       ├─ metadata.json
│       ├─ diff.patch
│       ├─ SUMMARY.txt
│       ├─ changed_files.txt
│       └─ files/
│           └─ <差分抽出対象ファイル群>
│
├─ git_full/         # フルバックアップ（.bundle形式）保存先
│   ├─ <name>.bundle
│   └─ <name>.json
```

---

## スクリプト別仕様

### 1. `git_rp_make.ps1`

#### 機能

- 現在の HEAD にタグを打ち、復元ポイント（`rp-YYYYMMDD_HHmmss`）を生成。
- `-Diff` 指定時は差分比較 (`baseTag..HEAD`) に基づき、差分 ZIP を生成。
- 出力先はリポ外 `BtcTradeSystemV1_git/git_rp/` 固定。

#### 主なパラメータ

| パラメータ | 型     | 説明                                                 |
| ---------- | ------ | ---------------------------------------------------- |
| `-Commit`  | switch | タグ付け前に commit を作成                           |
| `-Diff`    | switch | 差分バックアップ生成（base..HEAD）                   |
| `-BaseTag` | string | 差分起点タグを手動指定                               |
| `-Zip`     | switch | 出力を ZIP 化（デフォルト false でディレクトリ展開） |
| `-RpMemo`  | string | メモ（タグコメント／差分情報に埋め込み）             |

#### 出力内容

- タグ名：`rp-YYYYMMDD_HHmmss`
- 差分フォルダ構成：

  - `metadata.json` … 差分統計およびヘッダ情報
  - `SUMMARY.txt` … 差分範囲／変更件数サマリ
  - `diff.patch` … `git diff --binary` によるパッチ
  - `files/` … 変更対象ファイルのコピー

#### 実行例

```powershell
# タグのみ（軽量）
pwsh .\scripts\git\git_rp_make.ps1 -Commit

# 差分付き＋ZIP出力
pwsh .\scripts\git\git_rp_make.ps1 -Commit -Diff -Zip -RpMemo "節目: UI改修前"
```

---

### 2. `git_rp_list.ps1`

#### 機能

- 差分タグ（rp-\*）とフルバックアップ（.bundle）を最新順に一覧表示。
- `metadata.json` に基づき変更件数を詳細表示可能。

#### 主なパラメータ

| パラメータ  | 型     | 説明                             |
| ----------- | ------ | -------------------------------- |
| `-Details`  | switch | 変更件数やコミット情報を表示     |
| `-ShowTree` | switch | 保存ディレクトリツリーも表示     |
| `-OpenRoot` | switch | エクスプローラで保存ルートを開く |
| `-Limit`    | int    | 表示件数（既定 10 件）           |

#### 出力例

```
== Restore Points (rp-* / full)  (latest 10) ==
2025-10-14  15:52:58  14329ba  - Restore Point rp-20251014_171132 - 最終検証 ZIP
2025-10-14  15:32:37  e234e71  - Restore Point rp-20251014_153440 - chore: snapshot for rp-20251014_153224
2025-10-14  12:10:03  c9d8817  - Full Backup  BtcTradeSystemV1-full-main-20251014_121002
Press any key to exit...
```

---

### 3. `git_full_backup.ps1`

#### 機能

- 現在のリポジトリ全体を `.bundle` 形式で完全バックアップ。
- 出力先は `BtcTradeSystemV1_git/git_full/` 固定。

#### 概要フロー

```powershell
# フルバックアップ実行
pwsh .\scripts\git\git_full_backup.ps1 -Name "snapshot-20251014_1700"

# 検証
$bundle = Get-ChildItem "$env:USERPROFILE\BtcTradeSystemV1_git\git_full" -Filter *.bundle | Sort LastWriteTime | Select -Last 1
git bundle verify $bundle.FullName
```

#### 出力物

- `<name>.bundle` … 完全リポジトリアーカイブ
- `<name>.json` … メタ情報（branch/head/timestamp）

#### 復元（クローン）手順

```powershell
# A) 新規ディレクトリにクローン
git clone "<bundle>" <dest_dir>
cd <dest_dir>
git checkout main
```

---

## 差分検証手順

差分 ZIP の正当性を確認するための検証スクリプト（簡易テスト）:

```powershell
$zip   = (Get-ChildItem "$env:USERPROFILE\BtcTradeSystemV1_git\git_rp" -Recurse -Filter *.zip | Sort LastWriteTime | Select -Last 1).FullName
$rpchk = "$env:TEMP\_rpchk_apply"
Remove-Item $rpchk -Recurse -Force -ErrorAction SilentlyContinue
Expand-Archive $zip -DestinationPath $rpchk -Force
$meta  = Get-Content "$rpchk\metadata.json" -Raw | ConvertFrom-Json
$base  = if ($meta.base_tag) { $meta.base_tag } else { Split-Path (Split-Path $zip -Parent) -Leaf }
$repo  = "$env:USERPROFILE\BtcTradeSystemV1"
$wt    = "$env:TEMP\wt_base"
git -C $repo worktree remove "$wt" -f 2>$null | Out-Null
git -C $repo worktree add --detach "$wt" "$base" | Out-Null
$patch = Join-Path $rpchk 'diff.patch'
if ((Test-Path $patch) -and ((Get-Item $patch).Length -gt 0)) {
  git -C "$wt" apply --check --index "$patch"
  Write-Host "[OK] patch validated against $base" -ForegroundColor Green
} else {
  Write-Host "[OK] empty diff (no changes since $base)" -ForegroundColor DarkGray
}
git -C $repo worktree remove "$wt" -f | Out-Null
```

---

## 運用ルール

1. **保存先はリポ外固定。** プロジェクト内には一切バックアップを残さない。
2. **自動コミット禁止。** 通常はタグのみ。必要時のみ `-Commit` を明示。
3. **復元操作は必ず手動レビュー後。** スクリプトでの自動ロールバックは作らない。
4. **フルバックアップは節目ごとに実施。** 例：大規模修正／月次アーカイブ。
5. **タグ命名規則統一：** `rp-YYYYMMDD_HHmmss`（24h 制・秒単位ユニーク）。

---

## 検証済み挙動

| 項目                       | 結果 |
| -------------------------- | ---- |
| 差分 RP 作成（タグ＋ ZIP） | OK   |
| フルバックアップ（bundle） | OK   |
| 一覧表示（rp ＋ full）     | OK   |
| 差分検証（空／非空）       | OK   |
| メタ生成・保存先変更       | OK   |

---

## 補足

- 差分バックアップは「ファイル数・挿入・削除数」まで統計化。
- フルバックアップは `git bundle` により外部共有可能（リモート不要）。
- ハンドオフ ZIP 作成時（`make_handoff.ps1`）には自動で最新の RP タグ／Git 状態が含まれる。

---

**最終更新:** 2025-10-14 / system auto-generated

