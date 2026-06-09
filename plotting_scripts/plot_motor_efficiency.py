import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Infrastruktura z util.py (katalogi, tło, kolory, herby)
from util import (
    DATA_DIR, BG_PATH, PLOTS_DIR, add_club_logo,
    COLOR_WIN, COLOR_DRAW, COLOR_LOSS
)

MOTOR_STATS_PATH = DATA_DIR / "dfs" / "motor_stats_full.csv"
STATS_FULL_PATH = DATA_DIR / "dfs" / "stats_full.csv"

def generate_motor_plots():
    print("Rozpoczynam generowanie 3 zweryfikowanych wykresów motorycznych (300 DPI)...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not MOTOR_STATS_PATH.exists() or not STATS_FULL_PATH.exists():
        print("Błąd: Brak plików motor_stats_full.csv lub stats_full.csv!")
        return

    # 1. WCZYTANIE I SYNCHRONIZACJA DANYCH CHRONOLOGICZNIE
    df_games = pd.read_csv(STATS_FULL_PATH)
    df_games["date_time"] = pd.to_datetime(df_games["date_time"])
    df_games = df_games.sort_values("date_time").reset_index(drop=True)

    df_motor = pd.read_csv(MOTOR_STATS_PATH)
    df_motor = df_motor[df_motor["Split Name"] == "all"].copy()

    # POPRAWKA HSR: Sumujemy Zone 3 i Zone 4 dla pełnego odwzorowania High-Speed Running
    df_motor["Zone3_m"] = df_motor["Distance in Speed Zone 3  (km)"].astype(float) * 1000
    df_motor["Zone4_m"] = df_motor["Distance in Speed Zone 4  (km)"].astype(float) * 1000
    df_motor["HSR_m_full"] = df_motor["Zone3_m"]
    
    df_motor["Sprint_Dist_m"] = df_motor["Sprint Distance (m)"].astype(float)

    # Agregacja na poziomie meczu per zespół
    motor_grouped = df_motor.groupby("pzpn_id").agg({
        "Distance (km)": "sum",
        "HSR_m_full": "sum",
        "Sprint_Dist_m": "sum"
    }).reset_index()

    # Łączenie z bazą wyników meczowych
    df_final = pd.merge(df_games[["pzpn_id", "opponent", "true_goals", "true_goals_opponent"]], 
                        motor_grouped, on="pzpn_id", how="inner")
    df_final = df_final.dropna(subset=["true_goals", "true_goals_opponent"]).reset_index(drop=True)

    num_matches = len(df_final)
    if num_matches == 0:
        print("Błąd: Brak meczów po połączeniu baz!")
        return

    # GEOMETRIA WSPÓLNA (Sztywne ramy, herby zoom=0.50)
    start_x, end_x = 200, 1720
    x_coords = np.linspace(start_x, end_x, num_matches)
    bar_width = 24
    y_logo = 100  
    y_floor = 220

    # =========================================================================
    # WYKRES 1: CAŁKOWITY DYSTANS ZESPOŁU (POPRAWIONA SKALA OD 90 KM + WYRAZISTE LINIE)
    # =========================================================================
    fig1, ax1 = plt.subplots(figsize=(16, 9), dpi=300)
    fig1.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax1.axis("off")
    ax1.imshow(mpimg.imread(str(BG_PATH)), extent=[0, 1920, 0, 1080])

    ax1.text(960, 1010, "CAŁKOWITY DYSTANS ZESPOŁU (KM)", 
             color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    max_dist = df_final["Distance (km)"].max()
    scale_y1 = 530 / max_dist

    # POPRAWKA: Skala uwzględnia 90 km, a linie są o wiele bardziej wyraziste (alpha=0.15)
    for d_val in [90, 100, 110, 120, 130]:
        y_line = y_floor + d_val * scale_y1
        ax1.plot([start_x - 40, end_x + 40], [y_line, y_line], color="#FFFFFF", alpha=0.15, linestyle=":", zorder=1)
        ax1.text(start_x - 50, y_line, f"{d_val} km", color="#FFFFFF", alpha=0.6, fontsize=9, ha="right", va="center", fontweight="bold")

    for idx, match in df_final.iterrows():
        cx = x_coords[idx]
        dist = match["Distance (km)"]
        g, ga = int(match["true_goals"]), int(match["true_goals_opponent"])

        ax1.fill_between([cx - bar_width/2, cx + bar_width/2], y_floor, y_floor + dist * scale_y1, color="#FFFFFF", zorder=2)
        ax1.text(cx, y_floor + dist * scale_y1 + 10, f"{dist:.1f}", color="#FFFFFF", fontsize=8, fontweight="bold", ha="center")

        dot_color = COLOR_WIN if g > ga else (COLOR_DRAW if g == ga else COLOR_LOSS)
        ax1.scatter(cx, y_floor - 45, s=200, color=dot_color, edgecolors="#FFFFFF", linewidths=1, zorder=3)
        ax1.text(cx, y_floor - 45, "W" if g > ga else ("R" if g == ga else "P"), color="#000000", fontsize=7, fontweight="bold", ha="center", va="center", zorder=4)
        add_club_logo(ax1, match["opponent"], cx, y_logo, zoom=0.50)

    ax1.set_xlim(0, 1920)
    ax1.set_ylim(0, 1080)
    fig1.savefig(PLOTS_DIR / "motor_total_distance.png", dpi=300, pad_inches=0)
    plt.close(fig1)

    # =========================================================================
    # WYKRES 2: SUMA DYSTANSU HIGH-SPEED RUNNING (DODANA PEŁNA SKALA PIONOWA)
    # =========================================================================
    fig2, ax2 = plt.subplots(figsize=(16, 9), dpi=300)
    fig2.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax2.axis("off")
    ax2.imshow(mpimg.imread(str(BG_PATH)), extent=[0, 1920, 0, 1080])

    ax2.text(960, 1010, "INTENSYWNOŚĆ: SUMARYCZNY DYSTANS HIGH-SPEED RUNNING (HSR)", 
             color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    max_hsr = df_final["HSR_m_full"].max()
    scale_y2 = 530 / max_hsr

    # POPRAWKA: Wyrazista skala boczna dla realnych wartości HSR w metrach
    for hsr_val in [10000, 15000, 20000, 25000, 30000]:
        y_line = y_floor + hsr_val * scale_y2
        ax2.plot([start_x - 40, end_x + 40], [y_line, y_line], color="#FFFFFF", alpha=0.15, linestyle=":", zorder=1)
        ax2.text(start_x - 50, y_line, f"{hsr_val} m", color="#FFFFFF", alpha=0.6, fontsize=9, ha="right", va="center", fontweight="bold")

    for idx, match in df_final.iterrows():
        cx = x_coords[idx]
        hsr_m = match["HSR_m_full"]
        g, ga = int(match["true_goals"]), int(match["true_goals_opponent"])

        ax2.fill_between([cx - bar_width/2, cx + bar_width/2], y_floor, y_floor + hsr_m * scale_y2, color="#FFFFFF", zorder=2)
        ax2.text(cx, y_floor + hsr_m * scale_y2 + 10, f"{int(hsr_m)}m", color="#FFFFFF", fontsize=8, fontweight="bold", ha="center")

        dot_color = COLOR_WIN if g > ga else (COLOR_DRAW if g == ga else COLOR_LOSS)
        ax2.scatter(cx, y_floor - 45, s=200, color=dot_color, edgecolors="#FFFFFF", linewidths=1, zorder=3)
        ax2.text(cx, y_floor - 45, "W" if g > ga else ("R" if g == ga else "P"), color="#000000", fontsize=7, fontweight="bold", ha="center", va="center", zorder=4)
        add_club_logo(ax2, match["opponent"], cx, y_logo, zoom=0.50)

    ax2.set_xlim(0, 1920)
    ax2.set_ylim(0, 1080)
    fig2.savefig(PLOTS_DIR / "motor_total_hsr.png", dpi=300, pad_inches=0)
    plt.close(fig2)

    # =========================================================================
    # WYKRES 3: CAŁKOWITY DYSTANS SPRINTU W MECZU (WYRAZISTE LINIE POMOCNICZE)
    # =========================================================================
    fig3, ax3 = plt.subplots(figsize=(16, 9), dpi=300)
    fig3.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax3.axis("off")
    ax3.imshow(mpimg.imread(str(BG_PATH)), extent=[0, 1920, 0, 1080])

    ax3.text(960, 1010, "INTENSYWNOŚĆ: CAŁKOWITY DYSTANS SPRINTU W MECZU (M)", 
             color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    max_sprint = df_final["Sprint_Dist_m"].max()
    scale_y3 = 530 / max_sprint

    # Wyrazista skala boczna dla dystansu sprintów
    for spr_val in [1000, 1500, 2000, 2500, 3000]:
        y_line = y_floor + spr_val * scale_y3
        ax3.plot([start_x - 40, end_x + 40], [y_line, y_line], color="#FFFFFF", alpha=0.15, linestyle=":", zorder=1)
        ax3.text(start_x - 50, y_line, f"{spr_val} m", color="#FFFFFF", alpha=0.6, fontsize=9, ha="right", va="center", fontweight="bold")

    for idx, match in df_final.iterrows():
        cx = x_coords[idx]
        spr_m = match["Sprint_Dist_m"]
        g, ga = int(match["true_goals"]), int(match["true_goals_opponent"])

        ax3.fill_between([cx - bar_width/2, cx + bar_width/2], y_floor, y_floor + spr_m * scale_y3, color="#00FF66", zorder=2)
        ax3.text(cx, y_floor + spr_m * scale_y3 + 10, f"{int(spr_m)}m", color="#00FF66", fontsize=8, fontweight="bold", ha="center")

        dot_color = COLOR_WIN if g > ga else (COLOR_DRAW if g == ga else COLOR_LOSS)
        ax3.scatter(cx, y_floor - 45, s=200, color=dot_color, edgecolors="#FFFFFF", linewidths=1, zorder=3)
        ax3.text(cx, y_floor - 45, "W" if g > ga else ("R" if g == ga else "P"), color="#000000", fontsize=7, fontweight="bold", ha="center", va="center", zorder=4)
        add_club_logo(ax3, match["opponent"], cx, y_logo, zoom=0.50)

    ax3.set_xlim(0, 1920)
    ax3.set_ylim(0, 1080)
    fig3.savefig(PLOTS_DIR / "motor_total_sprint_distance.png", dpi=300, pad_inches=0)
    plt.close(fig3)
    
    print("🚀 Sukces! Wykresy motoryczne poprawione zgodnie z fizjologią meczową.")

if __name__ == "__main__":
    generate_motor_plots()