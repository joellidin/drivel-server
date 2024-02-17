# drivel-server

## Development

### Getting started

#### Environment variables

Create a .env file with the help of .env.template.

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
   scripts/deploy
   ```


### Accessing the endpoint

The service url is

   ```bash
   https://drivel-backend-k3u2qxk4cq-lz.a.run.app
   ```

The service requires Cloud IAM authentication. If you make a request using curl,
one way to authenticate is to add

   ```bash
   -H "Authorization: Bearer $(gcloud auth print-identity-token)"
   ```

to the curl command. For example:

```bash
curl -X GET \
  'https://drivel-backend-k3u2qxk4cq-lz.a.run.app/api/v1/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)"
```
