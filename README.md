# ANIA-2.0
Powstał przy użyciu AI DeepSeek
Program ma za zadanie pomóc w organizacji zjazdów z budowy. Zanan jest lokalizacja startowa, ilość samochodów z określona ilością miejsc oraz ilość osób do rozwiezienia wraz z miejscami zamieszkania.
Program na wyliczyć sam najbardziej optymalną konfigurację, wysłania określonych samochodów tak by każdy samochód zrobił jak najmniejszą ilość kilometrów.

ANIA-2.0 powstała gdyż zawsze robiła to moja koleżanka Ania, teraz gdy ktoś inny musi to robić jest to zbyt skomplikowane stąd koniecznosć zaangażowania technologi.

################################################
# Transport na budowie

Aplikacja webowa do optymalizacji przydziału osób do samochodów na budowie.

## Opis

Program wczytuje dane z pliku Excel (samochody, osoby, baza), a następnie
przydziela osoby do samochodów tak, aby łączny dystans był jak najmniejszy.
Uwzględnia:

- liczbę miejsc w każdym samochodzie,
- przypisanie kierowcy do konkretnego pojazdu (na stałe),
- dwa tryby odległości: linia prosta lub rzeczywiste trasy drogowe (OSRM).

## Wymagania

- Python 3.12 lub 3.13 (na 3.14 OR-Tools może mieć problemy z typami)
- biblioteki: `pandas`, `openpyxl`, `ortools`, `streamlit`, `requests`

## Instalacja i uruchomienie



### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install pandas openpyxl ortools streamlit requests
streamlit run app.py
```
![hej](/zrzut_ekranu_1.png)
