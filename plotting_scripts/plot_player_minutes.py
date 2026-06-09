import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Infrastruktura z Twojego util.py (katalogi, tło)
from util import DATA_DIR, BG_PATH, PLOTS_DIR

MINUTE_STATS_PATH = DATA_DIR / "dfs" / "minute_stats_U-17.csv"

def generate_player_minutes_plot():
    print("Agregowanie minut i generowanie wykresu kadrowego (300 DPI)...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not MINUTE_STATS_PATH.exists():
        print(f"Błąd: Brak pliku {MINUTE_STATS_PATH}!")
        return

    # 1. Wczytanie danych (obsługujemy średnik jako separator)
    df = pd.read_csv(MINUTE_STATS_PATH, sep=";")
    
    # Czyszczenie nazw kolumn na wypadek spacji
    df.columns = [col.strip() for col in df.columns]
    
    # Tworzymy pełne imię i nazwisko do grupowania
    df["Player"] = df["firstname"].str.strip() + " " + df["lastname"].str.strip()
    
    # Agregacja minut dla każdego zawodnika
    df_grouped = df.groupby("Player")["duration"].sum().reset_index()
    
    # Sortujemy od największej liczby minut do najmniejszej
    df_grouped = df_grouped[df_grouped["duration"] > 0] # Najpierw sortujemy malejąco, żeby mieć ranking
    df_grouped = df_grouped.sort_values(by="duration", ascending=True) # Ascending=True, bo w poziomych paskach matplotlib rysuje od dołu do góry
    
    players = df_grouped["Player"].values
    minutes = df_grouped["duration"].values
    num_players = len(players)

    # 2. Inicjalizacja płótna 16:9 w Ultra HD (300 DPI)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    # Podkład pod prezentację
    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    # Tytuł wyśrodkowany na górze
    ax.text(960, 1010, "MINUTY ROZEGRANE W SEZONIE", 
            color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    # 3. GEOMETRIA I DOSKONAŁE WYRÓWNANIE
    # Tworzymy dedykowaną oś dla wykresu słupkowego, żeby kontrolować marginesy tekstu
    # [lewo, dół, szerokość, wysokość] w skali 0-1
    ax_bars = fig.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars.set_facecolor("none") # Przezroczyste tło, żeby widzieć background.png
    
    # Rysowanie poziomych, czystych białych pasków
    bars = ax_bars.barh(np.arange(num_players), minutes, color="#FFFFFF", height=0.55, edgecolor="none", zorder=3)

    # Dodanie dokładnej liczby minut na końcu każdego paska
    for bar in bars:
        width = bar.get_width()
        ax_bars.text(width + 25, bar.get_y() + bar.get_height()/2, f"{int(width)}'", 
                     color="#FFFFFF", fontsize=8, fontweight="bold", ha="left", va="center", alpha=0.8, zorder=4)

    # Ustawienia osi pionowej (Zawodnicy)
    ax_bars.set_yticks(np.arange(num_players))
    # Wyjustowanie nazwisk do prawej strony (Matplotlib robi to automatycznie przy podaniu listy do yticks)
    ax_bars.set_yticklabels(players, color="#FFFFFF", fontsize=9, fontweight="bold", ha="right")

    # Sztywne granice skali minutowej (sufit na 3200, żeby zmieściły się napisy końcowe)
    ax_bars.set_xlim(0, 3200)
    ax_bars.set_xticks([500, 1000, 1500, 2000, 2500, 3000])
    ax_bars.set_xticklabels(["500 min", "1000 min", "1500 min", "2000 min", "2500 min", "3000 min"], 
                            color="#AAAAAA", fontsize=9)

    # Pionowe drapieżne linie siatki (skala pomocnicza dla trenera)
    ax_bars.grid(axis="x", linestyle="--", alpha=0.15, color="#FFFFFF", zorder=1)

    # Usunięcie zbędnych obramowań osi z Matplotlib, żeby wykres był czysty i "wtopiony" w tło
    for spine in ["top", "right", "left", "bottom"]:
        ax_bars.spines[spine].set_visible(False)
        
    ax_bars.tick_params(axis="y", colors="#FFFFFF", pad=15) # Odstęp nazwisk od początku paska
    ax_bars.tick_params(axis="x", colors="#AAAAAA", pad=10)

    # Sztywne zamknięcie sceny głównej
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)

    output_path = PLOTS_DIR / "player_minutes_ranking.png"
    plt.savefig(output_path, dpi=300, pad_inches=0, transparent=False)
    plt.close()
    print(f"🚀 Sukces! Wykres minutowy zawodników w 300 DPI zapisano w: {output_path}")

if __name__ == "__main__":
    generate_player_minutes_plot()