"""
Application Configuration Module.

This module defines the application settings using pydantic's BaseSettings for
enhanced configuration management. It allows for the loading of settings from
environment variables, providing a secure and flexible way to manage
application configurations. Key settings include API paths, project
identification, secrets, and ML model specifications. This setup facilitates
integration with cloud services and external APIs while avoiding the
hard-coding of sensitive information.

To access the application configurations, import the `settings` object from
this module throughout the project.

Example:
    ```python
    from drivel_server.core.config import settings
    api_base_url = settings.API_V1_STR
    project_name = settings.PROJECT_NAME
    ```
"""

from pydantic_settings import BaseSettings

from drivel_server.core.literals import GPT_MODELS


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class specifies various settings for the application, such as API
    paths, project name, paths to service account keys, and the speech-to-text
    model to use. It uses pydantic's BaseSettings for easy, environment-based
    configuration and validation, aiming to streamline application setup and
    ensure secure handling of sensitive parameters.
    """

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "drivel-server"
    SERVICE_ACCOUNT_KEY_FILE: str = "/run/secrets/google-service-account-key.json"
    OPENAI_API_KEY_FILE: str = "/run/secrets/openai-key.txt"

    GPT_MODEL: GPT_MODELS = "gpt-3.5-turbo"
    STT_MODEL: str = "whisper-1"


settings = Settings()
