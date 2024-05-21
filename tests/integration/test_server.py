"""Test server endpoints."""

from typing import get_args

from fastapi.testclient import TestClient
from openai import types

from drivel_server.core.config import settings
from drivel_server.main import app
from tests.integration.conftest import ChatInput

HEADERS = {"accept": "application/json", "Content-Type": "application/json"}


def test_root() -> None:
    with TestClient(app) as client:
        response = client.get(settings.API_V1_STR)
        assert response.status_code == 200
        assert response.json() == {"Hello": "World"}


def test_chat_200_response(chat_default_input: ChatInput) -> None:
    with TestClient(app) as client:
        response = client.post(
            f"{settings.API_V1_STR}/chat-responses",
            headers=HEADERS,
            json=chat_default_input,
            timeout=10,
        )
        assert response.status_code == 200
        assert "2" in response.json()[0]["message"]["content"]


def test_chat_invalid_model(chat_default_input: ChatInput) -> None:
    data = chat_default_input.copy()
    data["model"] = "invalid_model"
    with TestClient(app) as client:
        response = client.post(
            f"{settings.API_V1_STR}/chat-responses",
            headers=HEADERS,
            json=data,
            timeout=10,
        )
        assert response.status_code == 422
        models = ", ".join(f"'{model}'" for model in get_args(types.ChatModel))
        # Replace last comma with 'or'
        error_message = "Input should be " + " or".join(f"{models}".rsplit(",", 1))
        assert response.json()["detail"][0]["msg"] == error_message


def test_tts() -> None:
    # This is the data payload as required by the text-to-speech API.
    data = {
        "text": "Hola, que tal?",
        "language_code": "es-ES",
        "name": "es-ES-Standard-B",
    }

    with TestClient(app) as client:
        response = client.post(
            f"{settings.API_V1_STR}/text-to-speech/",
            headers=HEADERS,
            json=data,
            timeout=10,
        )
        assert response.status_code == 200


def test_stt() -> None:
    audio_file_path = "tests/data/audio/me_gusta_aprender_idiomas.mp3"
    headers = {"accept": "application/json"}
    with open(audio_file_path, "rb") as file, TestClient(app) as client:
        response = client.post(
            f"{settings.API_V1_STR}/speech-to-text/",
            headers=headers,
            files={"audio_file": (audio_file_path, file, "audio/mpeg")},
            timeout=10,
        )

        assert response.status_code == 200
