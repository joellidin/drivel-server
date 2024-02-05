"""Handle direct interactions with the OpenAI API."""

from typing import Any

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice


class OpenAIClient:
    def __init__(self) -> None:
        self.client = AsyncOpenAI()

    async def generate_response(self, params: dict[str, Any]) -> list[Choice]:
        """Encapsulate interaction with the OpenAI API for generating chat responses."""
        chat_completion = await self.client.chat.completions.create(**params)
        assert isinstance(chat_completion, ChatCompletion)
        return chat_completion.choices
