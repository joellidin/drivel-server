"""Endpoint and business logic related to text-to-speech."""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response
from google.cloud import texttospeech as tts

from drivel_server.clients import GoogleCloudClientSingleton
from drivel_server.schemas.tts import TTSParameters

router = APIRouter()


@router.post("/", response_model=None)
async def text_to_speech(params: TTSParameters) -> Response:
    """Process a text message and return its text-to-speech result."""
    try:
        client = await GoogleCloudClientSingleton.get_instance()
        synthesis_input = tts.SynthesisInput(text=params.text)

        # Build the voice request, select the language code and voice
        voice = tts.VoiceSelectionParams(
            language_code=params.language_code, name=params.name
        )

        # Select the type of audio file you want returned
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.MP3, speaking_rate=params.speaking_rate
        )

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
