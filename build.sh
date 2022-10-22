#!/bin/bash
VERSION=$(cat pyproject.toml | grep '^version = .*$' | sed 's/^version = "\(.*\)"$/\1/g')  #-$(printf %x "$(date +%s)")
DOCKER_REPO="rincewindwizzard/mqtt-presence-checker"

# replace with docker if needed
PODMAN=podman

poetry build
poetry publish

echo "Building version v$VERSION"
echo "Docker Image: $DOCKER_REPO:$VERSION"

# Build docker image
$PODMAN build -t "$DOCKER_REPO:latest" -t "$DOCKER_REPO:$VERSION" .

$PODMAN push "$DOCKER_REPO:latest"
$PODMAN push "$DOCKER_REPO:$VERSION"