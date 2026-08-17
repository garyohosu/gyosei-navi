# Phase 0 検証記録

このファイルはWORK_INSTRUCTION.mdに従って記録する。秘密情報・APIキー・個人情報・勤務先の実データ／社内情報は記載しない。

## 実行環境

- 実行日時: 2026-08-17
- OS: Windows 11 Pro 10.0.26200
- git: 2.42.0.windows.2
- Python: `uv python list` で 3.14.0 がインストール済み（`py --version` でも3.14.0を確認）。uvが3.10〜3.14系を管理可能な状態で、公式要件（Python 3.10+）を満たす。
- uv: 0.6.12 (e4e03833f 2025-04-02)
- Chrome: 151.0.7922.76（Prompt API要件のChrome 138+を満たす）
- C:ドライブ空き容量: 約44GB（十分）

## innovaTopia記事側の主張一覧（記事本文から抽出、公式READMEの記載で補完していない）

記事: 「デジタル庁、行政手続7万5000件を分析するMCPサーバを公開｜MITライセンスの検証用サンプル」（innovaTopia、2026-08-15 17:15、著者: 山本達也）
https://innovatopia.jp/ai/ai-news/116042/

| # | 記事の主張 | 公式READMEの記載（今回確認済み） | 実機結果 | 判定 | 備考 |
|---|---|---|---|---|---|
| A1 | 約7万5000件の行政手続データを対象 | 「行政手続等の棚卸調査結果（約75,000件）」と一致する記載あり | 75,071件（`apcli fetch` 変換ログ） | 一致 | 2026-08-17 実測 |
| A2 | Parquet変換後、約3MBのファイルサイズ | README本文に具体的サイズの記載なし（未確認） | 3,203KB（約3.1MB） | 一致 | 2026-08-17 実測。CSV比77.6%削減 |
| A3 | LLMには検索・集計条件の指定のみ担わせ、集計処理はサーバー側で実行する構成 | 「サーバー側で集計を完結」「AIに生データを渡して計算させることによる誤りを防ぐ」と一致 | MCP経由の `summarize_records` 結果（`total_group_count: 25`）がStep 4のCLI直接実行結果（同25グループ、国土交通省13,645件で一致）と完全に一致。LLMは条件（group_by/metrics）を指定しただけで、生データはLLMに渡らず同一の決定論的集計ロジックが動いたことを示す。加えて、LLMが誤った形式で集計を要求した際はサーバー側の型検証で明確に拒否された（Pydantic validation error）ことも確認 | 一致 | 2026-08-17 MCP接続実測。主根拠はCLIとMCPの集計結果一致、検証エラーは補強証拠 |
| A4 | MCP Apps対応クライアントで円グラフや表を表示可能 | 「MCP Apps対応...チャットUI内にグラフや表を直接表示できる」と一致（円グラフの明記は確認できず） | 今回の `claude -p`（テキスト出力モード）ではUI描画は評価対象外 | 未検証 | MCP Apps UIの表示確認は対話的なClaude Desktop/Code UIでの目視確認が必要 |
| A5 | dataset.yamlに項目の意味・コード値・欠損の扱い・指標の計算方法を定義 | 「データ定義（dataset.yaml）による意味の明示」と一致 | 未検証 | 未検証 | Step 5でdataset.yaml本体を確認する |
| A6 | SDMXの考え方を参考にした軽量な定義ファイル | README本文に明記なし | `docs/development.md:16` に「SDMX/DSD（Data Structure Definition）の考え方を参考に、メタデータ駆動の構成を採用」と明記 | 一致 | 2026-08-17 docs実測 |
| A7 | 照合処理は完全一致・Unicode正規化・近似一致の3段階 | 「表記揺れの正規化・類似名の近似一致」の記載あり | `src/admin_procedures/models.py:74` に「正確一致 → 正規化一致（NFKC）→ 類似文字列一致（difflib, cutoff 0.85）の順でフォールバック検索する」と明記。3段階・Unicode正規化とも一致 | 一致 | 2026-08-17 コード実測 |
| A8 | 近似一致は項目名のみに適用し、データの値には適用しない | `resolved_fields` はフィールド名の自動補正に関する記載で、値への適用は言及なし | フィールド名解決（`_fuzzy_get`）にのみ正規化・近似一致を適用。`where`フィルタの値照合は `response.py:1102` で「IN（完全一致のいずれか）」と明記され、値には近似一致を使わない | 一致 | 2026-08-17 コード実測 |
| A9 | 調査項目によりフェーズ1が2024-10-01、フェーズ2が2024-03-31と基準日が分かれる | README本文に明記なし | dataset.yamlに「フェーズ2調査項目」タグはあるが具体的な基準日の記載は見つからず | 対象外 | MCP実装の検証対象ではなく調査そのものの方法論に関する主張のため、Phase 0（実装の再現確認）のスコープ外と判断。原資料（デジタル庁配布ページ）側の記述の話であり、実装コード・dataset.yamlを読んでも真偽は判断できない |
| A10 | 数値は原則有効数字2桁以上の概数、試算困難な場合は1桁 | README本文に明記なし | dataset.yaml notesに「有効数字2桁以上の概数」「有効数字1〜2桁程度の概数」と明記 | 一致 | 2026-08-17 dataset.yaml実測 |
| A11 | 必要なのはPython 3.10以上 | 「Python 3.10+」バッジと一致 | 確認済み | 一致 | 手元環境はuv管理下で3.10〜3.14系が利用可能 |
| A12 | スクリプト1本のセットアップで動作 | 「git clone → cd → ./setup.sh」の3行構成、setup.shが依存インストール・データ取得・接続案内までを行うと記載 | Git Bash上で `./setup.sh --yes --skip-data` を実行し、依存インストール〜接続案内まで単一スクリプトでエラーなく完走した | 一致 | 2026-08-17 実測。Windowsでもsetup.sh単体で完結する |
| A13 | ツールの実行は手元の環境内で完結 | 「ローカルまたは単一利用者向けの実験用サンプル」「既定で127.0.0.1のみにバインド」と一致 | `apcli preview` は127.0.0.1のみにバインド（curlで確認）。`.mcp.json` はstdioでローカルサブプロセスを起動するのみ。`apcli fetch` の唯一の外部送信先はデジタル庁配布ページ（digital.go.jp）で、それ以外の通信は確認されなかった | 一致 | 2026-08-17 これまでの実測から総合判断 |
| A14 | ライセンスはMIT | 「MIT License」バッジ・LICENSEファイル記載と一致 | 確認済み | 一致 | GitHub上のライセンス表示でも確認済み |
| A15 | 技術検証を目的としたサンプルコードで、保守は保証しない | 「本実装は技術検証を目的としたサンプルコードです」「動作の安定性や継続的な保守を保証するものではありません」と一致 | 確認済み | 一致 | 免責事項セクションで確認 |
| A16 | 外部からの機能追加や仕様変更は原則として受け付けない | README本文に明記なし | `docs/development.md:541` に「原則として、外部からの機能追加、仕様変更、リファクタリング等のコントリビューションは受け付けていません」と明記 | 一致 | 2026-08-17 docs実測 |

判定の凡例: 確認済み＝READMEまたは記事以外の一次情報で裏取り済み／一致＝記事とREADME等一次情報が一致／未検証＝実機検証待ち。

## WORK_INSTRUCTION.md記載の10照合項目との対応

WORK_INSTRUCTION.mdのQ8確定時に列挙した10項目は、記事本文精読前の暫定リストだった。実際に記事を精読した結果、上記A1〜A16が記事本文に基づく実際の主張であり、10項目のうち複数はA1・A3・A5・A11・A14などと対応する一方、10項目の一部（MCP経由の自然言語検索、apcli単体でのLLMなし検索、apcli preview、Chrome内蔵AI、Windows対応）は記事本文よりも公式READMEに由来する説明である可能性が高い。実機検証・完了判定では、A1〜A16（記事本文由来）とWORK_INSTRUCTION.mdの10項目（README由来を含む）を区別して扱う。

## 進捗ログ

### 2026-08-17 事前レビュー（Q1）

- `git clone https://github.com/digital-go-jp/administrative-procedures-mcp.git` を実行し、`C:\PROJECT\administrative-procedures-mcp` に取得（ダウンロードのみ、未実行）。
- `.mcp.json` を確認: `{"mcpServers": {"admin-procedures": {"command": "uv", "args": ["run", "--extra", "excel", "python", "-m", "admin_procedures"]}}}`。stdioでMCPサーバーを起動する内容のみで、不審な処理なし。
- `setup.sh` を全文確認: ユーザー同意プロンプト（`--yes`省略時は各ステップで確認）、`uv sync --extra excel`（uvなければvenv+pip）、`apcli fetch procedures-survey-r6`（デジタル庁配布ページから取得）、接続方法の案内のみ。マシン設定変更は`.venv/`追加のみと明記されており、外部送信先は配布ページ以外に見当たらない。
- `src/` 配下をPythonファイル限定で `os.system` / `subprocess.*` / `eval` / `exec` / `urllib.request` / `requests.*` / `httpx.*` をgrepし目視確認。`subprocess.run` は `apcli install` コマンドが `fastmcp.cli install` を呼ぶ用途のみ（ユーザーが明示的に実行した場合のみ発火）、`urllib.request` はデータ取得時のリダイレクト禁止ハンドラ付き実装、`eval(` はPolarsの `.list.eval()` メソッドで文字列評価ではない。不審な処理は見つからなかった。
- 判定: 実行前レビュー完了。setup.shの内容を確認した上で、Windows/Git Bash環境での実行安定性を優先しWORK_INSTRUCTION.md記載の手動コマンド（`uv sync --extra excel` → `uv run apcli fetch procedures-survey-r6`）で進める。

### 2026-08-17 Step 3: セットアップ実施

- 環境: Windows 11 / Git Bash / uv 0.6.12 / Python 3.14.0（uvが自動選択・管理）
- 実行: `uv run apcli fetch procedures-survey-r6`（3行前の `uv sync --extra excel` で仮想環境作成済み）
- 結果: 成功。85パッケージ解決、76パッケージインストール（fastmcp==3.4.5、polars==1.43.2 等）。`FutureWarning`（`pl.read_excel` のArrow変換仕様変更に関する警告）が1件出たが致命的エラーではない。
- データ取得結果:
  - 取得元: `https://www.digital.go.jp/resources/procedures-survey-results`
  - 取得ファイル: `20250729_procedures-survey-results_outline_02.xlsx`（14.0MB）
  - 変換後: `datasets/procedures-survey-r6/data.parquet`（3203KB、CSV比77.6%削減）
  - レコード数: **75,071件**、フィールド数: 38（定義済み38に一致）
- 記事の主張との照合:
  - A1（約7万5000件）→ 実機75,071件で **一致**
  - A2（Parquet変換後 約3MB）→ 実機3,203KB（約3.1MB）で **一致**
- Windows固有の問題: なし（Git Bash経由でsetup.shを使わず手動コマンドのみで完了。venvのactivateも不要、`uv run` で一貫して実行できた）
- 追加確認（記事の主張A12「スクリプト1本のセットアップ」の実機確認）: `PYTHONIOENCODING=utf-8 ./setup.sh --yes --skip-data` をGit Bash上で実行し、依存インストール（`uv sync`相当）〜接続方法の案内までを単一スクリプトでエラーなく完走した。`--skip-data` は既に取得済みのデータを再ダウンロードしないためのオプション。Claude Code / Claude Desktopの検出メッセージも正しく表示された。Windows（Git Bash）でも `setup.sh` 単体でセットアップが完結することを確認した。

### 2026-08-17 Step 4: LLMなしでCLIを確認

- **Windows固有の詰まりどころを発見**: `uv run apcli list` / `inspect` の日本語部分が文字化けした（コンソールのコードページ932＝Shift-JISでUTF-8出力を解釈しているため）。`chcp 65001` は本ツールのパイプ経由実行では効果がなかったが、`PYTHONIOENCODING=utf-8` を環境変数として付けることで解決した。以降のコマンドはすべて `PYTHONIOENCODING=utf-8 uv run apcli ...` の形式で実行する。
- `uv run apcli list` → `procedures-survey-r6`（行政手続等の棚卸調査結果、デジタル庁、75,071件、schema_version 1）が一覧に表示された。
- `uv run apcli inspect procedures-survey-r6` → 38列のスキーマ、各列の役割（id/dim/attr/measure）、型、充填率（fill_rate）、コードリスト、computed measures（オンライン化率）、quality_summary（fully_populated 8 / mostly_populated 9 / sparse 21）を確認できた。
- `uv run apcli query procedures-survey-r6 -q 相続 --limit 5` → 日本語全文検索が動作し、`"total": 1614` 件がヒット。`--limit 5` で結果が5件に制限され、`next_cursor` によるページネーションも確認できた。再実行して `total: 1614` が同一であることを確認（再現性あり）。
- `uv run apcli summarize procedures-survey-r6 -g 所管府省庁 -m count` → 25グループに集計。上位は国土交通省13,645、厚生労働省10,504、経済産業省8,577。再実行して同じ結果（国土交通省13,645）を確認（再現性あり）。
- 応答には `provenance`（`dataset_title`, `published_at: 2025-07-24`, `fetched_at: 2026-08-17`, `source_url`, `publisher`）が付与されており、出典情報が結果に含まれることを確認した。
- `総手続件数` 等のmeasureフィールドの `desc` に「件数は原則有効数字2桁以上、一部試算値を含む」との記載があり、記事の主張A10（有効数字2桁以上の概数、試算困難な場合は1桁）と部分的に一致（「1桁」の明記はinspect出力中には見当たらず、未確認のまま）。
- 集計・検索の実行主体: レスポンスはJSON構造化データであり、LLMの手計算ではなくサーバー側（CLIプロセス内のPolarsクエリ）で処理されていることを確認した。
- 参考（Phase 0の範囲外の気づき）: `手続が行われるイベント(個人)` フィールドには「妊娠、出生・こども、引越し、就職・転職、結婚・離婚、医療・健康、税金、年金の受給、死亡・相続」等のライフイベント分類が既に含まれている。gyosei-naviが想定する人生イベント検索（引っ越し・結婚・出産・相続・退職）と概ね対応しており、Phase 1検討時の参考情報として記録しておく。

### 2026-08-17 Step 5: dataset.yaml の設計を確認

- ファイル: `datasets/procedures-survey-r6/dataset.yaml`（YAML、38フィールド定義、id_field=`手続ID`、source.url/asset_pattern/csv_header_rows等を記載）
- フィールドの意味・型・表示名: 各フィールドに `role`（id/dim/attr/measure）、`desc`、`csv_col_index`、`name` があり、必要に応じ `codelist`（コード値説明付き）や `multi_value` を付与。人が読んで意味が分かる自然文で記述されている。
- コード値: 例えば「手続類型」「手続主体」等は選択肢ごとに定義文が付き、単なるコード⇔ラベル対応ではなく制度上の意味まで記載されている。
- NULL・欠損の扱い: 「オンライン手続件数」フィールドに `notes: null（欠損）は「件数不明」を意味する。0 は基本的に「オンライン手続なし」だが、地方等で件数集計が困難な一部の手続では 0 と記録されている場合がある。` と明記。0と欠損が意味的に異なることが定義レベルで示されている。
- computed measures: `computed_measures` セクションに `オンライン率`（`mode: count_where`、`condition_field: オンライン化の実施状況`、`condition_values: [1 実施済]`）が定義されており、apcli inspect結果の `formula` 表示と対応することを確認した。
- 記事の主張A10（数値は原則有効数字2桁以上の概数、試算困難な場合は1桁）との照合: 「総手続件数」に `件数は有効数字2桁以上の概数であり、一部試算値を含む`、「オンライン手続件数」「非オンライン手続件数」に `件数は有効数字1〜2桁程度の概数であり、一部試算値を含む` との記載があり、**一致**（1桁の記載も確認できた）。
- 記事の主張A9（フェーズ1が2024-10-01、フェーズ2が2024-03-31）: dataset.yaml内には「フェーズ2調査項目」というタグ付けは複数フィールドにあるが、フェーズ1／フェーズ2それぞれの基準日を示す具体的な日付は今回確認した範囲（dataset.yaml、README、docs/）では見つからなかった。`docs/dataset-yaml-guide.md` にはyaml記法の例として `as_of_date: '2024-03-31'` が出てくるが、これは記法サンプルでありprocedures-survey-r6自体のas_of_dateではない。**未確認**のまま（原資料や配布ページ側の説明を要確認）。
- provenance/notes/quality_summary: Step 4の `apcli summarize` 応答に `provenance`（`published_at: 2025-07-24`, `fetched_at`, `source_url`, `publisher`）が付与されることを確認済み。`apcli inspect` 応答には `quality_summary`（fully_populated/mostly_populated/sparse の件数集計）が含まれることも確認済み。

### 2026-08-17 Step 6: MCPの4ツールを確認

`uv run apcli describe <tool>` で4ツールすべての定義を取得できた（LLM/MCP接続なしでツール定義だけを検査できる）。

- `list_datasets`: 引数 `q`（キーワード検索）、`publisher`（発行者フィルタ）。必須引数なし。
- `inspect_dataset`: 引数 `dataset_id`（必須）。
- `query_records`: 引数 `dataset_id`（必須）、`q`、`search_fields`、`select`、`where`（部分一致/IN/`$gte`/`$lte`/`$ne`/`$not_contains`/`$not_empty`）、`order_by`、`limit`（1-5000、既定50）、`cursor`。
- `summarize_records`: 引数 `dataset_id`（必須）、`metrics`（既定 `["count"]`、count/sum:field/avg:field/min:field/max:field）、`group_by`、`where`、`having`、`explode`（multi_value展開）、`limit`（既定200、上限10,000）。
- 4ツールとも `apcli` 経由でLLMなしに個別検査でき、Step 4で実際に `query`/`summarize` を実行した結果が上記のパラメータ定義と一致することを確認した。出典情報（`provenance`）はStep 4で確認済み。
- MCP仕様バージョン（`/health`）の確認は保留: 今回の検証はstdio前提のCLI経由のみで、HTTPモード（`ADMIN_PROCEDURES_PORT=... python -m admin_procedures`）は今回起動していない。Step 8（Claude Code接続）で別途確認するか、HTTPモードを別途起動して確認するかは未実施。

### 2026-08-17 Step 7: apcli preview とAPIキーなし利用を確認

- 実行: `uv run apcli preview --no-open`（バックグラウンド起動）
- 起動ログ: `MCP Apps プレビューホスト: http://127.0.0.1:8765/`（README記載の既定URLと一致）
- `curl http://127.0.0.1:8765/` → HTTP 200、`<title>apcli</title>` のHTMLを確認。既定で `127.0.0.1` のみにバインドされている（README記載どおり）。
- Chromeのヘッドレスモード（`chrome --headless --screenshot`, Chrome 151.0.7922.76）でスクリーンショットを取得し、以下を確認した。
  - UI自体は起動し、日本語で正しく表示される（「データセットを選択してください…」「データについて質問してください」等、文字化けなし）
  - `list_datasets` ツールがUI上に表示される
  - 画面右上に「内蔵AI を確認中…」と表示されたまま停止しており、**ヘッドレスモードではChrome内蔵AI（Prompt API / Gemini Nano）が有効化されなかった**
- 判定: UIの起動・データセット探索用の骨組みは自動確認できたが、Chrome内蔵AIの実際の利用可否・自然言語操作・単純/複雑クエリの差は、モデルダウンロードやフラグ有効化を伴う可能性があり、対話的な（ヘッドレスでない）Chromeでの手動確認が必要。今回は未確認のまま。
- 検証後、プレビューサーバーは停止した（PowerShellでリスナーを確認しプロセスをStop-Process）。

### 2026-08-17 Step 8: Claude Code等からMCP接続を確認

事前レビュー済みの `.mcp.json`（`uv run --extra excel python -m admin_procedures` をstdioで起動）を使い、`administrative-procedures-mcp` ディレクトリで非対話モード（`claude -p`）のClaude Codeセッションを実行して接続確認した。MCP関連ツール以外は使わせない意図で `--allowedTools` に4ツールのみを指定した。

**質問1「厚生労働省が所管する行政手続を検索して」**
- 結果: 厚生労働省所管の行政手続 **10,504件**（データセット全体75,071件中）と回答。冒頭の該当例（介護保険関連の手続）を表形式で提示。
- 回答文末尾に出典（`dataset_id: procedures-survey-r6`、`source_url`）と「本データは政府の公式見解ではありません。件数フィールドは概数・試算値を含みます。」という注意書きが自動的に付与された。
- num_turns: 6、total_cost_usd: 約0.38ドル。permission_denials: なし。

**質問2「所管府省庁別に手続件数を集計して」（stream-json形式で詳細ログを取得）**
- 呼び出されたツールと引数を実際に確認できた:
  1. `mcp__admin-procedures__list_datasets` `{}`
  2. `mcp__admin-procedures__inspect_dataset` `{"dataset_id": "procedures-survey-r6"}`
  3. `mcp__admin-procedures__summarize_records` `{"dataset_id": "procedures-survey-r6", "group_by": ["所管府省庁"], "metrics": [{"field": "総手続件数", "agg": "sum"}, {"field": "手続ID", "agg": "count"}]}` → **サーバー側でスキーマ検証エラー**（Pydanticの `3 validation errors`。`metrics` は文字列配列である必要があり、LLMが最初に生成したオブジェクト形式は拒否された）
  4. LLMが `ToolSearch` でツール定義を再確認した後、`mcp__admin-procedures__summarize_records` `{"dataset_id": "procedures-survey-r6", "group_by": ["所管府省庁"], "metrics": ["count", "sum:総手続件数"], "limit": 200}` で再実行 → 成功（`total_group_count: 25`）
- **記事の主張A3（LLMは検索・集計条件の指定のみ、集計処理はサーバー側で実行）の裏付け**: 主根拠は、MCP経由の最終結果 `total_group_count: 25` がStep 4のCLI実行結果（`uv run apcli summarize procedures-survey-r6 -g 所管府省庁 -m count` → 25グループ、国土交通省13,645件が最多）と完全に一致したこと。LLMはgroup_by/metricsという「条件」を指定しただけで、CLIと同一の決定論的集計ロジックが動いた証拠となる。補強証拠として、LLMが誤った形式で集計を要求した際にサーバー側の型検証で明確に拒否された（Pydantic validation error）ことも確認した——これはLLMが生データを手計算していない（できない）ことを示す傍証ではあるが、それ自体は「集計がサーバー側で実行される」ことの直接証明ではなく、あくまで補強材料として扱う。
- total_cost_usd: 約0.27ドル、num_turns: 7、permission_denials: なし。

**重要な注意点（意図と異なった挙動）**: `--allowedTools` にMCPの4ツールのみを指定したが、実際にはセッション冒頭で `Bash` ツール（`ls -la`）も実行されてしまい、Bashを含む他ツールへのアクセスを完全に遮断できなかった。この環境（現在の対話セッションの権限設定を引き継ぐ）では `--allowedTools` だけでは新規セッションを厳密にMCPツールのみへサンドボックスできないことが判明した。実行された内容自体は無害（ディレクトリ一覧のみ）だったが、今後同様の検証を行う場合は許可モード・権限設定も含めて別途検討が必要（次回への申し送り事項）。

**MCP仕様バージョン**: 上記のstdio接続では `/health` エンドポイントは存在しないため、応答中のMCP仕様バージョンは今回未確認のまま。必要であれば別途HTTPモードを起動して確認する。

### 2026-08-17 記事本文の補足確認（docs/development.md 参照）

Step 8完了後、A6・A7・A8・A16の裏取りのため `docs/development.md` および `src/admin_procedures/models.py` / `response.py` を確認した。

- A6（SDMXの考え方）: `docs/development.md:16` に「SDMX/DSD（Data Structure Definition）の考え方を参考に、メタデータ駆動の構成を採用しています」と明記。**一致**。
- A7（完全一致・Unicode正規化・近似一致の3段階）: `src/admin_procedures/models.py:74` の `_fuzzy_get` 関数に「正確一致 → 正規化一致 → 類似文字列一致の順でフォールバック検索する」とあり、正規化は `unicodedata.normalize("NFKC", ...)`、近似一致は `difflib.get_close_matches(..., cutoff=0.85)`。記事の「3段階」「Unicode正規化」の両方に**一致**。
- A8（近似一致は項目名のみ、データ値には適用しない）: `_fuzzy_get` はフィールド名・算出項目名の解決にのみ使用。`where` フィルタの値照合は `response.py:1102` で「IN（完全一致のいずれか）」と明記されており値には近似一致を使わない。**一致**。
- A16（外部コントリビューション原則不可）: `docs/development.md:541` に「原則として、外部からの機能追加、仕様変更、リファクタリング等のコントリビューションは受け付けていません」と明記。**一致**。

## Phase 0 進捗まとめ（2026-08-17時点）

### VALIDATION_PLAN.md §5 完了判定チェックリストとの対応

- [x] 公式リポジトリをcloneできた
- [x] セットアップできた（`uv sync --extra excel`、Windows/Git Bashで問題なし）
- [x] procedures-survey-r6を取得できた（75,071件、3,203KB）
- [x] apcli list が動いた
- [x] apcli inspect が動いた
- [x] apcli query で日本語検索できた（「相続」1,614件、再現性あり）
- [x] apcli summarize で集計できた（所管府省庁別25グループ、再現性あり）
- [x] dataset.yaml の設計を確認した（フィールド定義、NULL/欠損、コード値、computed measures、provenance/notes/quality_summary）
- [x] MCPの4ツールを確認した（`apcli describe` で入出力定義、Claude Code経由の実接続でも動作確認）
- [x] apcli preview を試した（UI起動・日本語表示は確認、ヘッドレスのため内蔵AI動作は未確認）
- [~] APIキーなしで使える範囲を確認した（UIとlist_datasets相当の探索は確認。Chrome内蔵AIでの実際の自然言語操作は対話的ブラウザでの手動確認が必要で未実施）
- [x] MCP対応AIから呼び出した（Claude Codeから2問実行し成功、ツール名・引数・サーバー側検証エラーまで記録）
- [x] 記事の説明と実機結果の一致・相違を整理した（A1〜A16のうちA1・A2・A3・A6・A7・A8・A10・A11・A12・A13・A14・A15・A16の13件は一致を確認。A9は調査方法論に関する主張でありPhase 0（MCP実装の検証）のスコープ外と判断。A4（グラフ表示）とChrome内蔵AIの実操作の2件は対話的なブラウザ確認が必要で未確認）

### 未確認のまま残っている項目（対話的なブラウザ操作が必要なもの）

1. **A4**: MCP Apps UIでの実際のグラフ・表表示（テキストのみの `claude -p` では評価できない。対話的なClaude Desktop/Codeでの目視確認が必要）
2. **Chrome内蔵AI（Prompt API/Gemini Nano）の実際の自然言語操作**: ヘッドレスモードでは「内蔵AIを確認中…」のまま停止。モデルダウンロード・フラグ有効化を伴う対話的なChromeでの手動確認が必要
3. **MCP仕様バージョン**（`/health` の `mcp_protocol_version`）: 今回はstdio接続のみで、HTTPモードを起動していないため未確認
4. **Windows固有の問題と回避策の網羅性**: 今回発見したのは文字化け（`PYTHONIOENCODING=utf-8` で解決）のみ。他の環境（別バージョンのWindows/Python等）での再現性は未検証

### スコープ外と判断した項目

- **A9**（フェーズ1が2024-10-01、フェーズ2が2024-03-31）: MCP実装の検証対象ではなく、デジタル庁の調査そのものの方法論に関する主張のため、Phase 0のスコープ外とした。原資料（配布ページ）側の記述の話であり、リポジトリのコード・dataset.yamlを読んでも真偽は判断できない。

### 停止条件の該当有無

VALIDATION_PLAN.md §6の停止条件（公式データ取得不可、データセット未認識、CLI検索・集計の再現不可、出典・品質情報の未確認、Windows固有問題が未解決）はいずれも**該当しない**。Phase 0は独自実装へ進むことを妨げる致命的な問題なく、ほぼ完了している。残るのは上記5項目の追加確認（主に対話的なブラウザ操作が必要なもの）。
