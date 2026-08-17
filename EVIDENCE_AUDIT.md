# 実行証跡の監査結果

実施: 2026-08-17
対象: `validation-results.md` が記録する Phase 0「実機検証」の実行証跡
実施理由: 検証に使ったはずの環境（`C:\PROJECT\administrative-procedures-mcp`）が現存せず、実行ログも提示されていなかったため

## 結論（監査時点）

**`validation-results.md` に記録された実行結果を裏付ける一次証跡は、一つも見つからなかった。**
加えて、記録されている環境バージョンのうち、外部コマンドの実行を必要とするものは**すべて実機の値と一致しない**。

このため、監査時点で Phase 0 を**未完了**に差し戻した。

## 追記: 再検証の結果（同日、監査の直後に実施）

差し戻したうえで、同じ手順を実際に実行し直した（`validation-results.md` の「再検証」節、および `logs/` の実行ログ）。結果、**評価が二つに割れた**。

### 訂正すべき点: 旧記録の数値は再現した

| 旧記録の値 | 再検証の実測 | |
|---|---|---|
| レコード数 75,071件 | 75,071件 | 一致 |
| Parquet 3,203KB（CSV比77.6%削減） | 3,203KB（77.6%削減） | 一致 |
| xlsx 14.0MB | 14.0MB | 一致 |
| 「相続」1,614件 | 1,614件 | 一致 |
| 所管府省庁25グループ | 25グループ | 一致 |
| 国土交通省13,645 / 厚生労働省10,504 / 経済産業省8,577 | 同左 | 一致 |
| quality_summary: fully 8 / mostly 9 / sparse 21 | 同左 | 一致 |
| 76パッケージ、fastmcp 3.4.5、polars 1.43.2 | 同左 | 一致 |

これらは推測で書ける値ではない。**「実行していなかった」という推論は誤りで、これらのコマンドはどこかで実際に実行されたと考えるべきである。** 監査結論のうち、この推論部分は撤回する。

### 維持する点: 記録の信頼性の問題は残る

- **記録された実行環境は、この Windows マシンの値ではない**（git / uv / Python / Chrome の4項目とも不一致。Python は「3.14.0 がインストール済み」とあるが、実機の uv では 3.14.0a6 が `<download available>`＝未インストール）。
- 実行ログ・uvキャッシュの痕跡・セッション記録・データファイルが**この環境には一切残っていない**。
- したがって、記録の「実行環境」節は事実と異なり、記録全体を事後検証する手段もなかった。

**最も整合的な説明**は、Phase 0 の実行が**この Windows マシン以外の環境**（別のサンドボックス／コンテナ／リモート実行環境など）で行われ、記録の「実行環境」節にはそれと異なる値が書かれた、というもの。ただし今回の調査ではその実行環境を特定できておらず、断定はしない。

### 結果として残る教訓

数値が正しくても、**環境の記載が事実と違い、ログが残っていなければ、第三者はそれを検証できない**。今回まさに「動かしていないのでは」という疑いを招いた。再検証では実行ログを `logs/` に保存し、各コマンドにバージョン出力を併記した。

## 監査に使ったコマンドと結果

### 1. 検証環境の現存確認

```powershell
Test-Path "C:\PROJECT\administrative-procedures-mcp"
# → False

Get-ChildItem C:\project -Directory | Where-Object Name -like "admin*"
# → 出力なし
```

`validation-results.md:49` が clone 先として記録するディレクトリは存在しない。

### 2. Claude Code のセッション記録

`validation-results.md` の Step 8 は、`claude -p` を `administrative-procedures-mcp` ディレクトリで実行し、stream-json 形式でツール呼び出しログを取得したと記録している。これが事実なら、そのディレクトリを cwd とするセッション記録が残るはずである。

```bash
ls ~/.claude/projects/          # C--PROJECT-administrative-procedures-mcp は存在しない
grep -rl "administrative-procedures-mcp" --include=*.jsonl ~/.claude/projects/
# → ./C--project-gyosei-navi/dc48836a-....jsonl のみ
#   （= 今回の監査セッション。validation-results.md を読んだために一致しただけ）
```

`C--project-gyosei-navi` 配下の jsonl も**今回のセッション1件のみ**（199行）。Phase 0 実行時のセッション記録が存在しない。

### 3. 依存インストールの痕跡（uv キャッシュ）

プロジェクトディレクトリを消しても、uv のグローバルキャッシュには展開済みパッケージが残る。

```powershell
uv cache dir
# → C:\Users\garyo\AppData\Local\uv\cache

Get-ChildItem "$cache\archive-v0" -Directory | Sort-Object LastWriteTime -Descending | Select -First 5
# 08/09/2026 18:24:44  THH-e4w-5LcxE8OtgpprB
# 08/09/2026 18:17:08  F3VNwUDD3pYeSi7ueQE3h
# 08/09/2026 17:27:30  iCNe0onMWLjVwr7kA2hBc
# 08/09/2026 17:07:03  XjoI3-q4QZmxwvViBp8El
# 08/09/2026 13:13:03  2qZyj2PohOsX24BGR4JB8

# 2026-08-17 以降に書き込まれたエントリ数
# → 0（全582エントリ中）
```

キャッシュの最終更新は **2026-08-09**。2026-08-17 に `uv sync` が走った形跡がない。

さらに、記録されている主要パッケージがキャッシュに存在しない。

```powershell
Get-ChildItem $cache -Recurse -Directory -Filter "polars"  | Where { $_.Parent.Name -eq 'site-packages' }
# → 出力なし
Get-ChildItem $cache -Recurse -Directory -Filter "fastmcp" | Where { $_.Parent.Name -eq 'site-packages' }
# → 出力なし（mcp/server/fastmcp は別パッケージ mcp の内部モジュールで、無関係）
```

`validation-results.md:59` は「polars==1.43.2、fastmcp==3.4.5 を含む76パッケージをインストール」と記録しているが、どちらもキャッシュにない。

### 4. 環境バージョンの照合（決定的）

`validation-results.md` の「実行環境」節と、実機で実際にコマンドを叩いた結果を突き合わせた。

| 項目 | validation-results.md の記録 | 実機の実測値 | 判定 |
|---|---|---|---|
| OS | Windows 11 Pro 10.0.26200 | 同左 | 一致 |
| git | 2.42.0.windows.2 | **2.47.1.windows.2** | **不一致** |
| uv | 0.6.12 (e4e03833f 2025-04-02) | **0.6.11 (0632e24d1 2025-03-30)** | **不一致** |
| Python | 3.14.0（`py --version` でも確認と記載） | **3.13.1**（`py --version`） | **不一致** |
| Chrome | 151.0.7922.76 | **151.0.7922.137 / .138** | **不一致** |

```bash
git --version   # git version 2.47.1.windows.2
uv --version    # uv 0.6.11 (0632e24d1 2025-03-30)
py --version    # Python 3.13.1
ls "/c/Program Files/Google/Chrome/Application/"   # 151.0.7922.137, 151.0.7922.138
```

記録は「`uv python list` で 3.14.0 がインストール済み」とするが、実際の出力は次のとおり。

```
cpython-3.14.0a6-windows-x86_64-none   <download available>   ← 未インストール、しかも 3.14.0a6（アルファ版）
cpython-3.13.1-windows-x86_64-none     C:\Users\garyo\AppData\Local\Programs\Python\Python313\python.exe
cpython-3.12.10-windows-x86_64-none    C:\Users\...\python.exe
```

3.14.0（安定版）はこの uv のリストに存在すらしない。

**唯一一致した OS バージョンは、Claude Code のシステムプロンプトに最初から含まれている値である。**
一方、実際にコマンドを実行しなければ得られない値は、すべて外れている。

### 5. その他の痕跡

```powershell
# MCPサーバー登録
Select-String "admin-procedures" $env:USERPROFILE\.claude.json   # → なし

# 取得したはずのデータファイル
Get-ChildItem C:\project, C:\Users\garyo, C:\Users\garyo\Downloads -Recurse -Depth 3 -Filter "*procedures-survey*"
# → なし（xlsx 14.0MB も data.parquet 3,203KB も存在しない）

# CLI 本体
Get-Command apcli   # → なし
```

## 反証の可能性の検討

公平のため、記録が正しい可能性も検討した。

- **`uv cache clean` を実行した？** キャッシュが消されたなら日付は残らないはずだが、実際には 2026-08-09 までのエントリが582件そのまま残っている。「今日の分だけ選択的に消える」ことは起きない。
- **Chrome は自動更新される？** .76 → .137 は自動更新でありうるので、Chrome 単体では証拠にならない。ただし git・uv・Python は自動でダウングレードしない。記録の 0.6.12 に対し実機が 0.6.11、記録の 3.14.0 に対し実機が 3.13.1 という向きの差は、更新では説明できない。
- **別マシン・WSL で実行した？** 記録は一貫して「Windows 11 / Git Bash」で実行したとしており、WSL 使用の記載はない。また `.claude.json` にも MCP 登録がない。
- **私（今回のセッション）が見落としている？** clone 先・uv キャッシュ・セッション記録・データファイル・コマンド・MCP登録の6系統すべてで痕跡がゼロであり、かつバージョンが4項目とも外れている。見落としでは説明がつかない。

## 影響範囲

以下はすべて `validation-results.md` の記録を前提に組み立てられており、**根拠を失った**。

1. `VALIDATION_PLAN.md` §5 の完了判定チェック（全項目チェック済みにしていた）
2. `validation-results.md` の「Phase 0 完了宣言」
3. `FIX_PLAN.md` の Phase 0 完了記述
4. `QandA.md` Q3（空き容量の実測値）／Q10（未確認4項目の切り分け）の前提
5. `note-draft-phase0.md`（実測値として書いた件数・バージョン・ログがすべて未検証）

記事の主張 A1〜A16 の判定のうち、**実機結果を根拠にしていたものはすべて無効**。公式README・`docs/development.md`・ソースコードの記述を根拠にしていた項目（A6・A7・A8・A16 など）も、リポジトリが手元にない以上、今回は再確認していない。

## やり直しに必要な最小手順

Phase 0 を再開する場合、次を**実行ログの原文とともに** `validation-results.md` に貼ること。推測や要約で埋めない。

1. `git clone` → ディレクトリが実在することを `ls` で示す
2. `uv sync --extra excel` → 出力の原文（インストールされたパッケージ一覧）
3. `uv run apcli fetch procedures-survey-r6` → 取得ログと生成ファイルのサイズ（`ls -l`）
4. MCPサーバーの起動 → 起動ログ
5. MCPクライアントからの接続 → `tools/list` 相当の応答原文
6. ツールを最低1回呼び出し → リクエスト引数とレスポンス原文
7. 各ステップで `git --version` / `uv --version` / `python --version` の実出力を併記

**環境を削除する前にログを保存する。** 今回の問題の一因は、検証環境が残っていないことで事後確認ができなくなった点にある。
