"""Endpoint and business logic related to ChatGPT."""

from fastapi import APIRouter, HTTPException, status
from openai.types.chat import ChatCompletion
from openai.types.chat.chat_completion import Choice

from drivel_server.clients import OpenAIClientSingleton
from drivel_server.schemas.chatgpt import OpenAIParameters

router = APIRouter()


@router.post("/", response_model=list[Choice])
async def chat_responses(params: OpenAIParameters) -> list[Choice]:
    """
    Forwards the conversation to the OpenAI API and retrieves a generated response.

    This endpoint accepts a POST request with a JSON body compliant with the
    `OpenAIParameters` model, which includes a list of conversation messages and other
    parameters for the OpenAI completion API. The endpoint processes this data to
    interact with the specified OpenAI GPT model and returns the model's response as a
    string.

    The response is encapsulated in a dictionary with the key 'response'. In the event
    of an API failure or absence of a response, an HTTP exception with an appropriate
    status code will be raised.

    For the structure of the input and further details on the parameters, refer to the
    `OpenAIParameters` model.
    """
    try:
        client = await OpenAIClientSingleton.get_instance()
        # Call the OpenAI API with the messages
        chat_completion = await client.chat.completions.create(
            **params.model_dump(exclude_none=True)
        )
        assert isinstance(chat_completion, ChatCompletion)
        # Return the text part of the OpenAI API response
        return chat_completion.choices
    except Exception as e:
        # Handle errors and exceptions
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
