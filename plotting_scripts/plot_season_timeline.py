import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

from util import (
    MATCHES_CSV_PATH, BG_PATH, PLOTS_DIR, add_club_logo, 
    COLOR_WIN, COLOR_DRAW, COLOR_LOSS
)

def generate_advanced_timeline():
    print("Generowanie ostatecznej osi czasu z wycentrowanymi rundami i poprawionym pozycjonowaniem...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not MATCHES_CSV_PATH.exists():
        print(f"Błąd: Brak pliku {MATCHES_CSV_PATH}!")
        return
    if not BG_PATH.exists():
        print(f"Błąd: Brak pliku tła w {BG_PATH}!")
        return

    # 1. Wczytanie i przygotowanie osi czasu
    df = pd.read_csv(MATCHES_CSV_PATH)
    df["date_time"] = pd.to_datetime(df["date_time"])
    df = df.sort_values("date_time").reset_index(drop=True)

    if len(df) == 0:
        print("Brak meczów do narysowania.")
        return

    # Podział na rundy (Runda Jesienna 2025 vs Runda Wiosenna 2026)
    df_2025 = df[df["date_time"].dt.year == 2025].copy()
    df_2026 = df[df["date_time"].dt.year == 2026].copy()

    # 2. Inicjalizacja figury 16:9 Full HD
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    # Podkład pod wykres
    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    # NOWE POZYCJONOWANIE: Przesunięcie całości w prawo i rozszerzenie strefy
    plot_min_x = 220
    plot_max_x = 1700
    center_x = (plot_min_x + plot_max_x) / 2  # Środek osi czasu do wyśrodkowania napisów

    # NOWE WYSOKOŚCI: Większy odstęp w pionie między osiami
    y_2025 = 810  # Wyżej runda jesienna
    y_2026 = 330  # Niżej runda wiosenna

    # 3. Wyśrodkowane nagłówki rund bezpośrednio NAD osiami
    ax.text(center_x, y_2025 + 110, "RUNDA JESIENNA 2025", color="#FFFFFF", fontsize=18, fontweight="bold", alpha=0.85, ha="center")
    ax.text(center_x, y_2026 + 110, "RUNDA WIOSENNA 2026", color="#FFFFFF", fontsize=18, fontweight="bold", alpha=0.85, ha="center")

    # Funkcja mapująca daty na piksele X
    def get_x_coordinates(df_round):
        if len(df_round) == 0:
            return []
        min_date = df_round["date_time"].min()
        max_date = df_round["date_time"].max()
        
        if min_date == max_date:
            return [center_x]
            
        total_days = (max_date - min_date).days
        coords = []
        for dt in df_round["date_time"]:
            day_diff = (dt - min_date).days
            pct = day_diff / total_days
            x_val = plot_min_x + pct * (plot_max_x - plot_min_x)
            coords.append(x_val)
        return coords

    # Rysujemy elementy dla obu rund
    for df_round, y_pos in [(df_2025, y_2025), (df_2026, y_2026)]:
        if len(df_round) == 0:
            continue

        # Cienka, elegancka linia osi czasu
        ax.plot([plot_min_x - 40, plot_max_x + 40], [y_pos, y_pos], color="#FFFFFF", alpha=0.15, linewidth=2, zorder=1)
        
        x_positions = get_x_coordinates(df_round)

        for idx, (_, match) in enumerate(df_round.iterrows()):
            cx = x_positions[idx]
            gf = int(match["goals_for"])
            ga = int(match["goals_against"])

            # Wybór koloru pod wynik
            if gf > ga:
                dot_color = COLOR_WIN
            elif gf == ga:
                dot_color = COLOR_DRAW
            else:
                dot_color = COLOR_LOSS

            loc_text = "D" if match["home_away"] == "home" else "W"

            # A. Kropka Dom/Wyjazd na osi
            ax.scatter(cx, y_pos, s=650, color=dot_color, edgecolors="#FFFFFF", linewidths=1.5, zorder=4)
            ax.text(cx, y_pos - 2, loc_text, color="#000000", fontsize=11, fontweight="bold", va="center", ha="center", zorder=5)

            # B. Wyszarzona data NAD kropką wyników
            date_str = match["date_time"].strftime("%d.%m")
            ax.text(cx, y_pos + 45, date_str, color="#FFFFFF", fontsize=11, alpha=0.4, va="center", ha="center", zorder=4)

            # POPRAWKA POZYCJONOWANIA: Przesunięcie herbu niżej, aby odsłonić wynik
            y_logo = y_pos - 130  
            y_text_offset = 65
            
            # C. Wydłużona pionowa linia (Lollipop) dająca briding space
            ax.plot([cx, cx], [y_pos - 15, y_logo + 25], color="#FFFFFF", alpha=0.12, linewidth=1.5, linestyle="--", zorder=2)

            # D. Wynik meczu bezpośrednio NAD logiem przeciwnika (teraz w pełni odsłonięty)
            score_str = f"{gf}:{ga}"
            ax.text(cx, y_logo - y_text_offset, score_str, color="#FFFFFF", fontsize=14, fontweight="bold", va="center", ha="center", zorder=4)

            # E. Zmniejszone logo przeciwnika (zoom=0.85) dla zachowania oddechu
            add_club_logo(ax, match["opponent"], cx, y_logo, zoom=0.70)

    # Końcowe ustawianie granic sceny
    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)

    output_path = PLOTS_DIR / "season_timeline.png"
    plt.savefig(output_path, dpi=300, pad_inches=0, transparent=False)
    plt.close()
    print(f"Sukces! Nowa, dopieszczona oś czasu zapisana w: {output_path}")

if __name__ == "__main__":
    generate_advanced_timeline()