Set-Location -Path $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\streamlit.exe")) {
    Write-Host "=== Pierwsze uruchomienie: tworzenie srodowiska i instalacja ==="
    python -m venv .venv
    & .venv\Scripts\Activate.ps1
    py -m pip install --upgrade pip
    pip install pandas openpyxl ortools streamlit requests folium streamlit-folium
} else {
    Write-Host "=== Srodowisko juz istnieje, pomijam instalacje ==="
    & .venv\Scripts\Activate.ps1
}

py -m streamlit run app.py --server.showEmailPrompt=False

pause
