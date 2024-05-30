from pydantic import ValidationError
import pytest

from drivel_server.schemas.tts import TTSParameters


def test_default_values() -> None:
    """Default values remain the same."""
    params = TTSParameters(text="Un texto cualquiera")
    assert params.language_code == "es-ES"
    assert params.name == "es-ES-Standard-B"


def test_text_must_not_be_empty_valid() -> None:
    """Valid text should not raise ValidationError."""
    params = TTSParameters(text="Hello", language_code="en-US", name="en-US-Standard-A")
    assert params.text == "Hello"


def test_text_must_not_be_empty_invalid() -> None:
    """Empty text should raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        TTSParameters(text="", language_code="en-US", name="en-US-Standard-A")
    assert "text must not be empty" in str(exc_info.value)


def test_language_code_must_follow_pattern_valid() -> None:
    """Valid language_code should not raise ValidationError."""
    params = TTSParameters(text="Hello", language_code="en-US", name="en-US-Standard-A")
    assert params.language_code == "en-US"


def test_language_code_must_follow_pattern_invalid() -> None:
    """Invalid language_code format should raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        TTSParameters(text="Hello", language_code="english", name="english-Standard-A")
    assert "language_code must be in the format" in str(exc_info.value)


def test_voice_name_must_start_with_language_code_valid() -> None:
    """voice_name starting with language_code should not raise ValidationError."""
    params = TTSParameters(text="Hello", language_code="en-US", name="en-US-Standard-A")
    assert params.name.startswith(params.language_code)


def test_voice_name_must_start_with_language_code_invalid() -> None:
    """voice_name not starting with language_code should raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        TTSParameters(text="Hello", language_code="en-US", name="fr-FR-Standard-A")
    assert "does not start with language_code" in str(exc_info.value)


def test_speaking_rate_valid_default() -> None:
    """Default `speaking_rate` should be valid."""
    params = TTSParameters(text="Un texto cualquiera")
    assert params.speaking_rate == 1


def test_speaking_rate_valid_custom() -> None:
    """Valid custom `speaking_rate` should not raise ValidationError."""
    params = TTSParameters(
        text="Hello", language_code="en-US", name="en-US-Standard-A", speaking_rate=2.5
    )
    assert params.speaking_rate == 2.5


@pytest.mark.parametrize(
    "speaking_rate",
    [
        (0.24),  # Below the valid range
        (4.01),  # Above the valid range
    ],
)
def test_speaking_rate_invalid(speaking_rate: float) -> None:
    """speaking_rate outside the range 0.25 to 4 should raise ValidationError."""
    with pytest.raises(ValidationError) as exc_info:
        TTSParameters(
            text="Hello",
            language_code="en-US",
            name="en-US-Standard-A",
            speaking_rate=speaking_rate,
        )
    assert "speaking_rate must be between 0.25 and 4" in str(exc_info.value)
