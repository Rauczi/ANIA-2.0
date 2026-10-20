#!/usr/bin/env python3
"""Program do optymalizacji transportu osób na budowie."""

import pandas as pd

PLIK = "dane_budowa.xlsx"

def wczytaj_dane():
    samochody = pd.read_excel(PLIK, sheet_name="Samochody")
    osoby = pd.read_excel(PLIK, sheet_name="Osoby")
    baza = pd.read_excel(PLIK, sheet_name="Baza")
    return samochody, osoby, baza

def main():

    samochody, osoby, baza = wczytaj_dane()

    print("=== SAMOCHODY ===")
    print(samochody)
    print("\n=== OSOBY ===")
    print(osoby)
    print("\n=== BAZA ===")
    print(baza)

    # Test odległości: baza → pierwsza osoba
    b = baza.iloc[0]
    o = osoby.iloc[0]
    d = odleglosc(b["Lat"], b["Lon"], o["Lat"], o["Lon"])
    print(f"\nOdległość baza → {o['Imie']} {o['Nazwisko']}: {d:.2f} km")

    macierz = zbuduj_macierz(osoby, baza)
    print("\n=== MACIERZ ODLEGŁOŚCI (km) ===")
    for row in macierz:
        print("  ".join(f"{x:6.2f}" for x in row))


    miejsca = list(samochody["Miejsca"])
    trasy = solve(macierz, miejsca)

    if trasy is None:
        print("\nNie znaleziono rozwiązania.")
    else:
        print("\n=== PRZYDZIAŁ OSÓB DO SAMOCHODÓW ===")
        for i, trasa in enumerate(trasy):
            rej = samochody.iloc[i]["Rejestracja"]
            # pomijamy bazę (0) na początku i końcu
            osoby_w_trasie = [osoby.iloc[node - 1] for node in trasa if node != 0]
            if not osoby_w_trasie:
                print(f"\nSamochód {rej}: (brak osób)")
                continue
            print(f"\nSamochód {rej} ({len(osoby_w_trasie)} osób):")
            for o in osoby_w_trasie:
                print(f"  - {o['Imie']} {o['Nazwisko']}")

import math

def odleglosc(lat1, lon1, lat2, lon2):
    """Odległość w linii prostej między dwoma punktami (w km, przybliżenie)."""
    R = 6371  # promień Ziemi w km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return 2 * R * math.asin(math.sqrt(a))

def zbuduj_macierz(osoby, baza):
    """Zwraca macierz odległości: punkt 0 = baza, 1..N = osoby."""
    punkty = [(baza.iloc[0]["Lat"], baza.iloc[0]["Lon"])]
    for _, o in osoby.iterrows():
        punkty.append((o["Lat"], o["Lon"]))

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

from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp


def solve(macierz_km, miejsca):
    """Rozwiązuje CVRP. Zwraca listę tras (każda trasa = lista indeksów punktów)."""
    # OR-Tools chce liczb całkowitych — przeliczamy km na metry
    macierz = [[int(round(d * 1000)) for d in row] for row in macierz_km]

    n = len(macierz)
    liczba_samochodow = len(miejsca)

    manager = pywrapcp.RoutingIndexManager(n, liczba_samochodow, 0)
    routing = pywrapcp.RoutingModel(manager)

    # Koszt przejazdu = odległość
    def callback(from_index, to_index):
        return macierz[manager.IndexToNode(from_index)][manager.IndexToNode(to_index)]

    cb = routing.RegisterTransitCallback(callback)
    routing.SetArcCostEvaluatorOfAllVehicles(cb)

    # Pojemność: każdy samochód ma limit miejsc
    def demand_callback(from_index):
        node = manager.IndexToNode(from_index)
        return 0 if node == 0 else 1  # baza = 0 osób, każda osoba = 1 miejsce

    dcb = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        dcb, 0, miejsca, True, "Pojemnosc"
    )

    # Parametry wyszukiwania
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
        trasa.append(manager.IndexToNode(index))  # powrót do bazy
        trasy.append(trasa)
    return trasy

if __name__ == "__main__":
    main()
