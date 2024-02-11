# Cloud Run

## Preparation

1. If you're on an M1 Mac run the following to enable amd64 platforms, such as
   the ones on Cloud Run, to run the image:

   ```export DOCKER_DEFAULT_PLATFORM=linux/amd64```

2. Install the gcloud CLI.

3. `gcloud auth login`

4. Configure docker: `gcloud auth configure-docker europe-north1-docker.pkg.dev`.

This guide further assumes that
- you have sufficient permissions to the GCP project reflog-414215, and that this project has a
   - repository in Artifact Registry, and a
   - Cloud Run service.

## Deployment

1. Build the image.

1. Tag the image: `docker tag drivel-server-server:latest europe-north1-docker.pkg.dev/reflog-414215/drivel-backend/drivel-server-server:latest`.

2. Push the image to the registry: `docker push europe-north1-docker.pkg.dev/reflog-414215/drivel-backend/drivel-server-server:latest`.

3. Deploy the pushed image: `gcloud run deploy <SERVICE> --image europe-north1-docker.pkg.dev/reflog-414215/drivel/drivel-server-server:latest --region europe-north1`.

## Accessing the endpoint

If the service requires Cloud IAM authentication, one way to authenticate is to
add `-H "Authorization: Bearer $(gcloud auth print-identity-token)"` to the
curl commands.

## Next steps

Continuous deployment and authentication.
