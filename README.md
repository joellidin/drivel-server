# drivel-server

## Development

### Getting started

#### Environment variables

Create a `.env.yaml` file with the help of `.env-dev.yaml`. You will also need
to have [`yq`](https://github.com/mikefarah/yq) to be able to parse the yaml
file into a `.env` file. To generate the `.env` file you can run `just
generate-dotenv`. This needs to be rerun as soon as your `.env.yaml` file is
updated.

#### Google cloud authentication

This is needed to authenticate to the Google API's, such as the Secret Manager.

1. Set up the [gcloud CLI](https://cloud.google.com/sdk/docs/install).

2. Create a [Application Default Credentials file](https://cloud.google.com/docs/authentication/provide-credentials-adc#google-idp):

```bash
gcloud auth application-default login
```

### Server

You can run the server with

```bash
uvicorn drivel_server.server:app --reload
```

in your virtual environment.

> [!NOTE]
> The `--reload` flag is used to update the server if the code changes
> and is not to be used in production

You can run the server in a docker container with

```bash
`docker compose up --build`
```

To make requests, you can then either do a simple curl:

```bash
curl -X GET 127.0.0.1:8000/api/v1/
```

or you can go into the browser with the same address and port.

#### Documentation

FastAPI automatically generates API documentation with Swagger UI, so you can
also go to [127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) in the browser and run
the GET request there.

## Deployment

To deploy you need sufficient permissions to the GCP project reflog-414215.
Additionally, you need to configure docker for gcloud. This only needs to be done once.

```bash
gcloud auth configure-docker europe-north1-docker.pkg.dev
```

Then, you can deploy with

```bash
just deploy
```

> [!NOTE]
> You need to install
> [just](https://github.com/casey/just?tab=readme-ov-file#installation) to use
> the [`justfile`](/justfile).


### Accessing the endpoints

The service url is

```bash
https://drivel-backend-k3u2qxk4cq-lz.a.run.app
```

You can test it out with the different `just` recipes:

- `just get_root`: calls the root endpoint
- `just chat_responses <message>`: calls the chat-responses endpoint
- `just tts <audio_file_path>`: calls the text-to-speech endpoint
- `just stt <message> <audio_output_path>`: calls the speech-to-text endpoint

All the arguments above have default values. More information about these
recipes could be found with

```bash
just --list
```

### Adding a new secret

If we need to have another secret in our google secret manager we have some
necessary steps to do:

1. Create the secret in `gcloud`, either through the web ui or by using `gcloud
   secret create`.
2. Add the secret name as an environment variable in `.env-dev.yaml`.
3. Update your `.env.yaml` file and run `just generate-dotenv`.
4. Add the secret name to our pydantic
   [`Settings`](https://github.com/joellidin/drivel-server/blob/main/drivel_server/core/config.py).
   It should be the same name as in step 2 but with lower case.
5. Add the secret to our github iam policy for our CI
   ```bash
   gcloud secrets add-iam-policy-binding "<secret-name>"
   --project="reflog-414215" --role="roles/secretmanager.secretAccessor"
   --member="principalSet://iam.googleapis.com/projects/1024792190274/locations/global/workloadIdentityPools/github/attribute.repository/joellidin/drivel-server"
   ```
6. Add the secret to our deploy recipe. You need to add this flag:
   ```bash
   --update-secrets={{GCP_SECRET_NAME}}={{GCP_SECRET_LOCATION}}:{{SECRET_VERSION}}
   ```
   See the just file for how we have done for the other secrets.
