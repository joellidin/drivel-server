"""Security related things, such as secrets."""

from typing import Literal

from drivel_server.core.config import settings


async def get_openai_secret(name: Literal["api_key", "org_id", "proj_id"]) -> str:
    """Get the OpenAI secret value.

    In a production environment, it is read from a file. In a development
    environment, it is fetched from Google Secret Manager.
    """
    match name:
        case "api_key":
            file = settings.openai_api_key_file
            gcp_secret_name = settings.GCP_SECRET_NAME_OPENAI_KEY
        case "org_id":
            file = settings.openai_organization_id_file
            gcp_secret_name = settings.GCP_SECRET_NAME_OPENAI_ORGANIZATION_ID
        case "proj_id":
            file = settings.openai_project_id_file
            gcp_secret_name = settings.GCP_SECRET_NAME_OPENAI_PROJECT_ID

    match settings.env:
        case "prod":
            with open(file, "r") as f:
                return f.read().strip()
        case "dev":
            from google.cloud import secretmanager

            client = secretmanager.SecretManagerServiceAsyncClient()
            secret = await client.access_secret_version(
                name=f"projects/{settings.GCP_PROJECT_NUMBER}/secrets/{gcp_secret_name}/versions/latest"
            )
            return secret.payload.data.decode()
