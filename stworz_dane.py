import pandas as pd

samochody = pd.DataFrame({
    "ID": [1, 2, 3],
    "Rejestracja": ["WA12345", "WA67890", "WK11111"],
    "Miejsca": [4, 3, 5],
})


osoby = pd.DataFrame({
    "Imie": ["Anna", "Jan", "Kasia", "Piotr", "Marek", "Ewa"],
    "Nazwisko": ["Kowalska", "Nowak", "Wiśniewska", "Zieliński", "Lewandowski", "Szymańska"],
    "Lat": [52.2297, 52.2370, 52.2450, 52.2500, 52.2600, 52.2700],
    "Lon": [21.0122, 21.0200, 21.0300, 21.0400, 21.0500, 21.0600],
    "Pojazd": ["WA12345", "", "WK11111", "", "", ""],

})

baza = pd.DataFrame({
    "Nazwa": ["Baza budowy"],
    "Lat": [52.2200],
    "Lon": [21.0000],
})

with pd.ExcelWriter("dane_budowa.xlsx") as writer:
    samochody.to_excel(writer, sheet_name="Samochody", index=False)
    osoby.to_excel(writer, sheet_name="Osoby", index=False)
    baza.to_excel(writer, sheet_name="Baza", index=False)

print("Plik dane_budowa.xlsx utworzony!")
