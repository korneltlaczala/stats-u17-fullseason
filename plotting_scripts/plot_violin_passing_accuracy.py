import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline

# Infrastruktura z Twojego util.py
from util import (
    DATA_DIR, BG_PATH, PLOTS_DIR, add_club_logo,
    COLOR_WIN, COLOR_DRAW, COLOR_LOSS
)

STATS_FULL_PATH = DATA_DIR / "dfs" / "stats_full.csv"
STATS_H1_PATH = DATA_DIR / "dfs" / "stats_half1.csv"
STATS_H2_PATH = DATA_DIR / "dfs" / "stats_half2.csv"

def clean_pct_column(df):
    df = df.dropna(subset=["pass_accuracy"]).copy()
    def to_float(val):
        if isinstance(val, str):
            return float(val.replace('%', '').strip())
        return float(val)
    df["pass_acc_clean"] = df["pass_accuracy"].apply(to_float)
    return df

def generate_passing_distribution_plot():
    print("Generowanie taktycznego profilu podań w 300 DPI...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not all(p.exists() for p in [STATS_FULL_PATH, STATS_H1_PATH, STATS_H2_PATH]):
        print("Błąd: Brak wymaganych plików CSV w data/dfs/")
        return

    # Wczytanie i czyszczenie danych chronologicznie
    df_full = clean_pct_column(pd.read_csv(STATS_FULL_PATH)).sort_values("date_time").reset_index(drop=True)
    df_h1 = clean_pct_column(pd.read_csv(STATS_H1_PATH)).sort_values("date_time").reset_index(drop=True)
    df_h2 = clean_pct_column(pd.read_csv(STATS_H2_PATH)).sort_values("date_time").reset_index(drop=True)

    num_matches = len(df_full)

    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    # Tytuł główny
    ax.text(960, 1010, "CELNOŚĆ PODAŃ NA PRZESTRZENI SEZONU", 
            color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    # =========================================================================
    # LEWA STRONA: WYGŁADZONA LINIA TRENDU Z ETYKIETAMI (CAŁE MECZE)
    # =========================================================================
    ax_timeline = fig.add_axes([0.10, 0.26, 0.48, 0.58]) # [left, bottom, width, height] w proporcjach do figury
    ax_timeline.set_facecolor("none")
    
    x_indices = np.arange(num_matches)
    acc_full = df_full["pass_acc_clean"].values

    # Wygładzanie krzywej za pomocą Spline Interpolation
    x_smooth = np.linspace(x_indices.min(), x_indices.max(), 300)
    spl = make_interp_spline(x_indices, acc_full, k=3)
    y_smooth = spl(x_smooth)

    # Obcinamy wygładzanie do granic logicznych (max 100%)
    y_smooth = np.clip(y_smooth, 0, 100)

    # Rysowanie wygładzonego pola
    ax_timeline.plot(x_smooth, y_smooth, color="#00FF66", linewidth=3, zorder=3)
    ax_timeline.fill_between(x_smooth, 40, y_smooth, color="#00FF66", alpha=0.10, zorder=2)

    # Rzeczywiste punkty meczowe na wykresie i dokładne etykiety %
    ax_timeline.scatter(x_indices, acc_full, color="#FFFFFF", s=40, edgecolors="#00FF66", linewidths=1.5, zorder=4)
    
    for i, val in enumerate(acc_full):
        ax_timeline.text(i, val + 1.5, f"{int(round(val))}%", 
                         color="#FFFFFF", fontsize=8, fontweight="bold", ha="center", va="bottom", zorder=5)

    # Stylizacja lewej osi
    ax_timeline.set_xlim(-0.6, num_matches - 0.4)
    ax_timeline.set_ylim(45, 100)
    ax_timeline.set_ylabel("CELNOŚĆ PODAŃ W MECZU (%)", color="#AAAAAA", fontsize=11, fontweight="bold")
    ax_timeline.tick_params(colors="#FFFFFF", labelsize=9)
    ax_timeline.grid(True, linestyle=":", alpha=0.15, color="#FFFFFF")
    ax_timeline.set_xticks(x_indices)
    ax_timeline.set_xticklabels([])

    # Logotypy na dole pod wykresem trendu
    bbox = ax_timeline.get_position()
    x_start_pixels = bbox.x0 * 1920
    x_end_pixels = bbox.x1 * 1920
    x_logos_coords = np.linspace(x_start_pixels, x_end_pixels, num_matches)
    y_floor_logos = 145

    for idx, match in df_full.iterrows():
        cx_logo = x_logos_coords[idx]
        g, ga = int(match["goals"]), int(match["goals_opponent"])
        dot_color = COLOR_WIN if g > ga else (COLOR_DRAW if g == ga else COLOR_LOSS)
        
        ax.scatter(cx_logo, y_floor_logos + 45, s=50, color=dot_color, edgecolors="#FFFFFF", linewidths=0.5, zorder=4)
        add_club_logo(ax, match["opponent"], cx_logo, y_floor_logos, zoom=0.38)

    # =========================================================================
    # PRAWA STRONA: CHRONOLOGICZNY SPLIT-VIOLIN PLOT (OD GÓRY DO DOŁU)
    # =========================================================================
    ax_violin = fig.add_axes([0.64, 0.15, 0.32, 0.72])
    ax_violin.set_facecolor("none")
    ax_violin.axis("off")

    acc_h1 = df_h1["pass_acc_clean"].values
    acc_h2 = df_h2["pass_acc_clean"].values

    # Sztywne pozycjonowanie pionowe: Mecz 1 na samej górze (y = num_matches), ostatni na dole (y = 1)
    y_time = np.linspace(num_matches, 1, num_matches)

    # Rysowanie centralnej osi symetrii (przerywana linia)
    center_x = 75  # Środek wykresu ustawiamy na umowną bazę celności 75%
    ax_violin.plot([center_x, center_x], [0.5, num_matches + 0.5], color="#444444", linestyle="--", linewidth=1.5)

    # Rysowanie kropek chronologicznie:
    # 1. Połowa (Lewa strona) -> odchylenie w lewo od osi centralnej
    # 2. Połowa (Prawa strona) -> odchylenie w prawo od osi centralnej
    for i in range(num_matches):
        y_pos = y_time[i]
        val_h1 = acc_h1[i]
        val_h2 = acc_h2[i]
        
        # Obliczamy pozycję X jako odległość od osi środkowej (skalowana x0.4 dla estetyki szerokości)
        x_pos_h1 = center_x - (val_h1 - 50) * 0.4
        x_pos_h2 = center_x + (val_h2 - 50) * 0.4
        
        # 1. Połowa - Neonowa zieleń
        ax_violin.scatter(x_pos_h1, y_pos, color="#00FF66", s=45, edgecolors="#FFFFFF", linewidths=0.5, zorder=5)
        # 2. Połowa - Czysta biel
        ax_violin.scatter(x_pos_h2, y_pos, color="#FFFFFF", s=45, edgecolors="#FFFFFF", linewidths=0.5, zorder=5)

    # Podpisy pod sekcjami wykresu skrzypcowego
    mean_h1 = acc_h1.mean()
    mean_h2 = acc_h2.mean()
    
    ax_violin.text(center_x - 14, num_matches * 0.5, f"1. POŁOWA\nŚr: {mean_h1:.1f}%", 
                   color="#00FF66", fontsize=13, fontweight="bold", ha="right", va="center")
    ax_violin.text(center_x + 14, num_matches * 0.5, f"2. POŁOWA\nŚr: {mean_h2:.1f}%", 
                   color="#FFFFFF", fontsize=13, fontweight="bold", ha="left", va="center")

    # Dodatkowe etykiety orientacyjne na osi czasu pionowej
    ax_violin.text(center_x, num_matches + 0.3, "POCZĄTEK SEZONU", color="#AAAAAA", fontsize=8, ha="center", va="bottom")
    ax_violin.text(center_x, 0.7, "KONIEC SEZONU", color="#AAAAAA", fontsize=8, ha="center", va="top")

    ax_violin.set_xlim(center_x - 25, center_x + 25)
    ax_violin.set_ylim(0.2, num_matches + 0.8)

    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    
    output_path = PLOTS_DIR / "violin_passing_accuracy.png"
    plt.savefig(output_path, dpi=300, pad_inches=0)
    plt.close()
    print(f"🚀 Gotowe! Wykres zapisany w: {output_path}")

if __name__ == "__main__":
    generate_passing_distribution_plot()