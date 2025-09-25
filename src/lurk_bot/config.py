"""Configuration helpers for environment-driven settings."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(slots=True)
class Settings:
    """Container for runtime configuration values."""

    discord_token: str
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    system_directives: tuple[str, ...] = ()
    max_context_turns: int = 6
    temperature: float = 0.8

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables."""

        discord_token = os.environ.get("DISCORD_TOKEN")
        if not discord_token:
            raise RuntimeError("DISCORD_TOKEN environment variable is required")

        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not openai_api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is required")

        model = os.environ.get("OPENAI_MODEL", cls.openai_model)
        max_turns_str = os.environ.get("MAX_CONTEXT_TURNS")
        temperature_str = os.environ.get("OPENAI_TEMPERATURE")
        extra = tuple(
            directive.strip()
            for directive in os.environ.get("SYSTEM_DIRECTIVES", "").split("||")
            if directive.strip()
        )

        max_turns = cls.max_context_turns
        if max_turns_str:
            try:
                max_turns = max(1, int(max_turns_str))
            except ValueError as exc:
                raise RuntimeError("MAX_CONTEXT_TURNS must be an integer") from exc

        temperature = cls.temperature
        if temperature_str:
            try:
                temperature = float(temperature_str)
            except ValueError as exc:
                raise RuntimeError("OPENAI_TEMPERATURE must be a float") from exc

        return cls(
            discord_token=discord_token,
            openai_api_key=openai_api_key,
            openai_model=model,
            system_directives=extra,
            max_context_turns=max_turns,
            temperature=temperature,
        )


__all__ = ["Settings"]
