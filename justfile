set export
set dotenv-load

# Define variables for reuse
IMAGE_NAME                     := env("IMAGE_NAME", "drivel-server-backend")
TAG                            := env("TAG", "latest")
GCP_PROJECT_ID                 := env("GCP_PROJECT_ID", "reflog-414215")
GCR_REGION                     := env("GCR_REGION", "europe-north1")
GCR_HOSTNAME                   := env("GCR_HOSTNAME", GCR_REGION + "-docker.pkg.dev")
GCP_SECRET_OPENAI_KEY_PATH     := "${SECRETS_FOLDER}/api-key/${GCP_SECRET_NAME_OPENAI_KEY}"
GCP_SECRET_ORG_ID_PATH         := "${SECRETS_FOLDER}/org-id/${GCP_SECRET_NAME_OPENAI_ORGANIZATION_ID}"
GCP_SECRET_OPENAI_KEY_LOCATION := "projects/${GCP_PROJECT_NUMBER}/secrets/${GCP_SECRET_NAME_OPENAI_KEY}"
GCP_SECRET_ORG_ID_LOCATION     := "projects/${GCP_PROJECT_NUMBER}/secrets/${GCP_SECRET_NAME_OPENAI_ORGANIZATION_ID}"
REPOSITORY_NAME                := env("REPOSITORY_NAME", "drivel-backend")
CLOUD_RUN_SERVICE              := env("CLOUD_RUN_SERVICE", "drivel-backend")
SECRET_VERSION                 := env("SECRET_VERSION", "latest")

# Full image name for GCR
GCR_IMAGE_NAME                 := GCR_HOSTNAME / GCP_PROJECT_ID / REPOSITORY_NAME / IMAGE_NAME

@build tag=TAG:
    echo "\033[1m\033[33mBuilding Docker image...\033[0m"
    TAG={{tag}} docker compose build --no-cache
    echo "\033[1m\033[32mDocker image built successfully.\033[0m"

@tag tag=TAG:
    echo "\033[1m\033[33mTagging the image for GCR...\033[0m"
    @docker tag {{IMAGE_NAME}}:{{tag}} {{GCR_IMAGE_NAME}}:{{tag}}
    echo "\033[1m\033[32mImage tagged successfully: ${GCR_IMAGE_NAME}\033[0m"

@push tag=TAG:
    echo "\033[1m\033[33mPushing the image to Google Cloud Registry...\033[0m"
    docker push {{GCR_IMAGE_NAME}}:{{tag}}
    echo "\033[1m\033[32mImage pushed to GCR successfully.\033[0m"

@build_and_push tag=TAG: (build tag) (tag tag) (push tag)

alias bp := build_and_push

@deploy tag=TAG: (build_and_push tag)
    echo "\033[1m\033[33mDeploying the image to Google Cloud Run...\033[0m"
    gcloud run deploy {{CLOUD_RUN_SERVICE}} --image {{GCR_IMAGE_NAME}} --region {{GCR_REGION}} --allow-unauthenticated \
        --update-secrets={{GCP_SECRET_OPENAI_KEY_PATH}}={{GCP_SECRET_OPENAI_KEY_LOCATION}}:{{SECRET_VERSION}} \
        --update-secrets={{GCP_SECRET_ORG_ID_PATH}}={{GCP_SECRET_ORG_ID_LOCATION}}:{{SECRET_VERSION}}
    echo "\033[1m\033[32mDeployment to Google Cloud Run successful.\033[0m"
