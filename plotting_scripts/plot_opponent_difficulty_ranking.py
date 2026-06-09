import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Importujemy sprawdzoną infrastrukturę z Twojego util.py
from util import (
    MATCHES_CSV_PATH, BG_PATH, PLOTS_DIR, 
    add_club_logo, COLOR_WIN
)

# CENTRALNA CONFIGURACJA PALETY (Spójna z resztą prezentacji)
COLOR_BAR_FILL = "#00FF66"   # Neonowa zieleń Polonii dla zdobytych punktów
COLOR_BAR_BG = "#252525"     # Rozjaśniony grafitowy korytarz tła słupka (sufit 6 pkt)
FONT_COLOR = "#FFFFFF"

def calculate_opponent_stats():
    """Wczytuje mecze, agreguje punkty oraz bramki w dwumeczach z każdym rywalem."""
    df = pd.read_csv(MATCHES_CSV_PATH)
    
    # Liczenie punktów dla pojedynczych meczów
    def get_points(row):
        gf = int(row["goals_for"])
        ga = int(row["goals_against"])
        if gf > ga: return 3
        elif gf == ga: return 1
        return 0
        
    df["points"] = df.apply(get_points, axis=1)
    
    # Agregacja danych po przeciwniku
    grouped = df.groupby("opponent").agg(
        total_points=("points", "sum"),
        goals_scored=("goals_for", "sum"),
        goals_conceded=("goals_against", "sum"),
        matches_played=("opponent", "count")
    ).reset_index()
    
    # Bilans bramkowy jako pomocnicza kolumna do sortowania (różnica bramek)
    grouped["goal_diff"] = grouped["goals_scored"] - grouped["goals_conceded"]
    
    # Sortowanie: najpierw punkty (malejąco), potem bilans bramek (malejąco)
    grouped = grouped.sort_values(
        by=["total_points", "goal_diff", "goals_scored"], 
        ascending=[False, False, False]
    ).reset_index(drop=True)
    
    return grouped

def generate_opponent_ranking():
    print("Przetwarzanie danych i generowanie rankingu przeciwników...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not MATCHES_CSV_PATH.exists():
        print(f"Błąd: Brak pliku {MATCHES_CSV_PATH}!")
        return
        
    opponents_df = calculate_opponent_stats()
    num_opponents = len(opponents_df)
    
    if num_opponents == 0:
        print("Brak danych o przeciwnikach.")
        return
        
    # Inicjalizacja płótna 16:9 Full HD
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    
    # Podkład pod wykres (Twoje kozackie tło)
    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])
    
    # Nagłówek główny grafiki
    ax.text(320, 960, "RANKING PRZECIWNIKÓW — ZDOBYTE PUNKTY I BILANS", 
            color=FONT_COLOR, fontsize=22, fontweight="bold", ha="left")
    
    # Parametry pozycjonowania słupków na ekranie
    start_y = 850          # Wysokość pierwszego (najwyższego) słupka
    bar_gap = 52           # Odstęp w pionie między słupkami
    start_x_bar = 320      # Gdzie fizycznie zaczyna się słupek w poziomie
    max_bar_width = 1000   # Maksymalna długość słupka odpowiadająca 6 punktom
    bar_height = 26        # Grubość słupka
    
    # Iteracja po zagregowanych przeciwnikach i rysowanie warstw
    for idx, row in opponents_df.iterrows():
        current_y = start_y - (idx * bar_gap)
        
        opponent_name = row["opponent"].upper()
        pts = int(row["total_points"])
        gf = int(row["goals_scored"])
        ga = int(row["goals_conceded"])
        
        # Matematyczne wyliczenie szerokości paska (maksymalna pula to 6 pkt w dwumeczu)
        # Zabezpieczenie: jeśli grali tylko 1 mecz (np. runda się nie skończyła), sufit to 3 pkt
        max_possible_pts = int(row["matches_played"]) * 3
        pct = pts / max_possible_pts if max_possible_pts > 0 else 0
        current_bar_width = max_bar_width * pct
        
        # 1. Rysowanie tła korytarza paska (pełny wymiar oznaczający 100% punktów)
        ax.fill_between(
            [start_x_bar, start_x_bar + max_bar_width], 
            current_y, current_y + bar_height, 
            color=COLOR_BAR_BG, alpha=0.85, zorder=2
        )
        
        # 2. Rysowanie paska postępu (zdobyte punkty) - jeśli zdobyto 0 pkt, nie rysujemy pustego paska
        if current_bar_width > 0:
            ax.fill_between(
                [start_x_bar, start_x_bar + current_bar_width], 
                current_y, current_y + bar_height, 
                color=COLOR_BAR_FILL, zorder=3
            )
            
        # 3. Dodanie idealnie gładkiego, wektorowego herbu po lewej stronie paska
        # Pozycja X koła herbu przesunięta o 60 pikseli w lewo od paska
        x_logo = start_x_bar - 60
        y_logo_center = current_y + (bar_height / 2)
        add_club_logo(ax, row["opponent"], x_logo, y_logo_center, zoom=0.68)
        
        # 4. Nazwa przeciwnika NAD słupkiem (lekko uniesiona w pionie, idealnie czytelna)
        ax.text(
            start_x_bar, current_y + bar_height + 6, 
            opponent_name, color=FONT_COLOR, fontsize=12, fontweight="bold", alpha=0.8
        )
        
        # 5. Liczba punktów wpisana wewnątrz zielonego paska (jeśli jest miejsce) lub tuż obok niego
        # Tekst sformatowany jako "X pkt"
        pts_str = f"{pts} PKT"
        if pct > 0.15:
            # Wewnątrz paska (czarny tekst na zielonym tle)
            ax.text(
                start_x_bar + 15, current_y + (bar_height / 2), 
                pts_str, color="#000000", fontsize=11, fontweight="bold", va="center", zorder=4
            )
        else:
            # Na zewnątrz paska (biały tekst tuż za paskiem)
            ax.text(
                start_x_bar + current_bar_width + 12, current_y + (bar_height / 2), 
                pts_str, color=FONT_COLOR, fontsize=11, fontweight="bold", va="center", zorder=4
            )
            
        # 6. Bilans bramkowy na samym końcu korytarza słupka po prawej stronie
        # Wyświetlane w formacie: "BRAMKI: 5:2"
        score_balance_str = f"BRAMKI: {gf}:{ga}"
        ax.text(
            start_x_bar + max_bar_width + 25, current_y + (bar_height / 2), 
            score_balance_str, color=FONT_COLOR, fontsize=12, fontweight="bold", alpha=0.9, 
            va="center", ha="left"
        )

    # Sztywne zamykanie sceny graficznej 16:9
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    
    output_path = PLOTS_DIR / "opponent_difficulty_ranking.png"
    plt.savefig(output_path, dpi=120, pad_inches=0, transparent=False)
    plt.close()
    print(f"🚀 Sukces! Wykres rankingu przeciwników zapisano w: {output_path}")

if __name__ == "__main__":
    generate_opponent_ranking()