from fastapi import APIRouter

from drivel_server.api.v1.endpoints import chatgpt, stt, tts

router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"Hello": "World"}


api_router = APIRouter()
api_router.include_router(router, prefix="", tags=["root"])
api_router.include_router(tts.router, prefix="/text-to-speech", tags=["tts"])
api_router.include_router(stt.router, prefix="/speech-to-text", tags=["stt"])
api_router.include_router(chatgpt.router, prefix="/chat-responses", tags=["chatgpt"])
