import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Infrastruktura zutil.py (katalogi, tło)
from util import DATA_DIR, BG_PATH, PLOTS_DIR

# Ścieżki do nowych plików
BRAMKI_PATH = DATA_DIR / "dfs" / "bramki_u17_2009_lista.csv"
ASYSTY_PATH = DATA_DIR / "dfs" / "asysty_u17_2009_lista.csv"

def generate_player_kanadyjska_plot():
    print("Agregowanie danych i generowanie klasyfikacji kanadyjskiej CLJ U-17 (300 DPI)...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not BRAMKI_PATH.exists() or not ASYSTY_PATH.exists():
        print(f"Błąd: Brak plików z danymi ({BRAMKI_PATH} lub {ASYSTY_PATH})!")
        return

    # 1. Wczytanie i łączenie danych z plików CSV [cite: 3, 4]
    df_bramki = pd.read_csv(BRAMKI_PATH)
    df_asysty = pd.read_csv(ASYSTY_PATH)

    # Łączenie obustronne (outer join), aby złapać zawodników mających tylko bramki lub tylko asysty
    df = pd.merge(df_bramki, df_asysty, on='nazwisko', how='outer')
    
    # Wypełnianie braków zerami i konwersja na int
    df['liczba_bramek'] = df['liczba_bramek'].fillna(0).astype(int)
    df['liczba_asyst'] = df['liczba_asyst'].fillna(0).astype(int)
    
    # Obliczanie sumy do klasyfikacji kanadyjskiej
    df['suma'] = df['liczba_bramek'] + df['liczba_asyst']
    
    # Filtrowanie i sortowanie (najlepsi na dole DataFrame, żeby na wykresie byli na górze)
    df = df[df["suma"] > 0]
    df = df.sort_values(by=["suma", "liczba_bramek"], ascending=True)
    
    players = df["nazwisko"].values
    goals = df["liczba_bramek"].values
    assists = df["liczba_asyst"].values
    totals = df["suma"].values
    num_players = len(players)

    # 2. Inicjalizacja płótna 16:9 (300 DPI)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    try:
        bg_img = mpimg.imread(str(BG_PATH))
        ax.imshow(bg_img, extent=[0, 1920, 0, 1080])
    except Exception as e:
        print(f"Ostrzeżenie: Nie udało się wczytać tła ({e}). Rysuję bez obrazka w tle.")
        ax.set_xlim(0, 1920)
        ax.set_ylim(0, 1080)

    # Tytuł slajdu i subtelna legenda
    ax.text(960, 1010, "KLASYFIKACJA KANADYJSKA: CENTRALNA LIGA JUNIORÓW U-17", 
            color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")
    
    ax.text(960, 960, "BIAŁY = BRAMKI   |   SZARY = ASYSTY", 
            color="#AAAAAA", fontsize=11, fontweight="bold", ha="center")

    # 3. GEOMETRIA 
    ax_bars = fig.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars.set_facecolor("none")
    
    # Rysowanie skumulowanych pasków (stacked bars)
    ax_bars.barh(np.arange(num_players), goals, color="#FFFFFF", height=0.55, edgecolor="none", zorder=3)
    ax_bars.barh(np.arange(num_players), assists, left=goals, color="#AAAAAA", height=0.55, edgecolor="none", zorder=3)

    # Liczba punktów (suma) na końcu każdego paska
    for i in range(num_players):
        ax_bars.text(totals[i] + 0.2, i, f"{totals[i]}", 
                     color="#00FF66", fontsize=10, fontweight="bold", ha="left", va="center", zorder=4)

    # Ustawienia osi pionowej (Nazwiska zawodników)
    ax_bars.set_yticks(np.arange(num_players))
    ax_bars.set_yticklabels(players, color="#FFFFFF", fontsize=10, fontweight="bold", ha="right")

    # Zakres i osie (maksymalnie, żeby paski ładnie wypełniły ekran)
    max_pts = int(max(totals)) if num_players > 0 else 10
    ax_bars.set_xlim(0, max_pts + 1)
    
    # Generujemy skoki na osi co 1 lub 2 punkty
    ticks_step = 1 if max_pts <= 12 else 2
    xticks_vals = np.arange(0, max_pts + 1, ticks_step)
    ax_bars.set_xticks(xticks_vals)

    # Delikatna siatka pionowa
    ax_bars.grid(axis="x", linestyle="--", alpha=0.15, color="#FFFFFF", zorder=1)

    # Czyszczenie ramek systemowych matplotlib
    for spine in ["top", "right", "left", "bottom"]:
        ax_bars.spines[spine].set_visible(False)
        
    ax_bars.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars.tick_params(axis="x", colors="#AAAAAA", pad=10)

    # Zapis
    output_path = PLOTS_DIR / "player_kanadyjska_clj_ranking.png"
    plt.savefig(output_path, dpi=300, pad_inches=0, transparent=False)
    plt.close()
    print(f"🚀 Klasyfikacja kanadyjska wygenerowana! Plik: {output_path}")

if __name__ == "__main__":
    generate_player_kanadyjska_plot()