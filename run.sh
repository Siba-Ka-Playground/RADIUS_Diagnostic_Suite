#!/bin/bash
echo "[*] Initializing ZTAA RADIUS Diagnostic Suite..."

# 1. Detect and Install Python if missing
if ! command -v python3 &> /dev/null; then
    echo "[!] Python3 is not installed. Attempting automatic installation..."
    if command -v apt &> /dev/null; then
        sudo apt update && sudo apt install -y python3 python3-venv python3-pip
    elif command -v yum &> /dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v brew &> /dev/null; then
        brew install python
    else
        echo "[FATAL] Could not find a supported package manager. Please install Python3 manually."
        exit 1
    fi
fi

# 2. Setup Virtual Environment
echo "[*] Setting up local environment..."
python3 -m venv venv
source venv/bin/activate

# 3. Install Dependencies
echo "[*] Installing Python dependencies..."
pip install -r requirements.txt -q

# 4. Launch Application
echo "[*] Launching Diagnostic Console..."
python3 app.py