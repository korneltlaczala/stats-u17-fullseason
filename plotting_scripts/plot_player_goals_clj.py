import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
import ast

# Infrastruktura zutil.py (katalogi, tło)
from util import DATA_DIR, BG_PATH, PLOTS_DIR

MINUTE_STATS_PATH = DATA_DIR / "dfs" / "minute_stats_U-17.csv"

def parse_and_count_goals(goals_str):
    """Parsuje kolumnę goals i zlicza bramki z obiektów json/listy."""
    if pd.isna(goals_str) or goals_str == '[]':
        return 0
    try:
        # Bezpieczna konwersja stringa na strukturę listy
        goals_list = ast.literal_eval(goals_str)
        return len(goals_list)
    except:
        return 0

def generate_player_goals_plot():
    print("Agregowanie bramek i generowanie klasyfikacji strzelców CLJ U-17 (300 DPI)...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not MINUTE_STATS_PATH.exists():
        print(f"Błąd: Brak pliku {MINUTE_STATS_PATH}!")
        return

    # 1. Wczytanie i filtrowanie danych pod kątem CLJ U-17
    df = pd.read_csv(MINUTE_STATS_PATH, sep=";")
    df.columns = [col.strip() for col in df.columns]
    
    df_clj = df[df["league"] == "CLJ U-17"].copy()
    
    # Mapowanie zawodnika i zliczanie bramek
    df_clj["Player"] = df_clj["firstname"].str.strip() + " " + df_clj["lastname"].str.strip()
    df_clj["goals_count"] = df_clj["goals"].apply(parse_and_count_goals)
    
    # Agregacja per zawodnik
    df_grouped = df_clj.groupby("Player")["goals_count"].sum().reset_index()
    
    # RĘCZNA KOREKTA TRENERA: Janek Tyszko (+1), Paweł Tyszko (-1)
    def apply_coaches_corrections(row):
        if row["Player"] == "Jan Tyszko":
            return row["goals_count"] + 1
        if row["Player"] == "Paweł Tyszko":
            return row["goals_count"] - 1
        return row["goals_count"]
        
    df_grouped["goals_count"] = df_grouped.apply(apply_coaches_corrections, axis=1)
    
    # Zostawiamy tylko zawodników z minimum 1 bramką i sortujemy rosnąco do poziomego wykresu
    df_grouped = df_grouped[df_grouped["goals_count"] > 0]
    df_grouped = df_grouped.sort_values(by="goals_count", ascending=True)
    
    players = df_grouped["Player"].values
    goals = df_grouped["goals_count"].values
    num_players = len(players)

    # 2. Inicjalizacja płótna 16:9 (300 DPI)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    # Tytuł slajdu
    ax.text(960, 1010, "KLASYFIKACJA STRZELCÓW: CENTRALNA LIGA JUNIORÓW U-17", 
            color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    # 3. GEOMETRIA (Identyczny układ, idealne wyjustowanie tekstów do prawej)
    ax_bars = fig.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars.set_facecolor("none")
    
    # Rysowanie czystych, grubych białych pasków
    bars = ax_bars.barh(np.arange(num_players), goals, color="#FFFFFF", height=0.55, edgecolor="none", zorder=3)

    # Liczba bramek na końcu każdego paska
    for bar in bars:
        width = bar.get_width()
        ax_bars.text(width + 0.2, bar.get_y() + bar.get_height()/2, f"{int(width)}", 
                     color="#00FF66", fontsize=10, fontweight="bold", ha="left", va="center", zorder=4)

    # Ustawienia osi pionowej (Nazwiska zawodników)
    ax_bars.set_yticks(np.arange(num_players))
    ax_bars.set_yticklabels(players, color="#FFFFFF", fontsize=10, fontweight="bold", ha="right")

    # Zakres i osie (maksymalnie np. 14 bramek, żeby paski ładnie wypełniły ekran)
    max_goals = int(max(goals)) if num_players > 0 else 10
    ax_bars.set_xlim(0, max_goals + 1)
    
    # Generujemy skoki na osi co 1 lub 2 bramki w zależności od skuteczności liderów
    ticks_step = 1 if max_goals <= 12 else 2
    xticks_vals = np.arange(0, max_goals + 1, ticks_step)
    ax_bars.set_xticks(xticks_vals)
    # ax_bars.set_xticklabels([f"{g} GOL" if g == 1 else f"{g} BRAMEK" for g in xticks_vals], color="#AAAAAA", fontsize=9)

    # Delikatna siatka pionowa
    ax_bars.grid(axis="x", linestyle="--", alpha=0.15, color="#FFFFFF", zorder=1)

    # Czyszczenie ramek systemowych matplotlib
    for spine in ["top", "right", "left", "bottom"]:
        ax_bars.spines[spine].set_visible(False)
        
    ax_bars.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars.tick_params(axis="x", colors="#AAAAAA", pad=10)

    # Zamknięcie sceny
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)

    output_path = PLOTS_DIR / "player_goals_clj_ranking.png"
    plt.savefig(output_path, dpi=300, pad_inches=0, transparent=False)
    plt.close()
    print(f"🚀 Klasyfikacja strzelców wygenerowana! Plik: {output_path}")

if __name__ == "__main__":
    generate_player_goals_plot()