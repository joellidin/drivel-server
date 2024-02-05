"""Encapsulate business logic for pre- and post-interaction with the OpenAI API."""

from openai.types.chat.chat_completion import Choice

from drivel_server.adapters.api_clients.openai_client import OpenAIClient
from drivel_server.interfaces.api.schemas.openai_params import OpenAIParameters


class OpenAIInteraction:
    def __init__(self) -> None:
        self.client = OpenAIClient()

    async def execute(self, params: OpenAIParameters) -> list[Choice]:
        """Process input, interact with OpenAI API, and return processed results."""
        # Pre-process params if necessary
        processed_params = params.model_dump(exclude_none=True)

        # Interact with OpenAI API
        try:
            return await self.client.generate_response(processed_params)
        except Exception as e:
            # Handle or re-raise exceptions as needed
            raise e
