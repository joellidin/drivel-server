# Cloud Run

## Preparation

1. If you're on an M1 Mac run the following to enable amd64 platforms, such as
   the ones on Cloud Run, to run the image:

   ```bash
   export DOCKER_DEFAULT_PLATFORM=linux/amd64
   ```

2. Install the [gcloud CLI](https://cloud.google.com/sdk/docs/install).

3. Authenticate to google cloud:
   
   ```bash
   gcloud auth login
   ```

4. Configure docker:
   
   ```bash
   gcloud auth configure-docker europe-north1-docker.pkg.dev
   ```

This guide further assumes that
- you have sufficient permissions to the GCP project reflog-414215, and that this project has a
   - repository in Artifact Registry called drivel-backend
   - Cloud Run service called drivel-backend

## Deployment

1. Build the image.

2. Tag the image:
   
   ```bash
   docker tag drivel-server-server:latest \
   europe-north1-docker.pkg.dev/reflog-414215/drivel-backend/drivel-server-server:latest
   ```

3. Push the image to the registry:

   ```bash
   docker push \
   europe-north1-docker.pkg.dev/reflog-414215/drivel-backend/drivel-server-server:latest
   ```

4. Deploy the pushed image:

   ```bash
   gcloud run deploy drivel-backend --image \
   europe-north1-docker.pkg.dev/reflog-414215/drivel-backend/drivel-server-server:latest \
   --region europe-north1
   ```

## Accessing the endpoint

The service url is `https://drivel-backend-k3u2qxk4cq-lz.a.run.app`. The
service requires Cloud IAM authentication. If you make a request using curl,
one way to authenticate is to add `-H "Authorization: Bearer $(gcloud auth
print-identity-token)"` to the curl command. For example:
```bash
curl -X GET \
  'https://drivel-backend-k3u2qxk4cq-lz.a.run.app/api/v1/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)"
```

## Next steps

Continuous deployment and authentication.
