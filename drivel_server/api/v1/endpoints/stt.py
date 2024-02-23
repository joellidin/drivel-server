"""Endpoint and business logic related to speech-to-text."""
import asyncio
import io

from fastapi import APIRouter, HTTPException, UploadFile, status
from openai import AsyncOpenAI
from openai.types.audio import Transcription

from drivel_server.core.config import settings
from drivel_server.core.security import get_openai_secret

router = APIRouter()


@router.post("/", response_model=Transcription)
async def speech_to_text(audio_file: UploadFile) -> Transcription:
    """
    Process an audio file and return its speech-to-text transcription.

    This function takes an uploaded audio file sends it to the OpenAI Whisper
    and returns the transcription object.
    """
    try:
        api_key, organization_id = await asyncio.gather(
            get_openai_secret("api_key"), get_openai_secret("org_id")
        )
        client = AsyncOpenAI(api_key=api_key, organization=organization_id)
        audio = await audio_file.read()
        buffer = io.BytesIO(audio)
        buffer.name = audio_file.filename
        return await client.audio.transcriptions.create(
            file=buffer, model=settings.stt_model, language="es"
        )
    except Exception as e:
        # Handle errors and exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
