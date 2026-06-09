import os
import re
from pathlib import Path
import pandas as pd

# Ścieżki bazowe (zakładam uruchamianie z głównego folderu projektu)
BASE_DIR = Path(__file__).resolve().parent.parent
MATCHES_PATH = BASE_DIR / "data" / "dfs" / "matches.csv"
MOTOR_DIR = BASE_DIR / "data" / "motoryczne"
OUTPUT_PATH = BASE_DIR / "data" / "dfs" / "motor_stats_full.csv"


def load_matches():
    """Wczytuje mecze i przygotowuje pomocnicze kolumny do mapowania."""
    df = pd.read_csv(MATCHES_PATH)
    # Konwersja pzpn_id na string, na wypadek braków danych
    df["pzpn_id"] = df["pzpn_id"].astype(str)

    # Wyciągamy 'DD.MM' z kolumny date_time (np. 2026-05-16T12:00:00 -> 16.05)
    df["match_date_short"] = pd.to_datetime(df["date_time"]).dt.strftime(
        "%d.%m"
    )

    return df


def parse_file_name(file_name):
    """Wyciąga dzień i miesiąc z nazwy pliku za pomocą RegEx."""
    # Szukamy wzorca cyfr oddzielonych kropką np. 16.05 lub 28.02
    # match = re.search(r"(\d{2})\.(\d{2})", file_name)
    match = re.search(r"(\d{1,2})\.(\d{2})", file_name)
    if match:
        day = int(match.group(1))
        month = int(match.group(2))
        return f"{day:02d}.{month:02d}"
    return None


def process_motor_data():
    matches_df = load_matches()
    all_motor_records = []

    # Sprawdzamy czy folder istnieje
    if not MOTOR_DIR.exists():
        print(f"Błąd: Folder {MOTOR_DIR} nie istnieje!")
        return

    # Iteracja po wszystkich plikach CSV w folderze motorycznym
    for file_path in MOTOR_DIR.glob("*.csv"):
        file_name = file_path.name
        print(f"Przetwarzanie pliku: {file_name}")

        # Wyciągamy krótką datę (np. '16.05')
        date_short = parse_file_name(file_name)

        if not date_short:
            print(
                f"  -> Pomijam plik {file_name}: nie znaleziono daty w formacie DD.MM"
            )
            continue

        # Szukamy odpowiedniego meczu w matches.csv na podstawie daty krótkiej
        # Możesz też dodać sprawdzanie rywala, jeśli dwie daty w różnych latach by się pokryły
        matched_game = matches_df[matches_df["match_date_short"] == date_short]

        if matched_game.empty:
            print(
                f"  -> Ostrzeżenie: Brak dopasowania w matches.csv dla daty {date_short}!"
            )
            pzpn_id = "UNKNOWN"
            opponent = "UNKNOWN"
        else:
            pzpn_id = matched_game.iloc[0]["pzpn_id"]
            opponent = matched_game.iloc[0]["opponent"]

        # Wczytanie pliku motorycznego
        try:
            # Niektóre pliki z systemów GPS mogą mieć specyficzne kodowanie, np. utf-8 lub latin-1
            motor_df = pd.read_csv(file_path, encoding="utf-8")
        except Exception as e:
            try:
                motor_df = pd.read_csv(file_path, encoding="latin-1")
            except Exception as e2:
                print(f"  -> Nie udało się wczytać pliku {file_name}: {e2}")
                continue

        # Dodajemy kolumny identyfikacyjne na początku ramki
        motor_df.insert(0, "pzpn_id", pzpn_id)
        motor_df.insert(1, "opponent", opponent)
        motor_df.insert(2, "file_source", file_name)

        all_motor_records.append(motor_df)

    # Łączymy wszystkie ramki w jedną wielką bazę danych
    if all_motor_records:
        final_motor_df = pd.concat(all_motor_records, ignore_index=True)

        # Tworzymy folder docelowy dfs jeśli nie istnieje
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

        # Zapisujemy do pliku
        final_motor_df.to_csv(OUTPUT_PATH, index=False, encoding="utf-8")
        print(
            f"\nSukces! Połączono dane motoryczne. Wynik zapisano w: {OUTPUT_PATH}"
        )
        print(f"Łączna liczba wierszy: {len(final_motor_df)}")
    else:
        print("Nie znaleziono lub nie przeprocesowano żadnych danych.")


if __name__ == "__main__":
    process_motor_data()