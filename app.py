#!/usr/bin/env python3
"""Interfejs webowy (Streamlit) do optymalizacji transportu."""

import colorsys
import math

import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def generuj_kolory(n):
    """Generuje n równomiernie rozłożonych kolorów w HEX (HSV -> RGB)."""
    kolory = []
    for i in range(n):
        h = i / max(n, 1)
        r, g, b = colorsys.hsv_to_rgb(h, 0.75, 0.85)
        kolory.append(f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}")
    return kolory


def znajdz_emoji(hex_kolor):
    """Dopasowuje najbliższe emoji koloru do koloru HEX."""
    palety = [
        ("🔴", (255, 0, 0)),
        ("🔵", (0, 0, 255)),
        ("🟢", (0, 255, 0)),
        ("🟣", (128, 0, 128)),
        ("🟠", (255, 165, 0)),
        ("🟤", (139, 69, 19)),
        ("🔷", (0, 128, 128)),
        ("🟡", (255, 255, 0)),
        ("🟣", (255, 0, 255)),
    ]
    h = hex_kolor.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    najlepsze_emoji = "⚪"
    najmniejsza_roznica = float("inf")

    for emoji, (pr, pg, pb) in palety:
        roznica = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if roznica < najmniejsza_roznica:
            najmniejsza_roznica = roznica
            najlepsze_emoji = emoji

    return najlepsze_emoji


def odleglosc(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))


def pobierz_macierz_osrm(punkty):
    coords = ";".join(f"{lon},{lat}" for lat, lon in punkty)
    url = f"http://router.project-osrm.org/table/v1/driving/{coords}?annotations=distance"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        raise RuntimeError(f"Błąd OSRM: {e}")
    if "distances" not in data:
        raise RuntimeError(f"OSRM nie zwrócił macierzy: {data}")
    return [[d / 1000.0 for d in row] for row in data["distances"]]


def zbuduj_macierz(osoby, baza, uzyj_osrm=False):
    punkty = [(baza.iloc[0]["Lat"], baza.iloc[0]["Lon"])]
    for _, o in osoby.iterrows():
        punkty.append((o["Lat"], o["Lon"]))

    if uzyj_osrm:
        return pobierz_macierz_osrm(punkty)

    n = len(punkty)
    macierz = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                macierz[i][j] = odleglosc(
                    punkty[i][0], punkty[i][1],
                    punkty[j][0], punkty[j][1],
                )
    return macierz


def solve(macierz_km, miejsca, przypisania=None, wymus_wszystkie=False):
    """Rozwiązuje CVRP bez powrotu do bazy."""
    n_baz = len(macierz_km)

    macierz = []
    for row in macierz_km:
        macierz.append([int(round(d * 1000)) for d in row] + [0])
    macierz.append([0] * (n_baz + 1))

    n = n_baz + 1
    liczba_samochodow = len(miejsca)

    manager = pywrapcp.RoutingIndexManager(
        n, liczba_samochodow, [0] * liczba_samochodow, [n_baz] * liczba_samochodow
    )
    routing = pywrapcp.RoutingModel(manager)
        # Kara za uruchomienie samochodu
    if not wymus_wszystkie:
        # Wysoka kara (np. 1000 km w metrach = 1 000 000) sprawi, że solver
        # będzie upychał ludzi w mniej samochodów.
        kara = 1000000
        for v in range(liczba_samochodow):
            routing.SetFixedCostOfVehicle(kara, v)

    def callback(from_index, to_index):
        return macierz[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    cb = routing.RegisterTransitCallback(callback)
    routing.SetArcCostEvaluatorOfAllVehicles(cb)

    def demand_callback(from_index):
        node = manager.IndexToNode(from_index)
        return 0 if node in (0, n_baz) else 1

    dcb = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(dcb, 0, miejsca, True, "Pojemnosc")

    if przypisania:
        for osoba_idx, auto_idx in przypisania.items():
            node_index = manager.NodeToIndex(int(osoba_idx))
            routing.solver().Add(routing.VehicleVar(node_index) == int(auto_idx))

    params = pywrapcp.DefaultRoutingSearchParameters()
    params.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    )

    solution = routing.SolveWithParameters(params)
    if not solution:
        return None

    trasy = []
    for v in range(liczba_samochodow):
        index = routing.Start(v)
        trasa = []
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            if node != n_baz:
                trasa.append(node)
            index = solution.Value(routing.NextVar(index))
        trasy.append(trasa)
    return trasy


st.set_page_config(page_title="Transport na budowie", layout="wide")
st.title("🚗 Optymalizacja transportu osób na budowie")

plik = st.file_uploader("Wgraj plik Excel (dane_budowa.xlsx)", type=["xlsx"])

if plik is not None:
    try:
        # Odczytaj wszystkie arkusze, ignorując wielkość liter i spacje w nazwach
        xls = pd.ExcelFile(plik)
        arkusze = {nazwa.strip().lower(): nazwa for nazwa in xls.sheet_names}

        if "samochody" not in arkusze or "osoby" not in arkusze or "baza" not in arkusze:
            st.error("Błąd: Plik Excel musi zawierać arkusze o nazwach: 'Samochody', 'Osoby' oraz 'Baza'.")
            st.stop()

        samochody = pd.read_excel(xls, sheet_name=arkusze["samochody"])
        osoby = pd.read_excel(xls, sheet_name=arkusze["osoby"])
        baza = pd.read_excel(xls, sheet_name=arkusze["baza"])

    except Exception as e:
        st.error(f"Nie udało się odczytać pliku Excel. Upewnij się, że plik nie jest otwarty w innym programie. Szczegóły: {e}")
        st.stop()

    st.subheader("Dane wejściowe")
    col1, col2, col3 = st.columns(3)
    col1.write("**Samochody**")
    col1.dataframe(samochody)
    col2.write("**Osoby**")
    col2.dataframe(osoby)
    col3.write("**Baza**")
    col3.dataframe(baza)

    uzyj_osrm = st.checkbox("Użyj rzeczywistych tras drogowych (OSRM)", value=False)

    wymus_wszystkie = st.checkbox("Wymuś użycie wszystkich samochodów", value=False)

    if st.button("Oblicz przydział"):
        macierz_km = zbuduj_macierz(osoby, baza, uzyj_osrm=uzyj_osrm)
        miejsca = list(samochody["Miejsca"])

        przypisania = {}
        for i, row in osoby.iterrows():
            rej = str(row.get("Pojazd", "")).strip()
            if rej and rej.lower() != "nan":
                match = samochody.index[samochody["Rejestracja"] == rej].tolist()
                if match:
                    przypisania[i + 1] = int(match[0])
                else:
                    st.warning(f"Nie znaleziono samochodu o rejestracji: {rej}")

        trasy = solve(macierz_km,miejsca,przypisania,wymus_wszystkie=wymus_wszystkie)

        if trasy is None:
            st.error("Nie znaleziono rozwiązania.")
        else:
            st.subheader("Wynik")
            kolory = generuj_kolory(len(trasy))

            for i, trasa in enumerate(trasy):
                rej = samochody.iloc[i]["Rejestracja"]
                osoby_w_trasie = [node for node in trasa if node != 0]
                kolor = kolory[i]
                ikona = znajdz_emoji(kolor)

                naglowek = f"{ikona} {i + 1}. Samochód {rej} — {len(osoby_w_trasie)} osób"

                with st.expander(naglowek):
                    st.markdown(
                        f"<div style='border-left: 6px solid {kolor}; "
                        f"height: 20px; margin-bottom: 8px;'></div>",
                        unsafe_allow_html=True,
                    )

                    if not osoby_w_trasie:
                        st.write("(brak osób)")
                        continue

                    lacznie = 0.0
                    poprzedni = trasa[0]
                    for krok, node in enumerate(trasa[1:], start=1):
                        dystans = macierz_km[poprzedni][node]
                        lacznie += dystans
                        o = osoby.iloc[node - 1]
                        kierowca = str(o.get("Pojazd", "")).strip() == rej
                        znacznik = " 🚗 (kierowca)" if kierowca else ""
                        st.write(
                            f"  {krok}. {o['Imie']} {o['Nazwisko']}{znacznik}"
                            f" — {dystans:.2f} km"
                        )
                        poprzedni = node

                    st.write(f"**Łącznie: {lacznie:.2f} km**")

            st.subheader("🗺️ Trasy na mapie")

            punkty = [(baza.iloc[0]["Lat"], baza.iloc[0]["Lon"])]
            for _, o in osoby.iterrows():
                punkty.append((o["Lat"], o["Lon"]))

            center_lat = sum(p[0] for p in punkty) / len(punkty)
            center_lon = sum(p[1] for p in punkty) / len(punkty)

            m = folium.Map(location=[center_lat, center_lon], zoom_start=12, tiles="OpenStreetMap")

            folium.Marker(
                location=[baza.iloc[0]["Lat"], baza.iloc[0]["Lon"]],
                popup="Baza",
                icon=folium.Icon(color="black", icon="home")
            ).add_to(m)

            for i, trasa in enumerate(trasy):
                if len(trasa) <= 1:
                    continue

                wspolrzedne = []
                for node_idx in trasa:
                    if node_idx == 0:
                        lat, lon = baza.iloc[0]["Lat"], baza.iloc[0]["Lon"]
                    else:
                        o = osoby.iloc[node_idx - 1]
                        lat, lon = o["Lat"], o["Lon"]
                    wspolrzedne.append(f"{lon},{lat}")

                url = (
                    "http://router.project-osrm.org/route/v1/driving/"
                    + ";".join(wspolrzedne)
                    + "?geometries=geojson&overview=full"
                )
                try:
                    resp = requests.get(url, timeout=10)
                    data = resp.json()
                    if data.get("routes"):
                        geom = data["routes"][0]["geometry"]["coordinates"]
                        folium_coords = [[lat, lon] for lon, lat in geom]
                        kolor = kolory[i]
                        folium.PolyLine(
                            folium_coords,
                            color=kolor,
                            weight=4,
                            opacity=0.8,
                            tooltip=f"Samochód {samochody.iloc[i]['Rejestracja']}"
                        ).add_to(m)
                except Exception as e:
                    st.warning(f"Nie udało się pobrać trasy dla samochodu {i+1}: {e}")

            for _, o in osoby.iterrows():
                folium.CircleMarker(
                    location=[o["Lat"], o["Lon"]],
                    radius=5,
                    color="gray",
                    fill=True,
                    popup=f"{o['Imie']} {o['Nazwisko']}"
                ).add_to(m)

            st_folium(m, width=700, height=500, returned_objects=[])

# --- Stopka: autor i licencja ---
st.markdown("---")

with st.expander("ℹ️ O projekcie i licencji"):
    st.markdown("""
    **Autor:** Michał Smyrek przy pomocy AI DeepSeek - https://chat.deepseek.com/

    **Licencja:** MIT

    Licencja MIT pozwala na:
    - **Commercial use** — użycie komercyjne
    - **Modification** — modyfikowanie kodu
    - **Distribution** — rozpowszechnianie
    - **Private use** — użytek prywatny

    Kod źródłowy: [GitHub](https://github.com/Rauczi/ANIA-2.0)
    """)

st.caption("Autor: Michał Smyrek. · Licencja MIT · commercial use, modification, distribution, private use")
