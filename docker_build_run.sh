#!/bin/sh

# abort on errors
set -e

# Configuration options
CONTAINER_NAME="testate-dev"
IMAGE_NAME="testate"
IMAGE_TAG="latest"
HOST_PORT=5000
CONTAINER_PORT=5000
DB_FILE="testate.db"
CONTAINER_DB_PATH="/app/testate.db"

# Build the image
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

# Check if container is already running
if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
    echo "Stopping existing container..."
    docker stop ${CONTAINER_NAME}
    sleep 1
fi

# Run the container
docker run --rm -p ${HOST_PORT}:${CONTAINER_PORT} \
    -v $(pwd)/${DB_FILE}:${CONTAINER_DB_PATH} \
    --name ${CONTAINER_NAME} \
    ${IMAGE_NAME}:${IMAGE_TAG}