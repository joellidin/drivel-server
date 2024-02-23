"""Security related things, such as secrets."""
from typing import Literal

from drivel_server.core.config import settings


async def get_openai_secret(name: Literal["api_key", "org_id"]) -> str:
    """Get the OpenAI secret value.

    In a production environment, it is read from a file. In a development
    environment, it is fetched from Google Secret Manager.
    """
    match name:
        case "api_key":
            file = settings.openai_api_key_file
            gcp_secret_name = settings.gcp_secret_name_openai_key
        case "org_id":
            file = settings.openai_organization_id_file
            gcp_secret_name = settings.gcp_secret_name_openai_organization_id

    match settings.env:
        case "prod":
            with open(file, "r") as f:
                return f.read().strip()
        case "dev":
            from google.cloud import secretmanager

            client = secretmanager.SecretManagerServiceAsyncClient()
            secret = await client.access_secret_version(
                name=f"projects/{settings.gcp_project_number}/secrets/{gcp_secret_name}/versions/latest"
            )
            return secret.payload.data.decode()
