#!/bin/bash

echo "Updating system packages..."
sudo apt-mark hold linux-image-azure linux-headers-azure linux-modules-azure
sudo apt update && sudo apt upgrade -y

echo "Installing Python and pip..."
sudo apt install -y python3 python3-pip git python3.10-venv

echo "Cloning app repo..."
git clone https://github.com/Joshua-Lester3/DL-storyteller.git

echo "Installing Python dependencies..."
cd DL-storyteller/src
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

echo "Running Python app..."
sudo ~/DL-storyteller/.venv/bin/python app.py
