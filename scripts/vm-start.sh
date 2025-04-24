#!/bin/bash

echo "Updating system packages..."

sudo apt update && sudo apt upgrade -y

echo "Installing Python and pip..."
sudo apt install -y python3 python3-pip git

echo "Cloning app repo..."
git clone https://github.com/Joshua-Lester3/DL-storyteller.git

echo "Installing Python dependencies..."
cd DL-storyteller/src
pip3 install -r requirements.txt

echo "Running Python app..."
python3 app.py
