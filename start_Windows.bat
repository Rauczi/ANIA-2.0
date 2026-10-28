@echo off
title Transport na budowie - Uruchamianie

cd /d "%~dp0"

echo ===================================================
echo   Sprawdzanie srodowiska...
echo ===================================================

if not exist .venv (
    echo [1/2] Tworzenie srodowiska wirtualnego...
    py -m venv .venv
) else (
    echo [1/2] Srodowisko wirtualne juz istnieje. Pomijam.
)

call .venv\Scripts\activate.bat

echo Sprawdzanie bibliotek...
python -c "import streamlit, pandas, openpyxl, ortools, requests, folium, streamlit_folium" >nul 2>&1

if errorlevel 1 (
    echo [2/2] Brakuje niektorych bibliotek. Instalowanie...
    python -m pip install --upgrade pip
    python -m pip install streamlit pandas openpyxl ortools requests folium streamlit-folium
) else (
    echo [2/2] Wszystkie biblioteki sa zainstalowane. Pomijam.
)

echo.
echo ===================================================
echo   Uruchamianie aplikacji...
echo ===================================================
echo.

python -m streamlit run app.py --server.showEmailPrompt=False

pause
