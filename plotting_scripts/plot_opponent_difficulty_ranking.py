import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Importujemy sprawdzoną infrastrukturę z Twojego util.py
from util import (
    MATCHES_CSV_PATH, BG_PATH, PLOTS_DIR, 
    add_club_logo, COLOR_WIN, COLOR_LOSS
)

# CENTRALNA KONFIGURACJA PALETY (Tylko bramki od środka!)
COLOR_GOALS_FOR = "#00FF66"  # Soczysty zielony dla bramek strzelonych (w prawo)
COLOR_GOALS_AG = "#FF3333"   # Agresywny czerwony dla bramek straconych (w lewo)
COLOR_BAR_BG = "#1A1A1A"      # Głęboki grafit wnętrza pasów
COLOR_CONTAINER_BORDER = "#333333" # Kolor ramki scalającej cały komponent
FONT_COLOR = "#FFFFFF"

def calculate_opponent_stats():
    """Wczytuje mecze, agreguje punkty oraz bramki w dwumeczach z każdym rywalem."""
    df = pd.read_csv(MATCHES_CSV_PATH)
    
    def get_points(row):
        gf = int(row["goals_for"])
        ga = int(row["goals_against"])
        if gf > ga: return 3
        elif gf == ga: return 1
        return 0
        
    df["points"] = df.apply(get_points, axis=1)
    
    grouped = df.groupby("opponent").agg(
        total_points=("points", "sum"),
        goals_scored=("goals_for", "sum"),
        goals_conceded=("goals_against", "sum"),
        matches_played=("opponent", "count")
    ).reset_index()
    
    grouped["goal_diff"] = grouped["goals_scored"] - grouped["goals_conceded"]
    
    # Sortowanie niezmienne: punkty -> bilans bramek -> bramki strzelone
    grouped = grouped.sort_values(
        by=["total_points", "goal_diff", "goals_scored"], 
        ascending=[False, False, False]
    ).reset_index(drop=True)
    
    return grouped

def generate_opponent_ranking():
    print("Generowanie czystego, jednopasmowego wykresu bilansu dwumeczów...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not MATCHES_CSV_PATH.exists():
        print(f"Błąd: Brak pliku {MATCHES_CSV_PATH}!")
        return
        
    opponents_df = calculate_opponent_stats()
    num_opponents = len(opponents_df)
    
    if num_opponents == 0:
        print("Brak danych o przeciwnikach.")
        return
        
    # Szukamy maksa bramkowego do symetrycznej skali od środka
    max_goals_in_series = max(opponents_df["goals_scored"].max(), opponents_df["goals_conceded"].max())
    if max_goals_in_series < 1:
        max_goals_in_series = 1

    # Inicjalizacja płótna 16:9 Full HD
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    
    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])
    
    # Nagłówek główny grafiki
    ax.text(340, 990, "TRUDNOŚĆ DWUMECZÓW — ZDOBYTE PUNKTY I BILANS BRAMKOWY", 
            color=FONT_COLOR, fontsize=22, fontweight="bold", ha="left")
    
    # PARAMETRY GEOMETRII (Dopasowane pod jeden pasek bramkowy i nazwę)
    start_y = 850          # Wysokość początkowa pierwszego wiersza
    bar_gap = 56           # Idealny pionowy skok między rywalami
    start_x_bar = 340      # Pozycja X rozpoczęcia paska
    max_bar_width = 960    # Szerokość korytarza bramkowego
    
    bar_height = 16        # Minimalnie grubszy pasek bramek, skoro jest sam
    text_height_offset = 18 # Odstęp dla nazwy zespołu nad paskiem
    padding = 6            # Margines dekoracyjnej obwódki kontenera
    
    center_x_goals = start_x_bar + (max_bar_width / 2)

    for idx, row in opponents_df.iterrows():
        # Obliczanie Y pod jeden pasek i tekst nad nim
        y_container_bottom = start_y - (idx * bar_gap)
        y_goals_bar = y_container_bottom
        y_text_top = y_goals_bar + bar_height + text_height_offset
        
        opponent_name = row["opponent"].upper()
        pts = int(row["total_points"])
        gf = int(row["goals_scored"])
        ga = int(row["goals_conceded"])
        
        # -------------------------------------------------------------
        # 1. RYSOWANIE KONTENERA (Zamyka w ramce pasek bramek + tekst nazwy)
        # -------------------------------------------------------------
        box_x = [start_x_bar - padding, start_x_bar + max_bar_width + padding, 
                 start_x_bar + max_bar_width + padding, start_x_bar - padding, start_x_bar - padding]
        box_y = [y_container_bottom - padding, y_container_bottom - padding, 
                 y_text_top + padding, y_text_top + padding, y_container_bottom - padding]
        ax.plot(box_x, box_y, color=COLOR_CONTAINER_BORDER, linewidth=1.2, alpha=0.4, zorder=1)

        # -------------------------------------------------------------
        # 2. PAS BRAMKOWY: OD ŚRODKA W BOKI (Zieleń vs Czerwień)
        # -------------------------------------------------------------
        # Tło paska
        ax.fill_between([start_x_bar, start_x_bar + max_bar_width], y_goals_bar, y_goals_bar + bar_height, color=COLOR_BAR_BG, zorder=2)
        
        pixel_per_goal = (max_bar_width / 2) / max_goals_in_series
        width_gf = gf * pixel_per_goal
        width_ga = ga * pixel_per_goal
        
        # Nasze bramki (W prawo — zieleń)
        if width_gf > 0:
            ax.fill_between([center_x_goals, center_x_goals + width_gf], y_goals_bar, y_goals_bar + bar_height, color=COLOR_GOALS_FOR, zorder=3)
        # Stracone bramki (W lewo — czerwień)
        if width_ga > 0:
            ax.fill_between([center_x_goals - width_ga, center_x_goals], y_goals_bar, y_goals_bar + bar_height, color=COLOR_GOALS_AG, zorder=3)
            
        # Czarna linia środkowa (Punkt zero)
        ax.plot([center_x_goals, center_x_goals], [y_goals_bar, y_goals_bar + bar_height], color="#0D0D0D", linewidth=1.5, zorder=4)

        # -------------------------------------------------------------
        # 3. NAZWA DRUŻYNY (Siedzi czysto i bezpiecznie nad paskiem bramek)
        # -------------------------------------------------------------
        ax.text(
            start_x_bar, y_goals_bar + bar_height + 4, 
            opponent_name, color=FONT_COLOR, fontsize=11, fontweight="bold", alpha=0.9, va="bottom"
        )

        # -------------------------------------------------------------
        # 4. KOREKTA POZYCJI LOGO: Centrowanie od dołu paska do samej góry tekstu
        # -------------------------------------------------------------
        y_real_center = (y_container_bottom + y_text_top) / 2
        x_logo = start_x_bar - 65
        add_club_logo(ax, row["opponent"], x_logo, y_real_center, zoom=0.50)
        
        # -------------------------------------------------------------
        # 5. BLOK TEKSTOWY PO PRAWEJ (Idealnie wyśrodkowany w osi wiersza)
        # -------------------------------------------------------------
        x_text_right = start_x_bar + max_bar_width + 25
        summary_text = f"{pts} PKT    |    BRAMKI: {gf}:{ga}"
        ax.text(
            x_text_right, y_real_center, 
            summary_text, color=FONT_COLOR, fontsize=12, fontweight="bold", alpha=0.9, 
            va="center", ha="left"
        )

    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    
    output_path = PLOTS_DIR / "opponent_difficulty_ranking.png"
    plt.savefig(output_path, dpi=300, pad_inches=0, transparent=False)
    plt.close()
    print(f"🚀 Sukces! Oczyszczony, wektorowy wykres rywali zapisano w: {output_path}")

if __name__ == "__main__":
    generate_opponent_ranking()