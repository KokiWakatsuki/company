"""
agent_runner.py
各エージェントを起動する薄いラッパー。
personas/*.md を読み込んでシステムプロンプトとして使う。
"""

import asyncio
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock

PERSONAS_DIR = Path(__file__).parent.parent / "personas"

# 役職ごとのツール設定
AGENT_TOOLS = {
    "CEO":        [],                                      # 会話のみ
    "CTO":        [],                                      # 会話のみ
    "Programmer": ["Bash", "Read", "Write", "Edit"],       # コード実装あり
    "Reviewer":   ["Read", "Bash"],                        # コード読み込みあり
    "Tester":     ["Bash", "Read"],                        # テスト実行あり
    "Secretary":  ["Read", "Write"],                       # ドキュメント作成
    "Researcher": ["Bash"],                                # Web調査あり
}

# 役職ごとのパーミッションモード
AGENT_PERMISSION = {
    "CEO":        "default",
    "CTO":        "default",
    "Programmer": "acceptEdits",   # ファイル書き込みは自動承認
    "Reviewer":   "default",
    "Tester":     "acceptEdits",
    "Secretary":  "acceptEdits",
    "Researcher": "default",
}


def load_persona(role: str) -> str:
    """personas/<role>.md を読み込んでシステムプロンプトとして返す"""
    persona_file = PERSONAS_DIR / f"{role.lower()}.md"
    if not persona_file.exists():
        raise FileNotFoundError(f"Persona file not found: {persona_file}")
    return persona_file.read_text(encoding="utf-8")


async def run_agent(
    role: str,
    message: str,
    cwd: str | None = None,
    context: str | None = None,
) -> str:
    """
    指定した役職のエージェントを起動してメッセージを送り、返答を返す。

    Args:
        role: 役職名 (CEO, CTO, Programmer, ...)
        message: 送るメッセージ
        cwd: 作業ディレクトリ（Programmerなど実装系に使用）
        context: 追加コンテキスト（会話履歴など）
    Returns:
        エージェントの返答テキスト
    """
    persona = load_persona(role)
    full_message = message
    if context:
        full_message = f"【これまでの経緯】\n{context}\n\n【依頼】\n{message}"

    options = ClaudeAgentOptions(
        system_prompt=persona,
        allowed_tools=AGENT_TOOLS.get(role, []),
        permission_mode=AGENT_PERMISSION.get(role, "default"),
        cwd=cwd,
    )

    result_parts = []
    async for msg in query(prompt=full_message, options=options):
        if isinstance(msg, AssistantMessage):
            for block in msg.content:
                if isinstance(block, TextBlock):
                    result_parts.append(block.text)

    return "\n".join(result_parts)
