"""Collection of all routers in v1."""

from fastapi import APIRouter

from drivel_server.api.v1.endpoints import chat_replies, stt, tts

router = APIRouter()


@router.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"Hello": "World"}


api_router = APIRouter()
api_router.include_router(router, prefix="", tags=["root"])
api_router.include_router(tts.router, prefix="/text-to-speech", tags=["tts"])
api_router.include_router(stt.router, prefix="/speech-to-text", tags=["stt"])
api_router.include_router(
    chat_replies.router, prefix="/chat-responses", tags=["chat_replies"]
)
