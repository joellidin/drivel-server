# drivel-server

## Development

### Server

To run the server you need to run:

```bash
uvicorn drivel_server.server:app --reload
```

in your virtual environment.

> [!NOTE]
> The `--reload` flag is used to update the server if the code changes
> and is not to be used in production

You can then either do a simple curl:

```bash
curl -X GET 127.0.0.1:8000/
```

or you can go into the browser with the same address and port.

#### Documentation

FastAPI automatically generates API documentation with Swagger UI, so you can
also go to [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in the browser and run
the GET request there.
