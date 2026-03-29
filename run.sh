#!/bin/bash
echo "🚀 Starting PyRufus GRUB Edition..."
echo "⚠️  Please run with sudo for USB access: sudo ./run.sh"
echo ""

# Create venv if needed
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
source venv/bin/activate
pip install -r requirements.txt

# Run
python3 main.py
