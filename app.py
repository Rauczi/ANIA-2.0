#!/usr/bin/env python3
"""Interfejs webowy (Streamlit) do optymalizacji transportu."""

import math

import requests

import pandas as pd
import streamlit as st

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def odleglosc(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))

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




def pobierz_macierz_osrm(punkty):
    """Pobiera macierz odległości z OSRM (w km).
    punkty: lista krotek (lat, lon).
    """
    # OSRM oczekuje lon,lat (odwrotnie niż my)
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

    # OSRM zwraca metry — zamieniamy na km
    macierz = [[d / 1000.0 for d in row] for row in data["distances"]]
    return macierz


def solve(macierz_km, miejsca, przypisania=None):
    macierz = [[int(round(d * 1000)) for d in row] for row in macierz_km]
    n = len(macierz)
    liczba_samochodow = len(miejsca)

    manager = pywrapcp.RoutingIndexManager(n, liczba_samochodow, 0)
    routing = pywrapcp.RoutingModel(manager)

    def callback(from_index, to_index):
        return macierz[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    cb = routing.RegisterTransitCallback(callback)
    routing.SetArcCostEvaluatorOfAllVehicles(cb)

    def demand_callback(from_index):
        node = manager.IndexToNode(from_index)
        return 0 if node == 0 else 1

    dcb = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(dcb, 0, miejsca, True, "Pojemnosc")

    if przypisania:
        for osoba_idx, auto_idx in przypisania.items():
            node_index = manager.NodeToIndex(int(osoba_idx))
            routing.solver().Add(
                routing.VehicleVar(node_index) == int(auto_idx)
            )


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
            trasa.append(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        trasa.append(manager.IndexToNode(index))
        trasy.append(trasa)
    return trasy


st.set_page_config(page_title="Transport na budowie", layout="wide")
st.title("🚗 Optymalizacja transportu osób na budowie")

plik = st.file_uploader("Wgraj plik Excel (dane_budowa.xlsx)", type=["xlsx"])

if plik is not None:
    samochody = pd.read_excel(plik, sheet_name="Samochody")
    osoby = pd.read_excel(plik, sheet_name="Osoby")
    baza = pd.read_excel(plik, sheet_name="Baza")

    st.subheader("Dane wejściowe")
    col1, col2, col3 = st.columns(3)
    col1.write("**Samochody**")
    col1.dataframe(samochody)
    col2.write("**Osoby**")
    col2.dataframe(osoby)
    col3.write("**Baza**")
    col3.dataframe(baza)

    uzyj_osrm = st.checkbox("Użyj rzeczywistych tras drogowych (OSRM)", value=False)

    if st.button("Oblicz przydział"):
        macierz = zbuduj_macierz(osoby, baza, uzyj_osrm=uzyj_osrm)
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

        trasy = solve(macierz, miejsca, przypisania)

        if trasy is None:
            st.error("Nie znaleziono rozwiązania.")
        else:
            st.subheader("Wynik")
            for i, trasa in enumerate(trasy):
                rej = samochody.iloc[i]["Rejestracja"]
                osoby_w_trasie = [osoby.iloc[node - 1] for node in trasa if node != 0]
                with st.expander(f"Samochód {rej} — {len(osoby_w_trasie)} osób"):
                    if not osoby_w_trasie:
                        st.write("(brak osób)")
                    else:
                        for o in osoby_w_trasie:
                            kierowca = str(o.get("Pojazd", "")).strip() == rej
                            znacznik = " 🚗 (kierowca)" if kierowca else ""
                            st.write(f"- {o['Imie']} {o['Nazwisko']}{znacznik}")
