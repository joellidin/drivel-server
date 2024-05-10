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
GCP_SECRET_PROJ_ID_PATH         := "${SECRETS_FOLDER}/proj-id/${GCP_SECRET_NAME_OPENAI_PROJECT_ID}"
GCP_SECRET_OPENAI_KEY_LOCATION := "projects/${GCP_PROJECT_NUMBER}/secrets/${GCP_SECRET_NAME_OPENAI_KEY}"
GCP_SECRET_ORG_ID_LOCATION     := "projects/${GCP_PROJECT_NUMBER}/secrets/${GCP_SECRET_NAME_OPENAI_ORGANIZATION_ID}"
GCP_SECRET_PROJ_ID_LOCATION     := "projects/${GCP_PROJECT_NUMBER}/secrets/${GCP_SECRET_NAME_OPENAI_PROJECT_ID}"
REPOSITORY_NAME                := env("REPOSITORY_NAME", "drivel-backend")
CLOUD_RUN_SERVICE              := env("CLOUD_RUN_SERVICE", "drivel-backend")
SECRET_VERSION                 := env("SECRET_VERSION", "latest")

# Full image name for GCR
GCR_IMAGE_NAME                 := GCR_HOSTNAME / GCP_PROJECT_ID / REPOSITORY_NAME / IMAGE_NAME

# api variables
server_uri          := "https://drivel-backend-k3u2qxk4cq-lz.a.run.app/api/v1"
chat_system_message := "You are a helpful assistant."
chat_message        := "What is 1 + 1?"
stt_audio_path      := "./tests/data/audio/me_gusta_aprender_idiomas.mp3"
tts_message         := "Hola, que tal?"
tts_language_code   := "es-ES"
tts_language_name   := "es-ES-Standard-B"
tts_output_path     := "tts-output.mp3"

default: get_root

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
        --update-secrets={{GCP_SECRET_ORG_ID_PATH}}={{GCP_SECRET_ORG_ID_LOCATION}}:{{SECRET_VERSION}} \
        --update-secrets={{GCP_SECRET_PROJ_ID_PATH}}={{GCP_SECRET_PROJ_ID_LOCATION}}:{{SECRET_VERSION}}
    echo "\033[1m\033[32mDeployment to Google Cloud Run successful.\033[0m"

@get_root:
    echo "\033[1m\033[33mCalling root endpoint...\033[0m"
    curl -X GET '{{server_uri}}/' \
        -H 'accept: application/json' -H 'Content-Type: application/json' && echo ""
    echo "\033[1m\033[32mSuccess.\033[0m"

@chat_response message=chat_message:
    echo "\033[1m\033[33mCalling chat responses...\033[0m"
    curl -s -X 'POST' \
      '{{server_uri}}/chat-responses/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{ \
            "max_tokens": 150, \
            "messages": [ \
              { \
                "content": "{{chat_system_message}}", \
                "role": "system" \
              }, \
              { \
                "content": "{{message}}", \
                "role": "user" \
              } \
            ], \
            "model": "gpt-3.5-turbo", \
            "n": 1 \
          }' \
    | jq -r ".[0].message.content"
    echo "\033[1m\033[32mSuccess.\033[0m"

@stt audio_file_path=stt_audio_path:
    echo "\033[1m\033[33mCalling speech-to-text for {{audio_file_path}}...\033[0m"
    curl -s -X 'POST' \
      '{{server_uri}}/speech-to-text/' \
      -H 'accept: application/json' \
      -H 'Content-Type: multipart/form-data' \
      -F 'audio_file=@{{audio_file_path}};type=audio/mpeg' \
    | jq -r ".text"
    echo "\033[1m\033[32mSuccess.\033[0m"

@tts message=tts_message audio_output_path=tts_output_path:
    echo "\033[1m\033[33mCalling speech-to-text...\033[0m"
    curl -s -X 'POST' \
      '{{server_uri}}/text-to-speech/' \
      -H 'accept: application/json' \
      -H 'Content-Type: application/json' \
      -d '{ \
            "text": "{{message}}", \
            "language_code": "{{tts_language_code}}", \
            "name": "{{tts_language_name}}" \
          }' \
       --output {{audio_output_path}}
    echo "\033[1m\033[32mSuccess saved audio file to {{audio_output_path}}.\033[0m"

@unit-test:
    pytest tests/unit --no-cov

@integration-test:
    pytest tests/integration --no-cov

@test:
    pytest
