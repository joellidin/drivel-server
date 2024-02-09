"""Server module."""

import io
import os
from typing import Literal, Self

from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.responses import Response
from google.cloud import texttospeech as tts
from openai import AsyncOpenAI
from openai.types.audio import Transcription
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice
from pydantic import BaseModel, ValidationInfo, field_validator, model_validator

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

app = FastAPI()


def get_openai_api_key(
    api_key_file: str | os.PathLike = "/run/secrets/openai-key",
) -> str:
    """
    Reading the OpenAI API key from file.

    Defaults to read from secret mounted in 'run/secrets` from the docker-compose setup.
    """
    with open(api_key_file, "r") as f:
        return f.read().strip()


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
        at least one user message.
        """
        assert (
            v[0].get("role") == "system"
        ), f"{info.field_name} must start with a system message"
        assert any(
            message.get("role") == "user" for message in v
        ), f"{info.field_name} must contain at least one user message"
        return v


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"Hello": "World"}


@app.post("/generate-response/", response_model=list[Choice])
async def generate_response(params: OpenAIParameters) -> list[Choice]:
    """
    Forwards the conversation to the OpenAI API and retrieves a generated response.

    This endpoint accepts a POST request with a JSON body compliant with the
    `OpenAIParameters` model, which includes a list of conversation messages and other
    parameters for the OpenAI completion API. The endpoint processes this data to
    interact with the specified OpenAI GPT model and returns the model's response as a
    string.

    The response is encapsulated in a dictionary with the key 'response'. In the event
    of an API failure or absence of a response, an HTTP exception with an appropriate
    status code will be raised.

    For the structure of the input and further details on the parameters, refer to the
    `OpenAIParameters` model.
    """
    try:
        openai_api_key = get_openai_api_key()
        client = AsyncOpenAI(api_key=openai_api_key)
        # Call the OpenAI API with the messages
        chat_completion = await client.chat.completions.create(
            **params.model_dump(exclude_none=True)
        )
        assert isinstance(chat_completion, ChatCompletion)
        # Return the text part of the OpenAI API response
        return chat_completion.choices
    except Exception as e:
        # Handle errors and exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


@app.post("/speech-to-text/", response_model=Transcription)
async def speech_to_text(audio_file: UploadFile) -> Transcription:
    """
    Process an audio file and return its speech-to-text transcription.

    This function takes an uploaded audio file sends it to the OpenAI Whisper
    and returns the transcription object.
    """
    try:
        openai_api_key = get_openai_api_key()
        client = AsyncOpenAI(api_key=openai_api_key)
        audio = await audio_file.read()
        buffer = io.BytesIO(audio)
        buffer.name = audio_file.filename
        return await client.audio.transcriptions.create(
            file=buffer, model="whisper-1", language="es"
        )
    except Exception as e:
        # Handle errors and exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e


class TTSParameters(BaseModel):
    """
    Represents the parameters for configuring a Text-to-Speech (TTS) request.

    ### Fields:
    - **text**: The input text string to be converted into speech. This field
        is required and must be provided by the user.

    - **language_code**: Specifies the BCP-47 language code that indicates the
        language of the input text and the accent of the synthesized speech.

    - **name**: The name of the voice model to be used for the TTS conversion.
        This field allows for customization of the voice model.
    """

    text: str
    language_code: str = "es-ES"
    name: str = "es-ES-Standard-B"

    @model_validator(mode="after")
    def check_voice_name(self) -> Self:
        """
        Validate the TTS voice name.

        It checks that messages start with a system message and that the list contains
        at least one user message.
        """
        assert self.name.startswith(self.language_code), (
            f"name '{self.name}' does not start with language_code"
            f" '{self.language_code}'"
        )
        return self


SERVICE_ACCOUNT_KEY_FILE = "/run/secrets/google-service-account-key"


@app.post("/text-to-speech/", response_model=None)
async def text_to_speech(params: TTSParameters) -> Response:
    """Process a text message and return its text-to-speech result."""
    try:
        async with tts.TextToSpeechAsyncClient.from_service_account_file(
            filename=SERVICE_ACCOUNT_KEY_FILE
        ) as client:
            # Set the text input to be synthesized
            synthesis_input = tts.SynthesisInput(text=params.text)

            # Build the voice request, select the language code and voice
            voice = tts.VoiceSelectionParams(
                language_code=params.language_code, name=params.name
            )

            # Select the type of audio file you want returned
            audio_config = tts.AudioConfig(audio_encoding=tts.AudioEncoding.MP3)

            # Perform the text-to-speech request on the text input with the selected
            # voice parameters and audio file type
            response = await client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )
            return Response(content=response.audio_content, media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
