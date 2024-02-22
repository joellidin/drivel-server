#!/bin/bash

# Stop execution on any error
set -e

# Source the variables defined in the .env file
source .env

# Define variables for reuse
IMAGE_NAME="drivel-server-server"
TAG="latest"
GCP_PROJECT_ID="reflog-414215"
GCR_REGION="europe-north1"
GCR_HOSTNAME="${GCR_REGION}-docker.pkg.dev"
REPOSITORY_NAME="drivel-backend"
CLOUD_RUN_SERVICE="drivel-backend"
SECRET_VERSION="latest"

# Full image name for GCR
GCR_IMAGE_NAME="${GCR_HOSTNAME}/${GCP_PROJECT_ID}/${REPOSITORY_NAME}/${IMAGE_NAME}:${TAG}"

echo "Starting deployment process..."

# Step 1: Build the Docker image without using cache
echo "Building Docker image..."
docker compose build --no-cache
echo "Docker image built successfully."

# Step 2: Tag the Docker image for Google Cloud Registry
echo "Tagging the image for GCR..."
docker tag ${IMAGE_NAME}:${TAG} ${GCR_IMAGE_NAME}
echo "Image tagged successfully: ${GCR_IMAGE_NAME}"

# Step 3: Push the Docker image to Google Cloud Registry
echo "Pushing the image to Google Cloud Registry..."
docker push ${GCR_IMAGE_NAME}
echo "Image pushed to GCR successfully."

# Step 4: Deploy the Docker image to Google Cloud Run
echo "Deploying the image to Google Cloud Run..."
gcloud run deploy ${CLOUD_RUN_SERVICE} --image ${GCR_IMAGE_NAME} --region ${GCR_REGION} --no-allow-unauthenticated --update-secrets=${SECRETS_FOLDER}/${GCP_SECRET_NAME_OPENAI_KEY}=projects/${GCP_PROJECT_NUMBER}/secrets/${GCP_SECRET_NAME_OPENAI_KEY}:${SECRET_VERSION}
echo "Deployment to Google Cloud Run successful."

echo "Deployment process completed successfully."
