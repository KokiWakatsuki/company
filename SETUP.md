# あなたがやるべき作業手順

> Claude Codeに作業を渡す直前までの準備手順です。
> 上から順番に実行してください。所要時間：約30分。

---

## 全体の流れ

```
ステップ1-2:  GitHub にリポジトリを2つ作成（Esslens, company）
ステップ3-4:  ローカルに Esslens をクローン、company を submodule として追加
ステップ5:    このプロジェクトのファイルを company/ にコピー
ステップ6-8:  Discord Bot の作成・チャンネル作成・.env の設定
ステップ9-10: 必要なツールの確認
ステップ11:   Claude Code を起動して作業を渡す
```

---

## ステップ1：GitHub に「Esslens」リポジトリを作成する

1. https://github.com/new を開く
2. 以下の設定で作成する：
   - Repository name: `Esslens`
   - Visibility: `Private`
   - README, .gitignore, license：すべてチェックしない
3. 「Create repository」をクリック

---

## ステップ2：GitHub に「company」リポジトリを作成する

同様に https://github.com/new を開いて：
- Repository name: `company`
- Visibility: `Private`
- README等：チェックしない

---

## ステップ3：ローカルに Esslens をセットアップする

ターミナルを開いて実行：

```bash
# Esslens をクローン
git clone https://github.com/あなたのユーザー名/Esslens.git
cd Esslens

# .gitignore を作成（workspace/ を除外する）
echo "workspace/" > .gitignore

# workspace ディレクトリを作成
mkdir workspace

# コミット
git add .gitignore
git commit -m "initial: add .gitignore"
git push origin main
```

---

## ステップ4：company を submodule として追加する

Esslens ディレクトリ内で実行：

```bash
git submodule add https://github.com/あなたのユーザー名/company.git company

git add .gitmodules company
git commit -m "add company as submodule"
git push origin main
```

完了後の構造：

```
Esslens/
├── .gitignore      ← workspace/ を除外
├── .gitmodules     ← submodule 登録情報（自動生成）
├── company/        ← company リポジトリの中身
└── workspace/      ← Git管理外（エージェントの作業場所）
```

---

## ステップ5：このプロジェクトのファイルを company/ にコピーする

ダウンロードしたファイル一式を `Esslens/company/` 内にコピーする。

コピーするもの：
```
company/
├── HANDOVER.md
├── SETUP.md（このファイル）
├── personas/
│   ├── ceo.md
│   ├── cto.md
│   ├── programmer.md
│   ├── reviewer.md
│   ├── tester.md
│   ├── secretary.md
│   └── researcher.md
└── orchestrator/
    ├── agent_runner.py
    └── human_gate.py
```

コピー後、コミットする：

```bash
cd Esslens/company

git add .
git commit -m "initial: add personas and orchestrator skeleton"
git push origin main

# Esslens 側も submodule の参照を更新
cd ..
git add company
git commit -m "update company submodule"
git push origin main
```

---

## ステップ6：Discord Bot を作成する

### 6-1. アプリケーションを作成

1. https://discord.com/developers/applications を開く
2. 「New Application」→ 名前を `Esslens` にして「Create」

### 6-2. Bot を設定

1. 左メニュー「Bot」をクリック
2. 「Reset Token」でトークンを発行 → **必ずメモする（一度しか表示されない）**
3. 「Privileged Gateway Intents」で以下を ON にする：
   - `MESSAGE CONTENT INTENT`（必須）

### 6-3. Bot をサーバーに追加

1. 左メニュー「OAuth2」→「URL Generator」
2. `SCOPES` で `bot` にチェック
3. `BOT PERMISSIONS` で以下にチェック：
   - `Send Messages`
   - `Read Message History`
   - `View Channels`
4. 生成されたURLをブラウザで開く → 自分のサーバーを選択して「認証」

---

## ステップ7：Discord サーバーにチャンネルを作成する

以下の5つのチャンネルを作成する（名前は完全一致）：

| チャンネル名 | 用途 |
|---|---|
| `general` | あなたの依頼 / Human Gate の確認メッセージ |
| `ceo-log` | CEO の発言ログ |
| `cto-log` | CTO の発言ログ |
| `dev-log` | Programmer / Reviewer / Tester のログ |
| `secretary-log` | 秘書 / リサーチャーのログ |

---

## ステップ8：.env ファイルを作成する

`Esslens/company/` 内に `.env` を作成：

```bash
cd Esslens/company
```

テキストエディタで `.env` を新規作成し、以下を記入：

```
DISCORD_BOT_TOKEN=ステップ6-2でメモしたトークン
```

`.env` を `.gitignore` に追加してコミット：

```bash
echo ".env" >> .gitignore
git add .gitignore
git commit -m "add .env to gitignore"
git push origin main
```

---

## ステップ9：必要なツールを確認する

```bash
# Python 3.10 以上であること
python3 --version

# GitHub CLI（エージェントがリポジトリ作成に使う）
gh --version

# GitHub CLI にログインしているか確認
gh auth status
```

**インストールされていない場合：**

```bash
# Mac
brew install gh

# Windows
winget install GitHub.cli

# ログイン
gh auth login
```

---

## ステップ10：Claude Code を確認する

```bash
claude --version
```

インストールされていない場合：
```bash
npm install -g @anthropic-ai/claude-code
```

Teamプランのアカウントでログイン済みか確認：
```bash
claude  # 起動して /login でTeamプランのアカウントでログイン
```

---

## ステップ11：Claude Code を起動して作業を渡す

**必ず `Esslens/company/` で起動すること。**

```bash
cd Esslens/company
claude
```

起動したら以下をそのまま貼り付ける：

---

```
HANDOVER.md を読んで、virtual-company プロジェクトの実装を開始してください。

【プロジェクト構成の補足】
- このディレクトリ（company/）は Esslens/ の submodule です
- workspace は Esslens/workspace/ にあります（company/ からの相対パスは ../workspace/）
- workspace/ は Esslens の .gitignore で除外済みです
- エージェントが作成する各プロジェクトは workspace/ 以下に gh repo create で作成します

【実装の優先順位】
1. orchestrator/main.py の骨格（Discord接続 + CEOへの転送のみ）
2. orchestrator/memory.py
3. requirements.txt、.env.example、Makefile
4. CEO だけで動作確認できる最小構成を完成させる

【完了条件】
company/ ディレクトリで make install && make start を実行すると
Discord Bot が起動し、#general へのメッセージに CEO が返答する状態にしてください。
```

---

## 完了後の動作確認

```bash
make install
make start
```

Discord の `#general` に投稿：
```
簡単なToDoアプリのREST APIを作ってください
```

確認項目：
1. `#ceo-log` に CEO の返答が流れる
2. `#general` に「実装を開始してよいですか？」という確認が来る
3. `OK` と返答すると処理が再開される
4. 最終的に `Esslens/workspace/` 以下にプロジェクトが作成される
