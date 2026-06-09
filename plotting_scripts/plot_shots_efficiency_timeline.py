import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Importujemy sprawdzoną, wygładzoną infrastrukturę z Twojego util.py
from util import (
    DATA_DIR, BG_PATH, PLOTS_DIR, add_club_logo, 
    COLOR_WIN, COLOR_DRAW, COLOR_LOSS
)

# Ścieżka do statystyk drużynowych z Eyeballa
STATS_FULL_PATH = DATA_DIR / "dfs" / "stats_full.csv"

# CENTRALNA KONFIGURACJA PALETY (Drapieżny, nowoczesny kontrast na ciemnym tle)
COLOR_SHOTS_TOTAL = "#3A3A3A"   # Stonowany, głęboki grafit dla wszystkich strzałów
COLOR_SHOTS_ON_TARGET = "#FFFFFF" # Czysta, jasna biel dla strzałów celnych
COLOR_GOALS = "#00FF66"           # Neonowa zieleń Polonii dla wisienki na torcie (bramki!)

def generate_shots_efficiency_plot():
    print("Rozpoczynam generowanie osi efektywności strzeleckiej (300 DPI)...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not STATS_FULL_PATH.exists():
        print(f"Błąd: Brak pliku {STATS_FULL_PATH}! Uruchom najpierw prep_team_stats_dfs.py")
        return
    if not BG_PATH.exists():
        print(f"Błąd: Brak pliku tła w {BG_PATH}!")
        return

    # 1. Wczytanie danych i odrzucenie wierszy bez Eyeballa (NaN), zachowując chronologię
    df = pd.read_csv(STATS_FULL_PATH)
    df["date_time"] = pd.to_datetime(df["date_time"])
    df = df.sort_values("date_time").dropna(subset=["shots_in_total"]).reset_index(drop=True)

    num_matches = len(df)
    if num_matches == 0:
        print("Brak meczów z danymi Eyeballa do wyświetlenia.")
        return

    # 2. Inicjalizacja płótna 16:9 Full HD
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300) # POTĘŻNE 300 DPI DO JAKOŚCI ULTRA HD
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    # Podkład pod wykres
    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    # Nagłówek główny slajdu
    ax.text(200, 990, "PRODUKTYWNOŚĆ OFENSYWNA — STRZAŁY VS STRZAŁY CELNE VS BRAMKI", 
            color="#FFFFFF", fontsize=22, fontweight="bold", ha="left")

    # 3. GEOMETRIA I POZYCJONOWANIE GRUP SŁUPKÓW
    start_x = 220
    end_x = 1720
    x_coords = np.linspace(start_x, end_x, num_matches) # Środki grup dla każdego meczu

    # Parametry pojedynczych słupków w grupie
    bar_width = 14       # Szerokość jednego słupka
    group_gap = 4        # Odstęp między słupkami wewnątrz jednej grupy
    
    # Wysokości bazowe elementów
    y_floor = 280        # Podłoga, od której słupki rosną w górę
    y_logo = 150         # Wysokość, na której środkujemy herby rywali
    
    # Skalowanie wysokości słupków: szukamy maks strzałów w sezonie, żeby idealnie dobrać proporcje pionowe
    max_shots_in_season = df["shots_in_total"].max()
    if pd.isna(max_shots_in_season) or max_shots_in_season == 0:
        max_shots_in_season = 25 # Bezpieczny sufit domyślny
        
    max_plot_bar_height = 460 # Maksymalna wysokość słupka na ekranie w pikselach
    scale_y = max_plot_bar_height / max_shots_in_season

    # 4. ITERACJA PO MECZACH I RYSOWANIE WARSTW
    for idx, match in df.iterrows():
        cx = x_coords[idx]
        
        # Pobranie czystych danych liczbowych
        shots_total = int(match["shots_in_total"])
        shots_on_target = int(match["shots_on_target"])
        goals = int(match["goals_for"])
        goals_against = int(match["goals_against"])

        # Przeliczenie realnych wysokości słupków na ekranie
        h_total = shots_total * scale_y
        h_on_target = shots_on_target * scale_y
        h_goals = goals * scale_y

        # Obliczanie pozycji X dla trzech słupków stojących obok siebie w grupie
        x_total = cx - bar_width - group_gap
        x_on_target = cx
        x_goals = cx + bar_width + group_gap

        # Rysowanie Słupka 1: Strzały ogółem (Grafitowy)
        ax.fill_between([x_total - bar_width/2, x_total + bar_width/2], y_floor, y_floor + h_total, color=COLOR_SHOTS_TOTAL, zorder=2)
        # Rysowanie Słupka 2: Strzały celne (Biały)
        ax.fill_between([x_on_target - bar_width/2, x_on_target + bar_width/2], y_floor, y_floor + h_target, color=COLOR_SHOTS_ON_TARGET, zorder=2)
        # Rysowanie Słupka 3: Bramki strzelone (Neonowa zieleń)
        if h_goals > 0:
            ax.fill_between([x_goals - bar_width/2, x_goals + bar_width/2], y_floor, y_floor + h_goals, color=COLOR_GOALS, zorder=2)

        # Wypisanie małych, czytelnych cyfr nad każdym słupkiem, żeby zawodnicy widzieli dokładny detal
        ax.text(x_total, y_floor + h_total + 8, str(shots_total), color="#FFFFFF", fontsize=9, alpha=0.5, ha="center", va="bottom")
        ax.text(x_on_target, y_floor + h_target + 8, str(shots_on_target), color="#FFFFFF", fontsize=9, alpha=0.8, ha="center", va="bottom")
        ax.text(x_goals, y_floor + h_goals + 8, str(goals), color=COLOR_GOALS, fontsize=10, fontweight="bold", ha="center", va="bottom")

        # 5. KÓŁECZKO WYNIKU NA SAMEJ GÓRZE GRUPY (Nad najwyższym słupkiem + 50px marginesu)
        y_dot = y_floor + h_total + 50
        
        if goals > goals_against:
            dot_color = COLOR_WIN
        elif goals == goals_against:
            dot_color = COLOR_DRAW
        else:
            dot_color = COLOR_LOSS
            
        loc_text = "D" if match["home_away"] == "home" else "W"
        
        ax.scatter(cx, y_dot, s=400, color=dot_color, edgecolors="#FFFFFF", linewidths=1.2, zorder=3)
        ax.text(cx, y_dot - 1.2, loc_text, color="#000000", fontsize=10, fontweight="bold", va="center", ha="center", zorder=4)

        # 6. PIONOWA LINIA LOLLIPOP (Łączy podłogę z herbem rywala na samym dole)
        ax.plot([cx, cx], [y_floor - 10, y_logo + 30], color="#FFFFFF", alpha=0.1, linewidth=1.2, linestyle="--", zorder=1)

        # 7. IDEALNIE WYGŁADZONE LOGO RYWALA POD OSIĄ (zoom przekazany prosto do utila!)
        add_club_logo(ax, match["opponent"], cx, y_logo, zoom=0.68)

    # Sztywne zamykanie sceny 16:9
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)

    output_path = PLOTS_DIR / "shots_efficiency_timeline.png"
    plt.savefig(output_path, dpi=300, pad_inches=0, transparent=False) # PEŁNE 300 DPI DO PLIKU WYJŚCIOWEGO
    plt.close()
    print(f"🚀 Sukces! Wykres efektywności strzałów w 300 DPI zapisano w: {output_path}")

if __name__ == "__main__":
    generate_shots_efficiency_plot()