"""Security related things, such as secrets."""
from drivel_server.core.config import settings


async def get_openai_api_key() -> str:
    """Get the OpenAI API key.

    In a production environment, it is read from a file. In a development
    environment, it is fetched from Google Secret Manager.
    """
    match settings.env:
        case "prod":
            with open(settings.openai_api_key_file, "r") as f:
                return f.read().strip()
        case "dev":
            from google.cloud import secretmanager

            client = secretmanager.SecretManagerServiceAsyncClient()
            secret = await client.access_secret_version(
                name=f"projects/{settings.gcp_project_number}/secrets/{settings.gcp_secret_name_openai_key}/versions/latest"
            )
            return secret.payload.data.decode()
