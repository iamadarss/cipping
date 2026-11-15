@echo off
setlocal enabledelayedexpansion

echo ========================================================
echo    UpClip Studio - Environment Setup & Hardware Detector
echo ========================================================

:: Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ and add it to PATH.
    exit /b 1
)

:: Create Virtual Environment if not exists
if not exist ".venv" (
    echo [*] Creating virtual environment .venv...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo [*] Upgrading pip...
python -m pip install --upgrade pip

:: Detect NVIDIA GPU
set HAS_NVIDIA=0
where nvidia-smi >nul 2>nul
if %errorlevel% equ 0 (
    set HAS_NVIDIA=1
    echo [OK] NVIDIA GPU detected via nvidia-smi!
) else (
    echo [i] No NVIDIA GPU detected. Standard CPU mode will be configured.
)

:: Prompt or choose build
set INSTALL_GPU=0
if "%HAS_NVIDIA%"=="1" (
    echo.
    set /p USER_CHOICE="Enable CUDA GPU acceleration (Y/n)? "
    if /i "!USER_CHOICE!"=="y" set INSTALL_GPU=1
    if "!USER_CHOICE!"=="" set INSTALL_GPU=1
)

if "%INSTALL_GPU%"=="1" (
    echo [*] Installing GPU accelerated PyTorch (CUDA 12.1)...
    pip install -r requirements-gpu.txt
) else (
    echo [*] Installing CPU standard PyTorch...
)

echo [*] Installing application dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo ========================================================
echo  Environment setup complete! Run 'python app.py' to start.
echo ========================================================
