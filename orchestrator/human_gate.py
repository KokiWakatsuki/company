"""
human_gate.py
エージェントが HUMAN_GATE: を出力したとき、
Discordにメッセージを投稿してユーザーの返答を待つ。
"""

import asyncio
from typing import Callable


class HumanGate:
    """
    ユーザーへの確認待ち状態を管理する。
    Discordにメッセージを投稿し、ユーザーが返答するまで処理を一時停止する。
    """

    def __init__(self, send_func: Callable):
        """
        Args:
            send_func: Discordにメッセージを送る非同期関数
                       signature: async def send(channel: str, message: str)
        """
        self.send = send_func
        self._pending: asyncio.Event | None = None
        self._user_response: str = ""

    async def ask(self, question: str, plan: str) -> str:
        """
        ユーザーに確認を求め、返答が来るまで待つ。

        Args:
            question: 確認内容
            plan: 計画の概要
        Returns:
            ユーザーの返答テキスト
        """
        self._pending = asyncio.Event()
        self._user_response = ""

        # Discordの #general に確認メッセージを投稿
        msg = (
            f"⚠️ **確認が必要です**\n\n"
            f"**{question}**\n\n"
            f"{plan}\n\n"
            f"続けてよければ `OK` または `はい`、"
            f"修正が必要であれば内容を入力してください。"
        )
        await self.send("general", msg)

        # ユーザーの返答を待つ（タイムアウトなし）
        await self._pending.wait()
        return self._user_response

    def receive_response(self, text: str):
        """
        Discordからユーザーの返答を受け取ったときに呼ぶ。
        """
        if self._pending and not self._pending.is_set():
            self._user_response = text
            self._pending.set()

    @property
    def is_waiting(self) -> bool:
        """現在ユーザーの返答待ち状態かどうか"""
        return self._pending is not None and not self._pending.is_set()
