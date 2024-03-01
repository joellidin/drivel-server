"""Clients to be used in the endpoints."""

import asyncio

from google.cloud import texttospeech as tts
from openai import AsyncClient

from drivel_server.core.security import get_openai_secret


class OpenAIClientSingleton:
    """
    A singleton to manage and reuse an instance of an asynchronous OpenAI client.

    This class ensures that only one instance of the OpenAI client is created and reused
    throughout the application, promoting efficient resource use and consistency in API
    calls.
    """

    _instance = None

    @classmethod
    async def get_instance(cls) -> AsyncClient:
        """
        Asynchronously retrieves the singleton instance of the OpenAI client.

        If the instance does not exist, it creates a new one by asynchronously obtaining
        the necessary API secrets and initializes the AsyncClient with these secrets.
        Otherwise, it returns the existing instance.

        Returns:
            AsyncClient: The singleton instance of the OpenAI client.
        """
        async with asyncio.Lock():
            if cls._instance is None:
                api_key, org_id = await cls._get_openai_secrets()
                cls._instance = AsyncClient(api_key=api_key, organization=org_id)
        return cls._instance

    @staticmethod
    async def _get_openai_secrets() -> tuple[str, str]:
        """
        Retrieves the OpenAI API key and orgID required for initializing the client.

        This method concurrently fetches the 'api_key' and 'org_id' using an unspecified
        `get_openai_secret` function, which is assumed to be an asynchronous function
        that accesses some form of secure storage.

        Returns:
            Tuple[str, str]: A tuple containing the OpenAI API key and organization ID.
        """
        a, b = await asyncio.gather(
            get_openai_secret("api_key"), get_openai_secret("org_id")
        )
        return a, b


class GoogleCloudClientSingleton:
    """
    A singleton to manage and reuse an instance of the Google Cloud TTS async client.

    This class ensures that only one instance of the Google Cloud Text-to-Speech client
    is created and reused throughout the application, promoting efficient resource use
    and consistency in API calls.
    """

    _instance = None

    @classmethod
    async def get_instance(cls) -> tts.TextToSpeechAsyncClient:
        """
        Retrieves the singleton instance of the Google Cloud Text-to-Speech client.

        If the instance does not exist, it creates a new one by initializing the
        TextToSpeechAsyncClient. Otherwise, it returns the existing instance.

        Returns:
            TextToSpeechAsyncClient: The singleton instance of the Google Cloud
            Text-to-Speech client.

        Side Effects:
            Prints a message indicating whether a new client was created or an existing
            one is reused.
        """
        async with asyncio.Lock():
            if cls._instance is None:
                cls._instance = tts.TextToSpeechAsyncClient()
        return cls._instance
