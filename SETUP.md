# あなたがやるべき作業手順

> Claude Codeに作業を渡す直前までの準備手順です。
> 上から順番に実行してください。所要時間：約30分。

---

## 全体の流れ

```
ステップ1-2:  GitHub にリポジトリを2つ作成（Esslens, company）
ステップ3:    ローカルに Esslens をセットアップ（flake.nix・.envrc・.gitignore）
ステップ4:    company を Esslens 内にクローン
ステップ5:    このプロジェクトのファイルを company/ にコピー
ステップ6-8:  Discord Bot の作成・チャンネル作成・.env の設定
ステップ9:    Nix と direnv の確認
ステップ10:   Claude Code の確認
ステップ11:   Claude Code を起動して作業を渡す
```

---

## 最終的なディレクトリ構成

```
Esslens/                  ← VSCodeで開く・git管理・claude起動・nixで環境管理
├── flake.nix             ← 開発環境の設計図（python, gh, git, nodejs等）
├── flake.lock            ← バージョン固定
├── .envrc                ← cd Esslens/ で自動的に nix develop が走る
├── .gitignore            ← company/ workspace/ .direnv/ を除外
├── company/              ← 独立したgitリポジトリ（Esslensの環境をそのまま使う）
└── workspace/            ← git管理外（エージェントが成果物を作る場所）
    ├── todo-app/         ← 独立リポジトリ（専用の flake.nix を持つ）
    └── chat-app/         ← 独立リポジトリ（専用の flake.nix を持つ）
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

```bash
# Esslens をクローン
git clone https://github.com/あなたのユーザー名/Esslens.git
cd Esslens

# .gitignore を作成（company/ workspace/ .direnv/ を除外）
cat > .gitignore << 'EOF'
company/
workspace/
.direnv/
EOF

# workspace ディレクトリを作成
mkdir workspace

# direnv 用の .envrc を作成（これだけで cd 時に自動で nix develop が走る）
echo "use flake" > .envrc

# flake.nix を作成（仮想会社システムを動かすための環境）
cat > flake.nix << 'EOF'
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
            pkgs.gh
            pkgs.git
            pkgs.nodejs_20
          ];
        };
      });
}
EOF

# flake.lock を生成
nix flake lock

# コミット
git add .
git commit -m "initial: Nix environment setup"
git push origin main
```

---

## ステップ4：company を Esslens 内にクローンする

```bash
# Esslens/ 内で実行
git clone https://github.com/あなたのユーザー名/company.git company
```

これだけです。company/ は .gitignore で除外されているため、
Esslens のコミット管理には影響しません。

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

コピー後、company/ リポジトリにコミットする：

```bash
cd Esslens/company

git add .
git commit -m "initial: add personas and orchestrator skeleton"
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

`.env` を company の `.gitignore` に追加してコミット：

```bash
echo ".env" > .gitignore
git add .gitignore
git commit -m "add .gitignore"
git push origin main
```

---

## ステップ9：Nix と direnv を確認する

```bash
# Nix が入っているか確認
nix --version
```

**Nix がインストールされていない場合：**

```bash
curl --proto '=https' --tlsv1.2 -sSf -L https://install.determinate.systems/nix | sh -s -- install
# インストール後ターミナルを再起動
```

```bash
# direnv が入っているか確認
direnv --version
```

**direnv がインストールされていない場合：**

```bash
# Mac
brew install direnv

# direnv をシェルに追加（fish の場合）
echo 'direnv hook fish | source' >> ~/.config/fish/config.fish

# zsh の場合
echo 'eval "$(direnv hook zsh)"' >> ~/.zshrc
```

ターミナルを再起動後、Esslens/ に移動して direnv を許可：

```bash
cd Esslens
direnv allow
```

これで `cd Esslens/` するたびに自動で Nix 環境に入るようになります。

---

## ステップ10：Claude Code を確認する

Nix 環境に入った状態（`cd Esslens/` 後）で確認：

```bash
claude --version
```

インストールされていない場合：
```bash
npm install -g @anthropic-ai/claude-code
```

Team プランのアカウントでログイン済みか確認：
```bash
claude  # 起動して /login で Team プランのアカウントでログイン
```

---

## ステップ11：Claude Code を起動して作業を渡す

**必ず `Esslens/` で起動すること（Nix 環境が有効な状態で）。**

```bash
cd Esslens
claude
```

起動したら以下をそのまま貼り付ける：

---

```
company/HANDOVER.md を読んで、virtual-company プロジェクトの実装を開始してください。

【プロジェクト構成】
- 作業ディレクトリは Esslens/（ここで claude を起動している）
- 仮想会社のシステムコードは company/ にある
- エージェントが作成するプロジェクトは workspace/ 以下に置く
- workspace/ 以下の各プロジェクトは gh repo create で独立リポジトリとして作成する

【環境方針（必ず守ること）】
- 開発環境：Esslens/ の flake.nix で管理済み（python, gh, git, nodejs が使える）
- company/ には flake.nix を作らない（Esslens の環境をそのまま使う）
- company/ には Dockerfile と docker-compose.yml を作成する（本番用）
- workspace/ 以下の各プロジェクトには専用の flake.nix を作成する（技術スタックが異なるため）

【実装の優先順位】
1. company/orchestrator/main.py の骨格（Discord接続 + CEOへの転送のみ）
2. company/orchestrator/memory.py
3. company/requirements.txt・.env.example・Makefile
4. company/Dockerfile・docker-compose.yml
5. CEO だけで動作確認できる最小構成を完成させる

【完了条件】
cd Esslens/company && make install && make start を実行すると
Discord Bot が起動し、#general へのメッセージに CEO が返答する状態にしてください。
```

---

## 完了後の動作確認

```bash
cd Esslens/company
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
