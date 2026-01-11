# Git バックアップ・復元システム仕様書（NEXT 正準）

> ======================================================================
> ⚠️ 境界宣言（V1由来 / NEXT読み替え）
>
> 本仕様書は V1 の思想（安全性・再現性・手動レビュー優先）を継承する。
> ただし、保存先・構造・スクリプト配置は NEXT 正準に統一する。
>
> - V1の保存先（例：%USERPROFILE%\BtcTradeSystemV1_git）は使用しない
> - 差分成果物（metadata.json / diff.patch 等）を正準としない（NEXTでは作らない）
> - 正準のバックアップ先は常に E:\btc_ts\backup
> ======================================================================

## 1. 目的

BtcTradeSystem NEXT における Git ベースのバックアップと復元手順を、運用でブレない「正準」として固定する。

本書のゴール：
- 誤操作で壊さない（自動ロールバック禁止、必ずレビュー）
- 復元手順が一意（タグ/Bundleどちらでも復元できる）
- GPT迷子防止（外部ルートの扱いを明文化）

## 1.5 設計原則（NEXT 正準）

本バックアップ・復元システムは、以下の原則に従って設計・運用する。

- 自動で「戻らない」  
  （復元・ロールバックは必ず人が判断し、レビューしてから行う）

- 成果物は最小限にする  
  （diff / metadata / 中間生成物を正準にしない）

- 正は一つだけ持つ  
  （保存先・命名規則・復元手順を複数用意しない）

- GPTに推測させない  
  （外部ルート・除外対象・参照禁止領域を明文化する）

この原則に反する仕組みは、便利であっても採用しない。

## 2. 正準の保存先（固定）

すべてリポジトリ外に保存する。

- backup_root: E:\btc_ts\backup

推奨構造（正準）：
E:\btc_ts\backup\
  ├─ git_bundle\        # フルバックアップ（git bundle）
  ├─ rp_tags\           # rp-* タグ一覧の書き出し（監査/確認用）
  └─ handoff_ctx\       # CTX-*.zip（引き継ぎZIPの退避）

※ E:\btc_ts 自体は運用データや設定の外部ルートであり、Git管理対象ではない。
   Gitバックアップは「リポジトリ（C:\BtcTradeSystem）」の再現を目的とする。

## 3. 構成ファイル（リポ内）

- scripts/git/git_rp_make.ps1
  - rp-YYYYMMDD_HHmmss タグを打つ（必要時のみコミット）
- scripts/git/git_rp_list.ps1
  - rp-* タグの一覧表示（運用確認）
- scripts/git/git_restore_from_bundle.ps1
  - bundle から復元（クローン/展開）
- scripts/git/git_rp_restore.ps1
  - rp タグへ戻す（※危険操作。手動レビュー前提）
- scripts/handoff/make_handoff.ps1
  - CTX-*.zip（GPT用引き継ぎZIP）を生成する

補足：
- scripts/git/git_full_backup.ps1 をフルバックアップ（bundle作成）の正準スクリプトとする。
  （bundle作成の手動ワンライナーは、非常時の代替手段としてのみ掲載する）
  
## 4. Restore Point（RP）運用ルール（タグ）

### 4.1 命名規則（固定）
- rp-YYYYMMDD_HHmmss

### 4.2 原則
- 自動コミット禁止（必要時のみ明示的に commit）
- rpタグは「復元ポイントの印」であり、差分ZIPやdiff.patch等の生成を正準としない

### 4.3 実行例
- タグのみ
  pwsh .\scripts\git\git_rp_make.ps1

- コミットしてからタグ（節目のみ）
  pwsh .\scripts\git\git_rp_make.ps1 -Commit -RpMemo "milestone: collector stabilize"

## 5. フルバックアップ（git bundle）運用（正準）

### 5.1 目的
- リモート不要で「リポジトリ全体」をアーカイブする
- 重大障害・移行・PC入替でも復元できる

### 5.2 出力
- 出力先：E:\btc_ts\backup\git_bundle\
- 成果物：
  - <name>.bundle（必須・これのみを正とする）

### 5.3 実行（例）
- 正準スクリプト（将来）：git_full_backup.ps1
  pwsh .\scripts\git\git_full_backup.ps1 -OutDir "E:\btc_ts\backup\git_bundle" -Name "BtcTS-next-main-20260108_1120"

- スクリプトが無い場合の手動正準（ワンライナー）
  $name="BtcTS-next-main-$(Get-Date -Format yyyyMMdd_HHmmss)"
  $out="E:\btc_ts\backup\git_bundle\$name.bundle"
  git bundle create $out --all
  git bundle verify $out

## 6. 復元手順（正準）

### 6.1 bundle から復元（推奨）
1) 新規フォルダへ clone
   git clone "<bundle_path>" "<dest_dir>"
2) ブランチ確認
   cd <dest_dir>
   git checkout main
3) 起動前チェック（最低限）
   git status -sb

### 6.2 rp タグへ戻す（危険：必ずレビュー）
原則：
- 先に git diff / git status を見て、戻す必要性を確認
- 可能なら worktree で検証してから適用

例（手動レビューの流れ）：
1) 現状退避（ブランチを切る等）
2) rpタグへ移動
   git reset --hard rp-YYYYMMDD_HHmmss
3) 起動確認

※ 自動ロールバック（無確認で戻す仕組み）は作らない。

※※ rp タグ復元は「作業を巻き戻す行為」であり、
   不具合修正や試行錯誤の代替手段として常用しない。

## 7. 外部ルートの扱い（GPT迷子防止の核）

### 7.1 外部ルート（正準）
- E:\btc_ts\ は運用外部ルート（config/data/logs/secrets 等）

### 7.2 repo_structure.yaml への反映ポリシー
- リポ構造（C:\BtcTradeSystem 配下）は自動抽出して常に正とする
- 外部ルート（E:\btc_ts）は「任意で付録として」同梱する
  - secrets は常に除外
  - 巨大フォルダ（dataset等）も除外
  - ツリーは “概要” のみ（深掘りしない）

### 7.3 自動生成の要件
- tools/make_repo_map_extract.py に --extra-root を追加し、
  repo_structure.yaml に external_roots セクションを出力できること
  （手書き [EXT_TREE] は廃止）

## 8. 更新履歴
- 2026-01-08: NEXT 正準 草案（保存先E:\btc_ts\backup固定 / diff成果物廃止）
- 2026-01-09: 本仕様をもって Git バックアップ・復元システムを完成とする
