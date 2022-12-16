#!/bin/bash
set -eu

DOCKER_IMAGE_NAME=notifications-api

source environment.sh

# this script should be run from within your virtualenv so you can access the aws cli
AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID:-"$(aws configure get aws_access_key_id)"}
AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY:-"$(aws configure get aws_secret_access_key)"}
SQLALCHEMY_DATABASE_URI=${SQLALCHEMY_DATABASE_URI:-"postgresql://postgres@host.docker.internal/notification_api"}
REDIS_URL=${REDIS_URL:-"redis://host.docker.internal:6379"}
API_HOST_NAME=${API_HOST_NAME:-"http://host.docker.internal:6011"}

# we always expose port 6011 but it is only really needed when running the flask API
docker run -it --rm \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e SQLALCHEMY_DATABASE_URI=$SQLALCHEMY_DATABASE_URI \
  -e REDIS_ENABLED=${REDIS_ENABLED:-0} \
  -e REDIS_URL=$REDIS_URL \
  -e API_HOST_NAME=$API_HOST_NAME \
  -e NOTIFY_ENVIRONMENT=$NOTIFY_ENVIRONMENT \
  -e MMG_API_KEY=$MMG_API_KEY \
  -e FIRETEXT_API_KEY=$FIRETEXT_API_KEY \
  -e NOTIFICATION_QUEUE_PREFIX=$NOTIFICATION_QUEUE_PREFIX \
  -e FLASK_APP=$FLASK_APP \
  -e FLASK_DEBUG=$FLASK_DEBUG \
  -e WERKZEUG_DEBUG_PIN=$WERKZEUG_DEBUG_PIN \
  -p 6011:6011 \
  -v $(pwd):/home/vcap/app \
  ${DOCKER_IMAGE_NAME} \
  ${@}
