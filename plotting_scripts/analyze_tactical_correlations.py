import pandas as pd
import numpy as np
from util import DATA_DIR

def analyze_tactical_data():
    stats_path = DATA_DIR / "dfs" / "stats_full.csv"
    df = pd.read_csv(stats_path)
    
    # Czyszczenie danych
    def clean_pct(val):
        if isinstance(val, str): return float(val.replace('%', '').strip())
        return float(val)

    df["pos"] = df["possessions"].apply(clean_pct)
    df["tilt"] = df["field_tilt"].apply(clean_pct)
    df["pts"] = df.apply(lambda row: 3 if row["goals"] > row["goals_opponent"] else (1 if row["goals"] == row["goals_opponent"] else 0), axis=1)
    
    # Podział na wyniki
    df_w = df[df["goals"] > df["goals_opponent"]]
    df_r = df[df["goals"] == df["goals_opponent"]]
    df_p = df[df["goals"] < df["goals_opponent"]]
    
    # 1. ŚREDNIE
    print(f"{'Wynik':<10} | {'Śr. Posiadanie':<15} | {'Śr. Field Tilt':<15}")
    print("-" * 45)
    for label, d in [("Wygrane", df_w), ("Remisy", df_r), ("Przegrane", df_p)]:
        print(f"{label:<10} | {d['pos'].mean():<15.2f} | {d['tilt'].mean():<15.2f}")
    
    # 2. KORELACJA (Tilt vs Punkty)
    correlation = df["tilt"].corr(df["pts"])
    print("\n" + "-" * 45)
    print(f"KORELACJA (Field Tilt vs Zdobyte Punkty): {correlation:.3f}")
    print("-" * 45)
    
    # 3. PROSTY WYKRES (Dla weryfikacji)
    # Używamy prostego plotu matplotlib, żebyś mógł rzucić okiem na trend
    import matplotlib.pyplot as plt
    plt.figure(figsize=(8, 5))
    plt.scatter(df["tilt"], df["pts"], color="cyan", alpha=0.6)
    plt.title("Weryfikacja: Field Tilt vs Zdobyte Punkty")
    plt.xlabel("Field Tilt (%)")
    plt.ylabel("Punkty w meczu (0, 1, 3)")
    plt.grid(True, linestyle=":", alpha=0.5)
    plt.show()

if __name__ == "__main__":
    analyze_tactical_data()