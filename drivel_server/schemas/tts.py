from typing import Self

from pydantic import BaseModel, model_validator


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
