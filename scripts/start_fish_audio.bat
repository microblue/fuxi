@echo off
REM 伏羲纪元 - Fish Audio 本地服务器启动脚本 (Windows)

setlocal enabledelayedexpansion

echo.
echo ====================================================
echo  Fish Audio Local Server Startup
echo ====================================================
echo.

set PORT=8000
set MODE=auto

if not "%FISH_AUDIO_PORT%"=="" set PORT=%FISH_AUDIO_PORT%
if not "%FISH_AUDIO_MODE%"=="" set MODE=%FISH_AUDIO_MODE%

echo Available startup methods:
echo   1) Docker (Recommended)
echo   2) From Source
echo   3) Python Package
echo.

set /p choice="Select method [1-3] (default: 1): "
if "%choice%"=="" set choice=1

if "%choice%"=="1" (
    echo.
    echo [1/3] Checking Docker...
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Docker is not installed
        echo Please visit: https://docs.docker.com/desktop/install/windows-install/
        pause
        exit /b 1
    )
    echo OK: Docker is available

    echo.
    echo [2/3] Pulling Fish Audio image...
    docker pull fishaudio/fish-speech:latest

    echo.
    echo [3/3] Starting Fish Audio service...
    docker run -p %PORT%:8000 ^
        -v fish_audio_models:/root/.cache/fish_speech/checkpoints ^
        --name fish_audio_server ^
        fishaudio/fish-speech:latest
) else if "%choice%"=="2" (
    echo.
    echo [1/4] Cloning repository...
    if exist "fish-speech" (
        echo WARNING: fish-speech directory already exists
    ) else (
        git clone https://github.com/fishaudio/fish-speech.git
    )
    cd fish-speech

    echo.
    echo [2/4] Creating virtual environment...
    if not exist "venv" (
        python -m venv venv
    )
    call venv\Scripts\activate.bat

    echo.
    echo [3/4] Installing dependencies...
    pip install -e .

    echo.
    echo [4/4] Starting server...
    python -m fish_speech.server --host 0.0.0.0 --port %PORT%
) else if "%choice%"=="3" (
    echo.
    echo [1/2] Installing fish-speech package...
    pip install fish-speech

    echo.
    echo [2/2] Starting server...
    python -m fish_speech.server --host 0.0.0.0 --port %PORT%
) else (
    echo ERROR: Invalid choice
    exit /b 1
)

echo.
echo ====================================================
echo SUCCESS: Fish Audio service started!
echo ====================================================
echo.
echo Service address: http://localhost:%PORT%
echo.
echo Next steps:
echo   1. Open another terminal window
echo   2. Set environment variable:
echo      set FISH_AUDIO_MODE=local
echo   3. Run voice generation:
echo      python -m pipeline.synth_voice ep002
echo.
pause
