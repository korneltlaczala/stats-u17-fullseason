import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Infrastruktura z util.py
from util import DATA_DIR, BG_PATH, PLOTS_DIR

MINUTE_STATS_PATH = DATA_DIR / "dfs" / "minute_stats_U-17.csv"

def generate_player_minutes_grouped_plot():
    print("Agregowanie aktywnych minut z podziałem na rozgrywki (300 DPI)...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not MINUTE_STATS_PATH.exists():
        print(f"Błąd: Brak pliku {MINUTE_STATS_PATH}!")
        return

    # 1. Wczytanie i czyszczenie danych
    df = pd.read_csv(MINUTE_STATS_PATH, sep=";")
    df.columns = [col.strip() for col in df.columns]
    
    # Tworzymy pełne imię i nazwisko
    df["Player"] = df["firstname"].str.strip() + " " + df["lastname"].str.strip()
    
    # Grupowanie po zawodniku i lidze
    df_grouped = df.groupby(["Player", "league"])["duration"].sum().unstack(fill_value=0)
    
    # Obliczamy sumę minut, żeby posortować zawodników od największej
    df_grouped["Total"] = df_grouped.sum(axis=1)
    df_grouped = df_grouped[df_grouped["Total"] > 0]
    df_grouped = df_grouped.sort_values(by="Total", ascending=True) # Od dołu do góry w barh
    
    players = df_grouped.index.values
    total_minutes = df_grouped["Total"].values
    num_players = len(players)
    
    # Usuwamy kolumnę Total, zostawiając tylko czyste ligi
    df_leagues = df_grouped.drop(columns=["Total"])
    
    # POPRAWKA 1: Usuwamy z ramki danych te ligi, które w całym sezonie mają łącznie 0 minut
    df_leagues = df_leagues.loc[:, (df_leagues != 0).any()]
    available_leagues = df_leagues.columns.tolist()

    # 2. Inicjalizacja płótna 16:9 w Ultra HD (300 DPI)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    # Tytuł
    ax.text(960, 1010, "MINUTY ROZEGRANE W SEZONIE Z PODZIAŁEM NA ROZGRYWKI", 
            color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    # 3. GEOMETRIA I WYKRES SKUMULOWANY
    ax_bars = fig.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars.set_facecolor("none")
    
    # POPRAWKA 2: Wyrazista, jasna i kontrastowa paleta barw (koniec ze zlewającymi się szarościami)
    bright_colors = ["#FFFFFF", "#00E5FF", "#FFD600", "#E040FB", "#FF6E40"]
    colors_map = {}
    color_idx = 0
    
    for league in available_leagues:
        if league == "CLJ U-17":
            colors_map[league] = "#00FF66" # Nasz neonowy zielony zostaje jako baza
        else:
            colors_map[league] = bright_colors[color_idx % len(bright_colors)]
            color_idx += 1

    # Słowniki mapowania nazw lig na krótkie labele tekstowe wewnątrz pasków
    league_short_labels = {
        "CLJ U-17": "CLJ U17",
        "CLJ U-19": "CLJ U19",
        "Ekstraliga U-16": "EXT U16",
        "Ekstraliga U-16 RW": "EXT U16 RW",
        "Liga okręgowa": "OKR",
        "I liga": "I LIGA",
        "V liga": "V LIGA",
        "Puchar Polski": "PP"
    }

    # Rysowanie pasków warstwowych
    left_positions = np.zeros(num_players)
    y_positions = np.arange(num_players)
    
    for league in available_leagues:
        league_mins = df_leagues[league].values
        ax_bars.barh(y_positions, league_mins, left=left_positions, 
                     color=colors_map[league], height=0.58, edgecolor="none", label=league, zorder=3)
        
        # POPRAWKA 3: Dodawanie czarnych napisów z nazwą ligi wewnątrz stripsów
        for i in range(num_players):
            current_mins = league_mins[i]
            # Tekst dodajemy tylko, jeśli pasek ma minimum 100 minut (żeby nie nachodził na krawędzie)
            if current_mins >= 100:
                # Środek aktualnego segmentu
                text_x = left_positions[i] + (current_mins / 2)
                short_text = league_short_labels.get(league, league[:5].upper())
                ax_bars.text(text_x, i, short_text, color="#000000", fontsize=6, 
                             fontweight="bold", ha="center", va="center", zorder=4)
                
        left_positions += league_mins

    # Łączna liczba minut na samym końcu paska
    for i in range(num_players):
        if total_minutes[i] > 0:
            ax_bars.text(total_minutes[i] + 25, i, f"{int(total_minutes[i])}'", 
                         color="#FFFFFF", fontsize=8, fontweight="bold", ha="left", va="center", alpha=0.8, zorder=4)

    # Ustawienia osi zawodników
    ax_bars.set_yticks(y_positions)
    ax_bars.set_yticklabels(players, color="#FFFFFF", fontsize=9, fontweight="bold", ha="right")

    # Sztywne granice skali
    ax_bars.set_xlim(0, 3200)
    ax_bars.set_xticks([500, 1000, 1500, 2000, 2500, 3000])
    ax_bars.set_xticklabels(["500 min", "1000 min", "1500 min", "2000 min", "2500 min", "3000 min"], 
                            color="#AAAAAA", fontsize=9)

    # Delikatna siatka
    ax_bars.grid(axis="x", linestyle="--", alpha=0.12, color="#FFFFFF", zorder=1)

    # Ukrywanie obramowań
    for spine in ["top", "right", "left", "bottom"]:
        ax_bars.spines[spine].set_visible(False)
        
    ax_bars.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars.tick_params(axis="x", colors="#AAAAAA", pad=10)

    # Wyczyszczona legenda (tylko z aktywnymi ligami)
    legend = ax_bars.legend(loc="lower right", bbox_to_anchor=(0.98, 0.02), 
                            frameon=True, facecolor="#1A1A1A", edgecolor="#444444", 
                            fontsize=9, labelcolor="#FFFFFF")
    legend.set_zorder(5)

    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)

    output_path = PLOTS_DIR / "player_minutes_grouped.png"
    plt.savefig(output_path, dpi=300, pad_inches=0, transparent=False)
    plt.close()
    print(f"🚀 Gotowe! Wyczyszczony wykres rankingowy zapisany w: {output_path}")

if __name__ == "__main__":
    generate_player_minutes_grouped_plot()