"""Schemas used by the text-to-speech endpoint."""

import re
from typing import Self

from pydantic import BaseModel, field_validator, model_validator

from drivel_server.core.config import settings


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
    speaking_rate: float = 1.0

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        """Validate that 'text' is not empty."""
        if v == "":
            raise ValueError("text must not be empty")
        return v

    @field_validator("language_code")
    @classmethod
    def language_code_must_follow_pattern(cls, v: str) -> str:
        """Validate 'language_code' as 'xx-XX': two lowercase, dash, two uppercase."""
        if not re.match(r"^[a-z]{2}-[A-Z]{2}$", v):
            raise ValueError(
                "language_code must be in the format: two lowercase letters"
                "dash, two uppercase letters"
            )
        return v

    @field_validator("speaking_rate")
    @classmethod
    def speaking_rate_must_be_in_range(cls, v: float) -> float:
        """Validate that 'speaking_rate' is between 0.25 and 4."""
        if not (
            settings.stt_speech_rate_interval[0]
            <= v
            <= settings.stt_speech_rate_interval[1]
        ):
            raise ValueError("speaking_rate must be between 0.25 and 4")
        return v

    @model_validator(mode="after")
    def voice_name_must_start_with_language_code(self) -> Self:
        """Validate that 'voice_name' starts with the language code."""
        assert self.name.startswith(self.language_code), (
            f"name '{self.name}' does not start with language_code"
            f" '{self.language_code}'"
        )
        return self
