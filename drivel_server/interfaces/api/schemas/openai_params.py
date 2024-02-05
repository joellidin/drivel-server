"""Specify the schema for request parameters sent to the OpenAI API."""
from typing import Literal

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, ValidationInfo, field_validator

MODELS = Literal[
    "gpt-4-0125-preview",
    "gpt-4-turbo-preview",
    "gpt-4-1106-preview",
    "gpt-4-vision-preview",
    "gpt-4",
    "gpt-4-0314",
    "gpt-4-0613",
    "gpt-4-32k",
    "gpt-4-32k-0314",
    "gpt-4-32k-0613",
    "gpt-3.5-turbo",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-16k-0613",
]


class OpenAIParameters(BaseModel):
    """
    Parameters to forward to the openAI API.

    ### Fields:
    - **messages**: A list of messages comprising the conversation so far. Only accepts
        system, user and assistant messages.

    - **model**: ID of the model to use. See the
        [model endpoint compatibility](https://platform.openai.com/docs/models/model-endpoint-compatibility)
        table for details on which models work with the Chat API.

    - **max_tokens**: The maximum number of tokens that can be generated in the chat
        completion.
        The total length of input tokens and generated tokens is limited by the
        model's context length.

        [Example Python code](https://cookbook.openai.com/examples/how_to_count_tokens_with_tiktoken)
        for counting tokens.

    - **n**: How many chat completion choices to generate for each input message. Note
        that you will be charged based on the number of generated tokens across all
        of the choices. Keep `n` as `1` to minimize costs.
    """

    messages: list[ChatCompletionMessageParam]
    model: MODELS = "gpt-3.5-turbo"
    max_tokens: int = 150
    n: int = 1
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "messages": [
                        {"content": "You are a helpful assistant.", "role": "system"},
                        {"content": "What is 1 + 1?", "role": "user"},
                    ],
                    "model": "gpt-3.5-turbo",
                    "max_tokens": 150,
                    "n": 1,
                }
            ]
        }
    }

    @field_validator("messages")
    @classmethod
    def check_messages(
        cls, v: list[ChatCompletionMessageParam], info: ValidationInfo
    ) -> list[ChatCompletionMessageParam]:
        """
        Validate the input messages.

        It checks that messages start with a system message and that the list contains
        at least on user message.
        """
        assert (
            v[0].get("role") == "system"
        ), f"{info.field_name} must start with a system message"
        assert any(
            message.get("role") == "user" for message in v
        ), f"{info.field_name} must contain at least one user message"
        return v
