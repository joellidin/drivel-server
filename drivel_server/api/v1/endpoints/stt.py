"""Endpoint and business logic related to speech-to-text."""

import io

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from openai.types.audio import Transcription

from drivel_server.clients import OpenAIClientSingleton
from drivel_server.schemas.stt import STTParameters

router = APIRouter()


@router.post("/", response_model=Transcription)
async def speech_to_text(
    audio_file: UploadFile, params: STTParameters = Depends()
) -> Transcription:
    """
    Process an audio file and return its speech-to-text transcription.

    This function takes an uploaded audio file, sends it to the OpenAI Whisper
    and returns the transcription object.
    """
    try:
        client = await OpenAIClientSingleton.get_instance()
        audio = await audio_file.read()
        buffer = io.BytesIO(audio)
        buffer.name = audio_file.filename
        return await client.audio.transcriptions.create(
            file=buffer, model=params.model, language=params.language
        )
    except Exception as e:
        # Handle errors and exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
