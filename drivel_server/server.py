"""Entrypoint for the Drivel Server API.

This module initializes the FastAPI application, includes all the route
routers.
"""
from fastapi import FastAPI

from drivel_server.interfaces.api.routers.openai_router import router as openapi_router

app = FastAPI()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint for server alive checks."""
    return {"Hello": "World"}


app.include_router(openapi_router)
