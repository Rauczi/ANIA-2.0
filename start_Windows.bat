@echo off
title Transport na budowie - Uruchamianie
cd /d "%~dp0"

echo ===================================================
echo   Sprawdzanie srodowiska...
echo ===================================================

:: 1. Sprawdz, czy istnieje srodowisko wirtualne (.venv)
if not exist .venv (
    echo [1/2] Tworzenie srodowiska wirtualnego...
    py -m venv .venv
) else (
    echo [1/2] Srodowisko wirtualne juz istnieje. Pomijam.
)

:: 2. Aktywuj srodowisko
call .venv\Scripts\activate.bat

:: 3. Sprawdz WSZYSTKIE kluczowe biblioteki naraz
echo Sprawdzanie bibliotek...
py -c "import streamlit, pandas, openpyxl, ortools, requests, folium, streamlit_folium" >nul 2>&1

if errorlevel 1 (
    echo [2/2] Brakuje niektorych bibliotek. Instalowanie (to moze potrwac)...
    py -m pip install --upgrade pip
    pip install streamlit pandas openpyxl ortools requests folium streamlit-folium
) else (
    echo [2/2] Wszystkie biblioteki sa zainstalowane. Pomijam.
)

echo.
echo ===================================================
echo   Uruchamianie aplikacji...
echo ===================================================
echo.

:: 4. Uruchom Streamlit
streamlit run app.py

pause
