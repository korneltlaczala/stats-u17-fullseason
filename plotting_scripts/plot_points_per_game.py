import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Importujemy sprawdzoną infrastrukturę z Twojego util.py
from util import (
    MATCHES_CSV_PATH, BG_PATH, PLOTS_DIR, 
    COLOR_WIN, COLOR_LOSS
)

def calculate_points_stats():
    """Wczytuje mecze i liczy statystyki punktów na mecz (PPG) oraz sumy punktów z rozbiciem na rundy."""
    df = pd.read_csv(MATCHES_CSV_PATH)
    df["date_time"] = pd.to_datetime(df["date_time"])
    
    def get_points(row):
        gf = int(row["goals_for"])
        ga = int(row["goals_against"])
        if gf > ga: return 3
        elif gf == ga: return 1
        return 0
        
    df["points"] = df.apply(get_points, axis=1)
    df["year"] = df["date_time"].dt.year
    
    stats = {}
    
    # 1. Cały sezon
    df_home = df[df["home_away"] == "home"]
    df_away = df[df["home_away"] == "away"]
    stats["full_home_ppg"] = df_home["points"].mean() if len(df_home) > 0 else 0
    stats["full_away_ppg"] = df_away["points"].mean() if len(df_away) > 0 else 0
    stats["full_home_total"] = df_home["points"].sum()
    stats["full_away_total"] = df_away["points"].sum()
    stats["full_count"] = len(df)
    
    # 2. Runda Jesienna (2025)
    df_2025 = df[df["year"] == 2025]
    df_h_2025 = df_2025[df_2025["home_away"] == "home"]
    df_a_2025 = df_2025[df_2025["home_away"] == "away"]
    stats["j_home_ppg"] = df_h_2025["points"].mean() if len(df_h_2025) > 0 else 0
    stats["j_away_ppg"] = df_a_2025["points"].mean() if len(df_a_2025) > 0 else 0
    stats["j_count"] = len(df_2025)
    
    # 3. Runda Wiosenna (2026)
    df_2026 = df[df["year"] == 2026]
    df_h_2026 = df_2026[df_2026["home_away"] == "home"]
    df_a_2026 = df_2026[df_2026["home_away"] == "away"]
    stats["w_home_ppg"] = df_h_2026["points"].mean() if len(df_h_2026) > 0 else 0
    stats["w_away_ppg"] = df_a_2026["points"].mean() if len(df_a_2026) > 0 else 0
    stats["w_count"] = len(df_2026)
    
    return stats

def draw_donut(ax, home_val, away_val, radius=1.0, title="", match_count=None, detailed_stats=None):
    """Rysuje gładki wykres pierścieniowy z informacją o meczach i średnich po bokach."""
    values = [home_val, away_val]
    
    # NOWA PALETA: Neonowa zieleń (Dom) i czysta jaskrawa Biel (Wyjazd) - brak negatywnych skojarzeń
    colors = ["#00FF66", "#FFFFFF"] 
    explode = (0.06, 0) 
    
    wedges, texts = ax.pie(
        values, 
        colors=colors, 
        radius=radius,
        explode=explode,
        startangle=90, 
        counterclock=False,
        wedgeprops=dict(width=0.26, edgecolor="#0D0D0D", linewidth=4),
    )
    
    # Wielki tekst średniego PPG ogólnego w środku koła
    total_ppg = (home_val + away_val) / 2
    ax.text(0, -0.05, f"{total_ppg:.2f}", color="#FFFFFF", fontsize=int(25 * radius), fontweight="bold", ha="center", va="center")
    ax.text(0, 0.18, "ŚREDNIA", color="#FFFFFF", fontsize=int(9 * radius), alpha=0.5, ha="center", va="center")
    
    # Podpis pod kółkiem rozbudowany o liczbę rozegranych spotkań
    full_title = title
    if match_count is not None:
        full_title += f" ({match_count} MECZÓW)"
    ax.text(0, -(radius + 0.28), full_title, color="#FFFFFF", fontsize=int(13 * radius), fontweight="bold", ha="center", va="center")

    # # NOWOŚĆ: Precyzyjne podpisy szczegółowe po prawej i lewej stronie małych kółek (Dom/Wyjazd)
    # if detailed_stats:
    #     # Tekst po lewej stronie koła (Statystyki DOM - zieleń)
    #     ax.text(-radius - 0.25, 0, f"DOM\n{detailed_stats['home']:.2f}", color="#00FF66", 
    #             fontsize=int(11 * radius), fontweight="bold", ha="right", va="center", linespacing=1.3)
    #     # Tekst po prawej stronie koła (Statystyki WYJAZD - biel)
    #     ax.text(radius + 0.25, 0, f"WYJAZD\n{detailed_stats['away']:.2f}", color="#FFFFFF", 
    #             fontsize=int(11 * radius), fontweight="bold", ha="left", va="center", linespacing=1.3)
    # NOWOŚĆ: Precyzyjne podpisy szczegółowe po prawej i lewej stronie małych kółek (Dom/Wyjazd)
    if detailed_stats:
        # Tekst po PRAWEJ stronie koła (Statystyki DOM - zieleń, dodatni X, wyrównanie do lewej)
        ax.text(radius + 0.25, 0, f"DOM\n{detailed_stats['home']:.2f}", color="#00FF66", 
                fontsize=int(11 * radius), fontweight="bold", ha="left", va="center", linespacing=1.3)
        # Tekst po LEWEJ stronie koła (Statystyki WYJAZD - biel, ujemny X, wyrównanie do prawej)
        ax.text(-radius - 0.25, 0, f"WYJAZD\n{detailed_stats['away']:.2f}", color="#FFFFFF", 
                fontsize=int(11 * radius), fontweight="bold", ha="right", va="center", linespacing=1.3)

def generate_points_plots():
    print("Przetwarzanie statystyk punktowych i generowanie wykresu PPG...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    # colors = ["#00FF66", "#FFFFFF"] 
    colors = ["#00FF66", "#FF3333"] 
    
    
    if not MATCHES_CSV_PATH.exists():
        print(f"Błąd: Brak pliku {MATCHES_CSV_PATH}!")
        return
        
    stats = calculate_points_stats()
    
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    
    # Podkład z drapieżnym tłem
    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])
    
    # -------------------------------------------------------------
    # SEKCJA KÓŁEK (Lewa strona ekranu)
    # -------------------------------------------------------------
    
    # 1. Duże kółko - Cały Sezon (Środek-Góra)
    ax_full = fig.add_axes([0.18, 0.44, 0.32, 0.44])
    ax_full.axis("off")
    draw_donut(ax_full, stats["full_home_ppg"], stats["full_away_ppg"], radius=1.0, title="CAŁY SEZON")
    
    # 2. Małe kółko - Runda Jesienna (Dół-Lewo) + Średnie po bokach + liczba meczów
    ax_jesien = fig.add_axes([0.09, 0.08, 0.22, 0.25])
    ax_jesien.axis("off")
    j_details = {"home": stats["j_home_ppg"], "away": stats["j_away_ppg"]}
    draw_donut(ax_jesien, stats["j_home_ppg"], stats["j_away_ppg"], radius=0.75, 
               title="RUNDA JESIENNA", match_count=stats["j_count"], detailed_stats=j_details)
    
    # 3. Małe kółko - Runda Wiosenna (Dół-Prawo) + Średnie po bokach + liczba meczów
    ax_wiosna = fig.add_axes([0.37, 0.08, 0.22, 0.25])
    ax_wiosna.axis("off")
    w_details = {"home": stats["w_home_ppg"], "away": stats["w_away_ppg"]}
    draw_donut(ax_wiosna, stats["w_home_ppg"], stats["w_away_ppg"], radius=0.75, 
               title="RUNDA WIOSENNA", match_count=stats["w_count"], detailed_stats=w_details)
    
    # -------------------------------------------------------------
    # SEKCJA SŁUPKÓW (Prawa strona ekranu)
    # -------------------------------------------------------------
    right_section_x = 1180  
    
    ax.text(right_section_x, 880, "PUNKTY W SEZONIE", color="#FFFFFF", fontsize=22, fontweight="bold", ha="left")
    
    max_bar_width = 460
    max_possible_points = 45 # 15 meczów * 3 pkt
    home_pct = stats["full_home_total"] / max_possible_points
    away_pct = stats["full_away_total"] / max_possible_points
    
    # Słupek 1: MECZE U SIEBIE
    y_home_bar = 620
    # POPRAWKA: Rozjaśnione tło korytarza paska (z alpha=0.6 na wyrazisty grafit alpha=0.9), by dokładnie widzieć maksa (45 pkt)
    ax.fill_between([right_section_x, right_section_x + max_bar_width], y_home_bar, y_home_bar + 42, color="#252525", alpha=0.9, zorder=2)
    ax.fill_between([right_section_x, right_section_x + (max_bar_width * home_pct)], y_home_bar, y_home_bar + 42, color="#00FF66", zorder=3)
    
    ax.text(right_section_x, y_home_bar + 60, "MECZE U SIEBIE", color="#FFFFFF", fontsize=14, fontweight="bold", alpha=0.7)
    ax.text(right_section_x + max_bar_width, y_home_bar + 60, f"PPG: {stats['full_home_ppg']:.2f}", color="#00FF66", fontsize=15, fontweight="bold", ha="right")
    ax.text(right_section_x + 15, y_home_bar + 13, f"{stats['full_home_total']} / {max_possible_points} pkt", color="#000000", fontsize=15, fontweight="bold", zorder=4)
    
    # Słupek 2: MECZE NA WYJEŹDZIE
    y_away_bar = 400
    # POPRAWKA: Rozjaśnione tło korytarza paska
    ax.fill_between([right_section_x, right_section_x + max_bar_width], y_away_bar, y_away_bar + 42, color="#252525", alpha=0.9, zorder=2)
    ax.fill_between([right_section_x, right_section_x + (max_bar_width * away_pct)], y_away_bar, y_away_bar + 42, color="#FFFFFF", zorder=3)
    
    ax.text(right_section_x, y_away_bar + 60, "MECZE NA WYJEŹDZIE", color="#FFFFFF", fontsize=14, fontweight="bold", alpha=0.7)
    ax.text(right_section_x + max_bar_width, y_away_bar + 60, f"PPG: {stats['full_away_ppg']:.2f}", color="#FFFFFF", fontsize=15, fontweight="bold", ha="right")
    ax.text(right_section_x + 15, y_away_bar + 13, f"{stats['full_away_total']} / {max_possible_points} pkt", color="#000000", fontsize=15, fontweight="bold", zorder=4)
    
    # Nowoczesna, czysta legenda na dole
    leg_y = 230
    ax.scatter(right_section_x + 15, leg_y, s=120, color="#00FF66", edgecolors="#FFFFFF", linewidths=1)
    ax.text(right_section_x + 35, leg_y, "PUNKTY DOM", color="#FFFFFF", fontsize=12, alpha=0.6, va="center")
    
    ax.scatter(right_section_x + 220, leg_y, s=120, color="#FFFFFF", edgecolors="#FFFFFF", linewidths=1)
    ax.text(right_section_x + 240, leg_y, "PUNKTY WYJAZD", color="#FFFFFF", fontsize=12, alpha=0.6, va="center")

    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    
    output_path = PLOTS_DIR / "points_per_game.png"
    plt.savefig(output_path, dpi=120, pad_inches=0, transparent=False)
    plt.close()
    print(f"🚀 Sukces! Zaktualizowany wykres PPG zapisano w: {output_path}")

if __name__ == "__main__":
    generate_points_plots()