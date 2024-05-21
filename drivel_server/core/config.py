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

from typing import Final, Literal

from pydantic import computed_field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from drivel_server.core.literals import GPT_MODELS


class Settings(BaseSettings):
    """
    Configuration settings for the application.

    This class specifies various settings for the application, such as API
    paths, project name and the speech-to-text model to use. It uses pydantic's
    BaseSettings for easy, environment-based configuration and validation,
    aiming to streamline application setup and ensure secure handling of
    sensitive parameters.

    Fields without defaults need to be present in `.env` or defined as
    environment variables, otherwise a pydantic ValidationError will be raised.
    """

    model_config = SettingsConfigDict(yaml_file=".env.yaml", yaml_file_encoding="utf-8")

    GCP_PROJECT_NUMBER: str
    GCP_SECRET_NAME_OPENAI_KEY: str
    GCP_SECRET_NAME_OPENAI_ORGANIZATION_ID: str
    GCP_SECRET_NAME_OPENAI_PROJECT_ID: str
    SECRETS_FOLDER: str

    # The environment variable `ENV` is set to prod in the deploy script. In
    # development, the env variable is not set. Instead, the devault value
    # below is used.
    env: Literal["dev", "prod"] = "dev"

    API_V1_STR: Final[str] = "/api/v1"
    project_name: str = "drivel-server"

    gpt_model: GPT_MODELS = "gpt-3.5-turbo"
    stt_model: str = "whisper-1"

    @computed_field
    @property
    def openai_api_key_file(self) -> str:
        """Construct path to OpenAI API key file."""
        return f"{self.SECRETS_FOLDER}/api-key/{self.GCP_SECRET_NAME_OPENAI_KEY}"

    @computed_field
    @property
    def openai_organization_id_file(self) -> str:
        """Construct path to OpenAI organization ID file."""
        return (
            f"{self.SECRETS_FOLDER}/org-id/"
            f"{self.GCP_SECRET_NAME_OPENAI_ORGANIZATION_ID}"
        )

    @computed_field
    @property
    def openai_project_id_file(self) -> str:
        """Construct path to OpenAI project ID file."""
        return (
            f"{self.SECRETS_FOLDER}/proj-id/"
            f"{self.GCP_SECRET_NAME_OPENAI_PROJECT_ID}"
        )

    @classmethod
    def settings_customise_sources(  # noqa: PLR0913
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Customize the sources of settings for a Pydantic BaseSettings class.

        This class method allows for the customization of the order and types of
        settings sources used by a Pydantic BaseSettings class. By overriding this
        method, additional settings sources can be added, or existing ones can be
        reordered.
        """
        return (
            init_settings,
            YamlConfigSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


settings = Settings()
