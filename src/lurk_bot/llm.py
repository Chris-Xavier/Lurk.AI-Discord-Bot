"""Wrapper around the OpenAI chat completion API."""

from __future__ import annotations

from typing import Iterable, Sequence

import openai

from .persona import build_system_message
from .memory import RoleContentPair


class ChatModel:
    """A minimal wrapper for invoking OpenAI's chat completion endpoint."""

    def __init__(self, *, api_key: str, model: str, temperature: float, system_directives: Sequence[str] | None = None) -> None:
        openai.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.system_message = build_system_message(list(system_directives or []))

    async def generate_reply(self, history: Iterable[RoleContentPair], user_message: str) -> str:
        """Produce a chat completion from the provided context."""

        messages = [{"role": "system", "content": self.system_message}]
        messages.extend({"role": role, "content": content} for role, content in history)
        messages.append({"role": "user", "content": user_message})

        response = await openai.ChatCompletion.acreate(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
        )
        return response.choices[0].message["content"].strip()


__all__ = ["ChatModel"]
