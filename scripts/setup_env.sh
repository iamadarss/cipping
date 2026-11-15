#!/usr/bin/env bash
set -e

echo "========================================================"
echo "   UpClip Studio - Environment Setup & Hardware Detector"
echo "========================================================"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found. Please install Python 3.10+."
    exit 1
fi

# Create venv if needed
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment .venv..."
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "[*] Upgrading pip..."
pip install --upgrade pip

# Detect NVIDIA GPU
HAS_NVIDIA=0
if command -v nvidia-smi &> /dev/null; then
    HAS_NVIDIA=1
    echo "[OK] NVIDIA GPU detected via nvidia-smi!"
else
    echo "[i] No NVIDIA GPU detected. Standard CPU mode will be configured."
fi

INSTALL_GPU=0
if [ "$HAS_NVIDIA" -eq 1 ]; then
    read -r -p "Enable CUDA GPU acceleration (Y/n)? " USER_CHOICE
    USER_CHOICE=${USER_CHOICE:-Y}
    if [[ "$USER_CHOICE" =~ ^[Yy]$ ]]; then
        INSTALL_GPU=1
    fi
fi

if [ "$INSTALL_GPU" -eq 1 ]; then
    echo "[*] Installing GPU accelerated PyTorch (CUDA 12.1)..."
    pip install -r requirements-gpu.txt
else
    echo "[*] Installing CPU standard PyTorch..."
fi

echo "[*] Installing application dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "========================================================"
echo " Environment setup complete! Run 'python app.py' to start."
echo "========================================================"
