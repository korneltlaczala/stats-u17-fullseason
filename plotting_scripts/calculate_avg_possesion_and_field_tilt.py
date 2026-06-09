import pandas as pd
from util import DATA_DIR

def calculate_averages():
    stats_path = DATA_DIR / "dfs" / "stats_full.csv"
    if not stats_path.exists():
        print("Błąd: Brak pliku stats_full.csv")
        return

    df = pd.read_csv(stats_path)
    
    # Funkcja do czyszczenia procentów
    def clean_pct(val):
        if isinstance(val, str):
            return float(val.replace('%', '').strip())
        return float(val)

    # Czyszczenie danych
    df["pos"] = df["possessions"].apply(clean_pct)
    df["tilt"] = df["field_tilt"].apply(clean_pct)
    
    # Obliczenie średnich
    avg_possession = df["pos"].mean()
    avg_field_tilt = df["tilt"].mean()
    
    print("-" * 30)
    print("ŚREDNIE SEZONOWE (POLONIA WARSZAWA U17)")
    print("-" * 30)
    print(f"Średnie posiadanie piłki: {avg_possession:.2f}%")
    print(f"Średni Field Tilt:        {avg_field_tilt:.2f}%")
    print("-" * 30)

if __name__ == "__main__":
    calculate_averages()