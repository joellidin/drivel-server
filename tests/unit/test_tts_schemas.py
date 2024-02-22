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
