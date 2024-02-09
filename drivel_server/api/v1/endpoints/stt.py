import io

from fastapi import APIRouter, HTTPException, UploadFile, status
from openai import AsyncOpenAI
from openai.types.audio import Transcription

from drivel_server.core.config import settings
from drivel_server.core.security import get_openai_api_key

router = APIRouter()


@router.post("/speech-to-text/", response_model=Transcription)
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
            file=buffer, model=settings.STT_MODEL, language="es"
        )
    except Exception as e:
        # Handle errors and exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
