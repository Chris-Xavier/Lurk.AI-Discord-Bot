"""In-memory conversation history for the Discord bot."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Deque, Dict, Iterable, List, Tuple


RoleContentPair = Tuple[str, str]


@dataclass
class ConversationMemory:
    """Stores the rolling conversation history per channel.

    The memory keeps a fixed number of message pairs (user + assistant)
    so the prompt remains within the model's context window.
    """

    max_turns: int = 6

    def __post_init__(self) -> None:
        self._history: Dict[int, Deque[RoleContentPair]] = defaultdict(deque)

    def append_exchange(self, channel_id: int, user: str, assistant: str) -> None:
        """Add a new user/assistant pair to the conversation history."""

        history = self._history[channel_id]
        history.append(("user", user))
        history.append(("assistant", assistant))

        # Trim the history to the most recent ``max_turns`` user+assistant pairs.
        while len(history) > self.max_turns * 2:
            history.popleft()
            history.popleft()

    def append_user_only(self, channel_id: int, user: str) -> None:
        """Add a user message when we have not yet responded."""

        self._history[channel_id].append(("user", user))
        while len(self._history[channel_id]) > self.max_turns * 2:
            self._history[channel_id].popleft()

    def append_assistant_only(self, channel_id: int, assistant: str) -> None:
        """Add an assistant message when seeded from outside the bot."""

        self._history[channel_id].append(("assistant", assistant))
        while len(self._history[channel_id]) > self.max_turns * 2:
            self._history[channel_id].popleft()

    def clear(self, channel_id: int) -> None:
        """Remove the stored history for a given channel."""

        self._history.pop(channel_id, None)

    def iter_history(self, channel_id: int) -> Iterable[RoleContentPair]:
        """Yield the history for the given channel in chronological order."""

        return list(self._history.get(channel_id, ()))


__all__: List[str] = ["ConversationMemory", "RoleContentPair"]
