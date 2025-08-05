#!/bin/bash
set -e

# Start Ollama server
ollama serve &

# Wait for Ollama API to respond
while ! curl -s http://localhost:11434/api/tags >/dev/null; do
  echo "Waiting for Ollama to start..."
  sleep 1
done

# Pull the model with visible progress
echo "Pulling llama3.2:3b ..."
ollama pull llama3.2:3b

# Show loaded models
ollama list

# Keep container running with Ollama in foreground
wait