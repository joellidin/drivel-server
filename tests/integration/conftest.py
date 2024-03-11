from typing import NotRequired, TypedDict

import pytest


class ChatInput(TypedDict):
    messages: list[dict]
    model: NotRequired[str]


@pytest.fixture()
def chat_default_input() -> ChatInput:
    return {
        "messages": [
            {"content": "You are a helpful assistant.", "role": "system"},
            {"content": "What is 1 + 1?", "role": "user"},
        ]
    }
