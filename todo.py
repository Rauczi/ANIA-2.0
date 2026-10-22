print("Witaj w menedżerze zadań!")
print("Wersja 0.1")
#!/usr/bin/env python3
"""Prosty menedżer zadań (to-do) w konsoli."""

def pokaz_menu():
    print("\n--- MENEDŻER ZADAŃ ---")
    print("1. Dodaj zadanie")
    print("2. Pokaż zadania")
    print("3. Wyjście")

def main():
    print("Witaj w menedżerze zadań!")
    while True:
        pokaz_menu()
        wybor = input("Wybierz opcję: ")

        if wybor == "1":
            print("→ [tu będzie dodawanie zadania]")
        elif wybor == "2":
            print("→ [tu będzie lista zadań]")
        elif wybor == "3":
            print("Do zobaczenia!")
            break
        else:
            print("Nieznana opcja, spróbuj ponownie.")

if __name__ == "__main__":
    main()
