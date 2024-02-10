"""Security related things, such as secrets."""
import os

from drivel_server.core.config import settings


def get_openai_api_key(
    api_key_file: str | os.PathLike = settings.OPENAI_API_KEY_FILE,
) -> str:
    """Reading the OpenAI API key from file."""
    with open(api_key_file, "r") as f:
        return f.read().strip()
