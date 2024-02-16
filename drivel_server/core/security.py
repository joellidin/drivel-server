"""Security related things, such as secrets."""
from drivel_server.core.config import settings


async def get_openai_api_key() -> str:
    """Get the OpenAI API key.

    In a production environment, it is read from a file. In a development
    environment, it is fetched from Google Secret Manager.
    """
    match settings.ENV:
        case "prod":
            with open(settings.OPENAI_API_KEY_FILE, "r") as f:
                return f.read().strip()
        case "dev":
            from google.cloud import secretmanager

            client = secretmanager.SecretManagerServiceAsyncClient()
            secret = await client.access_secret_version(
                name=f"projects/{settings.GCP_PROJECT_NUMBER}/secrets/{settings.GCP_SECRET_NAME_OPENAI_KEY}/versions/latest"
            )
            return secret.payload.data.decode()
