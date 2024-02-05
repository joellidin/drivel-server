"""Server module."""

import io
from typing import Literal, Type, TypeVar

from fastapi import FastAPI, File, HTTPException, UploadFile, status
from google.cloud import speech
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam
from openai.types.chat.chat_completion import Choice
from pydantic import BaseModel, ValidationInfo, field_validator
from pydub import AudioSegment

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

T = TypeVar("T", bound="SpeechRecognitionResponse")

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


class TranscriptionResult(BaseModel):
    """Representation of a single transcription result from the speech recognition.

    ### Fields:
        - **transcription**: The transcribed text.

        - **result_end_time**: The time, in seconds, at which the transcription
          result ends in the audio.

        - **language_code**: The language code of the transcribed text.
    """

    transcription: str
    result_end_time: float
    language_code: str


class SpeechRecognitionResponse(BaseModel):
    """Representation of the overall response from the speech recognition.

    ### Fields:
    - **transcriptions**: A list of transcription results.

    - **total_billed_time**: The total time billed by the speech recognition
        service, in seconds.

    - **request_id**: A unique identifier for the recognition request.

    Methods:
    - **from_google_response**: Class method to create an instance from a
        Google Cloud Speech-to-Text response.
    """

    transcriptions: list[TranscriptionResult]
    total_billed_time: int
    request_id: int

    @classmethod
    def from_google_response(cls: Type[T], response: speech.RecognizeResponse) -> T:
        """Constructs an instance of the class from a Google STT API response.

        This method parses the Google Speech-to-Text API's RecognizeResponse to
        extract the fields.
        """
        items = [
            TranscriptionResult(
                transcription=alternative.transcript,
                result_end_time=result.result_end_time.total_seconds(),
                language_code=result.language_code,
            )
            for result in response.results
            for alternative in result.alternatives
        ]
        return cls(
            transcriptions=items,
            total_billed_time=response.total_billed_time.seconds,
            request_id=response.request_id,
        )


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


@app.post("/perform-stt/", response_model=SpeechRecognitionResponse)
async def perform_stt(raw_audio: UploadFile = File(...)) -> SpeechRecognitionResponse:  # noqa: B008
    """Process an audio file and return its speech-to-text transcription.

    This function takes an uploaded audio file of m4a format, converts it to
    wav, sends it for transcription, and then formats the response into a
    structured format.
    """
    try:
        # preprocess, assuming the input audio has m4a format
        audio_bytes_m4a = await raw_audio.read()
        audio_segment = AudioSegment.from_file(
            io.BytesIO(audio_bytes_m4a), format="m4a"
        )
        buffer = io.BytesIO()
        audio_segment.export(buffer, format="wav")
        buffer.seek(0)
        audio_bytes_wav = buffer.getvalue()
        audio = speech.RecognitionAudio(content=audio_bytes_wav)

        # prepare the STT client and config
        client = speech.SpeechClient()
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=48000,
            language_code="es-ES",
            enable_automatic_punctuation=True,
        )

        # detect speech in the audio file
        response = client.recognize(config=config, audio=audio)
        return SpeechRecognitionResponse.from_google_response(response)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
