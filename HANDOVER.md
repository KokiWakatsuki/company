# virtual-company 引き継ぎ資料

> Claude Code への作業依頼書。このファイルをプロジェクトルートに置き、
> Claude Code を起動したら「HANDOVER.md を読んで実装を開始してください」と伝える。

---

## プロジェクト概要

Discordを観測窓として、複数のAIエージェント（CEO・CTO・Programmerなど）が
自律的に会話・タスク分解・実装を行う「仮想会社」システムを構築する。

ユーザーはDiscordの `#general` チャンネルに依頼を投稿するだけでよい。
あとはエージェントたちが自律的に動き、会話ログがDiscordの各チャンネルに流れてくる。

---

## ユーザーの要件

### 必須要件
- ユーザーの介入は「最初の依頼」と「実装開始前の承認」のみ
- エージェント間の橋渡しは完全自動
- 各エージェントの会話がDiscordの対応チャンネルに自動投稿される
- 成果物（コード）は `workspace/` 以下にエージェントが自律的にリポジトリを作成・管理する
- GitHub操作は `gh` コマンド（GitHub CLI）を使う

### 制約
- 追加課金ゼロ（Anthropic TeamプランのUsage消費のみ）
- サーバーはローカルPC上で動作（常時稼働は不要）
- Anthropic APIキーは不要（Claude Agent SDKがClaude Codeのログイン状態を使う）

---

## 環境方針

| 環境 | ツール | 用途 |
|---|---|---|
| 開発環境 | Nix Flakes + direnv | Esslens/ で管理・cd で自動起動 |
| 本番環境 | Docker（docker compose） | デプロイ・本番稼働 |

### 重要：Nix の管理単位

```
Esslens/              ← flake.nix はここだけ（会社システム全体の環境）
├── flake.nix         ← python, gh, git, nodejs 等をすべてここで管理
├── flake.lock
├── .envrc            ← "use flake" の1行だけ。cd で自動的に nix develop が走る
├── .gitignore        ← company/ workspace/ .direnv/ を除外
├── company/          ← flake.nix 不要。Esslens の環境をそのまま使う
└── workspace/
    ├── todo-app/     ← プロジェクト固有の flake.nix を持つ（技術スタックが異なるため）
    └── chat-app/     ← 同上
```

**company/ に flake.nix は作らない。** Esslens の環境（python, gh 等）をそのまま使う。

**workspace/ 以下の各プロジェクトは自前の flake.nix を持つ。** Programmer エージェントが
プロジェクトの技術スタック（Next.js, Rust, etc.）に合わせて作成する。

### Esslens/flake.nix に含めるパッケージ

```nix
{
  description = "Esslens development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = nixpkgs.legacyPackages.${system}; in {
        devShells.default = pkgs.mkShell {
          packages = [
            pkgs.python312
            pkgs.python312Packages.pip
            pkgs.gh        # GitHub CLI（エージェントがリポジトリ作成に使う）
            pkgs.git
            pkgs.nodejs_20 # Claude Agent SDK（Node.js製）
          ];
        };
      });
}
```

### Esslens/.envrc

```bash
use flake
```

これだけ。`cd Esslens/` した瞬間に自動で `nix develop` 相当の環境に入る。

### company/ の Dockerfile（本番用）

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "orchestrator/main.py"]
```

---

## システム構成


```
ユーザー（Discord #general に投稿）
    ↓
Orchestrator（main.py）
    ├── CEOエージェントを起動
    │     ↓ ASSIGN: CTO などを出力
    ├── CTOエージェントを起動
    │     ↓ ASSIGN: Programmer などを出力
    ├── Programmerエージェントを起動（workspace/以下で作業）
    │     ↓ gh repo create → コード実装 → git push
    └── 各エージェントの返答をDiscordの対応チャンネルに自動投稿

Human Gate: HUMAN_GATE: を検知したらDiscordに確認メッセージを投稿し、
            ユーザーの返答（OK/はい）を待ってから処理を再開する。
```

---

## リポジトリ構成

GitHubアカウント上の構成：

```
github.com/あなた/
├── Esslens        ← 親リポジトリ（Claude Codeはここで起動）
├── company        ← 独立したリポジトリ（仮想会社システム本体）
├── todo-app       ← エージェントが自動作成（例）
└── chat-app       ← エージェントが自動作成（例）
```

ローカルのディレクトリ構成：

```
Esslens/                        ← git管理（.gitignore で company/ と workspace/ を除外）
├── .gitignore                  ← company/ と workspace/ を除外済み
├── company/                    ← 独立したgitリポジトリ（このディレクトリ）
│   ├── HANDOVER.md             ← このファイル
│   ├── Makefile                ← 未作成
│   ├── .env                    ← 未作成（DISCORD_BOT_TOKEN のみ必要）
│   ├── requirements.txt        ← 未作成
│   ├── personas/               ← 各人物の人格定義（作成済み）
│   │   ├── ceo.md
│   │   ├── cto.md
│   │   ├── programmer.md
│   │   ├── reviewer.md
│   │   ├── tester.md
│   │   ├── secretary.md
│   │   └── researcher.md
│   └── orchestrator/           ← 一部作成済み・要完成
│       ├── main.py             ← 未作成（最重要）
│       ├── agent_runner.py     ← 作成済み（要レビュー）
│       ├── human_gate.py       ← 作成済み（要レビュー）
│       └── memory.py           ← 未作成
└── workspace/                  ← .gitignoreで除外・エージェントが成果物を作る場所
    └── （エージェントが自動でリポジトリを作成）
```

---

## エージェント間通信プロトコル

各エージェントはテキストでこのフォーマットを出力する。
Orchestrator がこのキーワードを検知して次のアクションを決定する。

```
# 別のエージェントへのタスク割り振り
ASSIGN: <役職名>
TASK: <タスクの内容>
CONTEXT: <背景・目的>
DIR: <作業ディレクトリ（Programmerのときのみ）>

# ユーザーへの確認（実装開始前に必ず使う）
HUMAN_GATE: <確認したい内容>
PLAN:
- <計画項目1>
- <計画項目2>

# 報告
REPORT: <報告内容>
REPO: <GitHubリポジトリURL（作成した場合）>
```

役職名の対応:
- `CEO` / `CTO` / `Programmer` / `Reviewer` / `Tester` / `Secretary` / `Researcher`

---

## Discordチャンネル構成

以下のチャンネルを事前に作成しておく（Orchestratorが自動投稿する）:

| チャンネル名 | 用途 |
|---|---|
| `#general` | ユーザーの依頼 / Human Gate の確認メッセージ |
| `#ceo-log` | CEOの発言ログ |
| `#cto-log` | CTOの発言ログ |
| `#dev-log` | Programmer / Reviewer / Testerの発言ログ |
| `#secretary-log` | 秘書・リサーチャーの発言ログ |

---

## 実装すべきファイル一覧

### 1. `orchestrator/main.py`（最重要・最初に作る）

Discord Bot のメインファイル。以下を実装する:

```python
# 担当: discord.py を使ったBot
# - #general のメッセージを受信
# - human_gate が待機中のときはユーザーの返答を human_gate.receive_response() に渡す
# - それ以外は agent_runner.run_agent("CEO", message) を呼び出す
# - エージェントの返答を parse_response() で解析
# - ASSIGN: を検知したら対応するエージェントを再帰的に起動
# - HUMAN_GATE: を検知したら human_gate.ask() を呼び出して一時停止
# - 各エージェントの返答を対応するDiscordチャンネルに投稿

ROLE_TO_CHANNEL = {
    "CEO": "ceo-log",
    "CTO": "cto-log",
    "Programmer": "dev-log",
    "Reviewer": "dev-log",
    "Tester": "dev-log",
    "Secretary": "secretary-log",
    "Researcher": "secretary-log",
}
```

### 2. `orchestrator/memory.py`

SQLiteで会話履歴を保存する。

```python
# - conversations テーブル: id, role, message, response, timestamp, project_id
# - プロジェクトIDでグルーピング（1タスク = 1プロジェクト）
# - get_context(project_id) で会話履歴を文字列で返す
```

### 3. `requirements.txt`

```
discord.py>=2.3.0
claude-agent-sdk
python-dotenv
aiosqlite
```

### 4. `.env.example`

```
DISCORD_BOT_TOKEN=your_token_here
```

### 5. `Makefile`

```makefile
start:
    python orchestrator/main.py

install:
    pip install -r requirements.txt
```

---

## agent_runner.py の注意点（作成済みだが要確認）

`ClaudeAgentOptions` に `cwd` パラメータが存在するか確認すること。
存在しない場合は `os.chdir()` で代替するか、別の方法を調べること。

---

## workspace のパス設計

`workspace/` は `Esslens/workspace/` に配置される。
`company/` からの相対パスは `../workspace/` になる。
Programmerがプロジェクトを作成するときのパス計算：

```python
# company/orchestrator/ から見た workspace の場所
WORKSPACE_DIR = Path(__file__).parent.parent.parent / "workspace"
# 展開例: /Users/xxx/Esslens/workspace/

# プロジェクト作成時
project_dir = WORKSPACE_DIR / f"{task_id}-{task_slug}"
# 展開例: /Users/xxx/Esslens/workspace/20250414-todo-app/
```

`workspace/` は `Esslens/.gitignore` で除外されているため、
各プロジェクトリポジトリ（`gh repo create` で作成）は独立して管理される。

---

## 実装の優先順位

1. `orchestrator/main.py` の骨格（Discord接続 + CEOへの転送のみ）
2. `orchestrator/memory.py`
3. `requirements.txt` と `.env.example`
4. `Makefile`
5. CEOだけで動作確認（CTO以下はまだ繋がなくてよい）
6. CTO → Programmer の連鎖を追加
7. Human Gate の動作確認
8. 残りの役職（Reviewer, Tester, Secretary, Researcher）を追加

---

## 動作確認の手順（実装完了後）

```bash
# 1. 依存インストール
make install

# 2. .env を作成してDISCORD_BOT_TOKENを設定

# 3. 起動
make start

# 4. Discordの #general に投稿
# 「簡単なToDoアプリのAPIを作ってください」

# 5. #ceo-log に CEOの返答が流れることを確認
# 6. Human Gate の確認メッセージが #general に来ることを確認
# 7. OK と返答して処理が再開することを確認
```

---

## 参考リンク

- Claude Agent SDK: https://github.com/anthropics/claude-agent-sdk-python
- discord.py: https://discordpy.readthedocs.io/
- GitHub CLI: https://cli.github.com/
