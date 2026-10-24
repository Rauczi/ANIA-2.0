#!/bin/bash

# Przejdź do katalogu, w którym znajduje się skrypt
cd "$(dirname "$0")" || exit 1

# KLUCZOWY PUNKT: sprawdź, czy środowisko jest już gotowe
if [ ! -f ".venv/bin/streamlit" ]; then
    echo "=== Pierwsze uruchomienie: tworzenie środowiska i instalacja zależności ==="
    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install --upgrade pip
    pip install pandas openpyxl ortools streamlit requests folium streamlit-folium
else
    echo "=== Środowisko już istnieje, pomijam instalację ==="
    source .venv/bin/activate
fi

# Uruchom aplikację
streamlit run app.py
