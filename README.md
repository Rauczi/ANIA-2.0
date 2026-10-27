# ANIA-2.0
Powstał przy użyciu AI DeepSeek
Program ma za zadanie pomóc w organizacji zjazdów z budowy. Zanan jest lokalizacja startowa, ilość samochodów z określona ilością miejsc oraz ilość osób do rozwiezienia wraz z miejscami zamieszkania.
Program na wyliczyć sam najbardziej optymalną konfigurację, wysłania określonych samochodów tak by każdy samochód zrobił jak najmniejszą ilość kilometrów.
Można na sztywno przypisać daną osobę do samochodu przypisując przy niej w kolumnie numer rejestracyjny

ANIA-2.0 powstała gdyż zawsze robiła to moja koleżanka Ania, teraz gdy ktoś inny musi to robić jest to zbyt skomplikowane stąd koniecznosć zaangażowania technologi.
Aktualizacja 0.1 22.10.2026
dodano:

* nie wymaga powrotu do bazy (samochód zostaje u ostatniego pasażera),
* pokazuje numerowaną listę z dystansami i mapę z trasami.

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
- aplikacja generuje mapę z trasami, koloruje samochody i nie wymaga powrotu do bazy.
- aplikacja zapamiętuje stan po odświeżeniu strony
- działa eksport wyników do arkusza excel

## Wymagania

- Python 3.12 lub 3.13 (na 3.14 OR-Tools może mieć problemy z typami)
- biblioteki: `pandas`, `openpyxl`, `ortools`, `streamlit`, `requests`

## Instalacja i uruchomienie

Należy pobrać plik dane_budowy.xlsx - uzupełnić go danymi i uruchomić poniży link
https://ania-2pxe.streamlit.app/     - na każdym komputerze

Lub uruchomienie poprzez pliki wykonywalne:
start_Linux.sh < dla Linux
start_Windows.bat < dla Windows

### Linux / Windows - konsola

```bash
Linux:
| - Terminal Pierwsze uruchomienie
|   Przechodzimy do folderu w którym mamy folder z programem:
|       cd /ścieżka/do/ANIA-2.0
|   Następnie instalujemy wszytskie potrzebne dodatki:
|       1.  python3 -m venv .venv
|       2.  source .venv/bin/activate
|       3.  python -m pip install --upgrade pip
|       4.  pip install pandas openpyxl ortools streamlit requests folium streamlit-folium
|   Następnie uruchamiamy aplikację:
|       streamlit run app.py
|
|
|-  Kolejne Uruchamianie:
|       1.  cd /ścieżka/do/ANIA-2.0
|       2.  source .venv/bin/activate
|       3.  streamlit run app.py

Windows:
| - Powershell Pierwsze uruchomienie:
|   Przechodzimy do folderu w którym mamy folder z programem:
|       cd C:\ścieżka\do\ANIA-2.0
|   Następnie instalujemy wszytskie potrzebne dodatki:
|       1.  python -m venv .venv
|       2.  .venv\Scripts\activate
|       3.  pip install pandas openpyxl ortools streamlit requests
|       4.  python -m pip install --upgrade pip
|       5.  pip install folium streamlit-folium
|   Następnie uruchamiamy aplikację:
|       py -m streamlit run app.py --server.showEmailPrompt=False
|-  Kolejne Uruchamianie:
|       1.  C:\ścieżka\do\ANIA-2.0
|       2.  py -m venv .venv
|       3.  py -m streamlit run app.py --server.showEmailPrompt=False

````````````````````````````````````````````````````
######### Przebitka z programu ##########
![hej](/zrzut_ekranu_1.png)
