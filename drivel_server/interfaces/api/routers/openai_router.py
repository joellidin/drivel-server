"""Bridge between client and OpenAI API, processing parameters, returning response."""
from fastapi import APIRouter, HTTPException, status
from openai.types.chat.chat_completion import Choice

from drivel_server.core.use_cases.openai_processing import OpenAIInteraction
from drivel_server.interfaces.api.schemas.openai_params import OpenAIParameters

router = APIRouter()
openai_interaction = OpenAIInteraction()


@router.post("/generate-response/", response_model=list[Choice])
async def generate_response(params: OpenAIParameters) -> list[Choice]:
    """Process parameters, interact with OpenAI API, return response."""
    try:
        return await openai_interaction.execute(params)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
