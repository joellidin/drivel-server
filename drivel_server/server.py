"""Server module."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint."""
    return {"Hello": "World"}


class OpenAIParameters:
    """Todo."""

    ...
