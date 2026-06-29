#!/usr/bin/env sh
set -e

echo "Starting AI UPSC Study OS with Docker Compose..."
if command -v docker >/dev/null 2>&1; then
  if docker compose version >/dev/null 2>&1; then
    docker compose up --build
  elif command -v docker-compose >/dev/null 2>&1; then
    docker-compose up --build
  else
    echo "Error: Docker Compose is not installed. Please install Docker Compose."
    exit 1
  fi
else
  echo "Error: Docker is not installed. Please install Docker and Docker Compose."
  exit 1
fi
