from pydantic_settings import BaseSettings

from drivel_server.core.literals import GPT_MODELS


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "drivel-server"
    SERVICE_ACCOUNT_KEY_FILE: str = "/run/secrets/google-service-account-key"
    OPENAI_API_KEY_FILE: str = "/run/secrets/openai-key"

    GPT_MODEL: GPT_MODELS = "gpt-3.5-turbo"
    STT_MODEL: str = "whisper-1"


settings = Settings()
