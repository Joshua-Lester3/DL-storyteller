#!/bin/bash

echo "Updating system packages..."
sudo apt-mark hold linux-image-azure linux-headers-azure
sudo apt update && sudo apt upgrade -y

echo "Installing Python and pip..."
sudo apt install -y python3 python3-pip git python3.10-venv

echo "Cloning app repo... Do NOT expect changes in VM to be persistent across sessions."
git clone https://github.com/Joshua-Lester3/DL-storyteller.git
cd DL-storyteller
git reset --hard
git pull

echo "Installing Python dependencies..."
cd src
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

PORT=11434
LOGFILE=ollama.log

echo "Checking prerequisites..."
if ! command -v curl &>/dev/null; then
  echo "ERROR: 'curl' is required. Install it with your package manager." >&2
  exit 1
fi

if command -v ollama &>/dev/null; then
  echo "✓ Ollama is already installed."
else
  echo "Installing Ollama..."
  curl -fsSL https://ollama.com/install.sh | sudo sh
  echo "✓ Installation complete."
fi

echo
echo "Verifying Ollama CLI..."
if ! command -v ollama &>/dev/null; then
  echo "ERROR: Ollama command still not found. Aborting." >&2
  exit 1
fi

echo
# Optional: detect if a server is already running on $PORT
if lsof -iTCP:"$PORT" -sTCP:LISTEN &>/dev/null; then
  echo "✓ Ollama server already listening on port $PORT."
else
  echo "Starting Ollama server on port $PORT..."
  nohup ollama serve --gpu >"$LOGFILE" 2>&1 &
  # give it a moment to bind
  sleep 2
  if lsof -iTCP:"$PORT" -sTCP:LISTEN &>/dev/null; then
    echo "✓ Ollama server is now running."
  else
    echo "WARNING: Ollama server may not have started correctly. Check $LOGFILE."
  fi
fi

echo "Running Python app..."
~/DL-storyteller/src/.venv/bin/python3 app.py
