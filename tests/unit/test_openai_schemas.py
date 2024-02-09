from openai.types.chat import (
    ChatCompletionMessageParam,
    ChatCompletionSystemMessageParam,
    ChatCompletionUserMessageParam,
)
from pydantic import ValidationError
import pytest

from drivel_server.schemas.chatgpt import OpenAIParameters


# Test for valid input
def test_openai_parameters_valid() -> None:
    valid_input = {
        "messages": [
            ChatCompletionSystemMessageParam(
                {"content": "Initial system message", "role": "system"}
            ),
            ChatCompletionUserMessageParam(
                {"content": "What's the weather like?", "role": "user"}
            ),
        ],
        "model": "gpt-3.5-turbo",
        "max_tokens": 150,
        "n": 1,
    }
    params = OpenAIParameters(**valid_input)
    assert params.messages[0]["role"] == "system"
    assert any(msg["role"] == "user" for msg in params.messages)


# Test for invalid input: First message is not a system message
def test_openai_parameters_invalid_first_message() -> None:
    invalid_messages: list[ChatCompletionMessageParam] = [
        ChatCompletionUserMessageParam(
            {"content": "User message first, which is invalid", "role": "user"}
        )
    ]

    with pytest.raises(ValidationError):
        OpenAIParameters(messages=invalid_messages)


# Test for invalid input: No user message
def test_openai_parameters_no_user_message() -> None:
    invalid_messages: list[ChatCompletionMessageParam] = [
        ChatCompletionSystemMessageParam(
            {"content": "System message first", "role": "system"}
        ),
        ChatCompletionSystemMessageParam(
            {
                "content": "Another system message, still no user message",
                "role": "system",
            }
        ),
    ]
    with pytest.raises(ValidationError):
        OpenAIParameters(messages=invalid_messages)


# Test default values
def test_openai_parameters_default_values() -> None:
    valid_messages = [
        ChatCompletionSystemMessageParam(
            {"content": "Initial system message", "role": "system"}
        ),
        ChatCompletionUserMessageParam({"content": "User's message", "role": "user"}),
    ]
    params = OpenAIParameters(messages=valid_messages)
    assert params.model == "gpt-3.5-turbo"
    assert params.max_tokens == 150
    assert params.n == 1


# Test incorrect field types
def test_openai_parameters_incorrect_types() -> None:
    incorrect_input = {
        "messages": "This should be a list, not a string",
        "model": 123,  # should be a string
        "max_tokens": "should be an integer",
        "n": "also should be an integer",
    }
    with pytest.raises(ValidationError):
        OpenAIParameters(**incorrect_input)
