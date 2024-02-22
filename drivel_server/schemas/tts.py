"""Schemas used by the text-to-speech endpoint."""
import re
from typing import Self

from pydantic import BaseModel, field_validator, model_validator


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

    @model_validator(mode="after")
    def voice_name_must_start_with_language_code(self) -> Self:
        """Validate that 'voice_name' starts with the language code."""
        assert self.name.startswith(self.language_code), (
            f"name '{self.name}' does not start with language_code"
            f" '{self.language_code}'"
        )
        return self
