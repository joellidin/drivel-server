"""Server module."""

import io
from typing import Literal

from fastapi import FastAPI, HTTPException, UploadFile, status
from fastapi.responses import Response
from openai import AsyncOpenAI
from openai.types.audio import Transcription
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice
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

app = FastAPI()


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
        client = AsyncOpenAI()
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
        client = AsyncOpenAI()
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
    """Parameters to the text-to-speech endpoint."""

    text: str


@app.post("/text-to-speech/", response_model=None)
async def text_to_speech(text: TTSParameters) -> Response:  # noqa: B008
    """Process a text message and return its text-to-speech result."""
    try:
        client = AsyncOpenAI()
        response = await client.audio.speech.create(
            model="tts-1-hd", voice="nova", input=text.text
        )
        return Response(content=response.content, media_type="audio/mp3")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=e.with_traceback
        ) from e
