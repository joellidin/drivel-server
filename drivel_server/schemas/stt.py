"""Schemas used by the text-to-speech endpoint."""

from fastapi import APIRouter
from pydantic import BaseModel

from drivel_server.core.config import settings

router = APIRouter()


class STTParameters(BaseModel):
    """
    Represents the parameters for configuring a Speech-to-Text (STT) request.

    ### Fields:
    - **model**: The name of the model to be used for the STT conversion. This
      field allows for customization of the model used.

    - **language**: Specifies the BCP-47 language code that indicates the
    language of the input audio and the expected transcription.
    """

    model: str = settings.stt_model
    language: str = "es"
