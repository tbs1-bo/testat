#!/bin/sh

docker build -t testate:latest .

# check if container is already running
if [ "$(docker ps -q -f name=testate-dev)" ]; then
    echo "Stopping existing container..."
    docker stop testate-dev
    sleep 1
fi

docker run --rm -p 5000:5000 \
    -v $(pwd)/testate.db:/app/testate.db \
    --name testate-dev \
    testate:latest
