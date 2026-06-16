import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Infrastruktura zutil.py (katalogi, tło)
from util import DATA_DIR, BG_PATH, PLOTS_DIR

# Ścieżki do plików przy użyciu pathlib (rozwiązuje błąd AttributeError)
BRAMKI_PATH = DATA_DIR / "dfs" / "bramki_u17_2009_lista.csv"
ASYSTY_PATH = DATA_DIR / "dfs" / "asysty_u17_2009_lista.csv"

def generate_all_plots():
    print("Agregowanie danych i generowanie trzech zestawień CLJ U-17 (300 DPI)...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not BRAMKI_PATH.exists() or not ASYSTY_PATH.exists():
        print(f"Błąd: Brak plików z danymi ({BRAMKI_PATH} lub {ASYSTY_PATH})!")
        return

    # 1. Wczytanie danych z jawnym wskazaniem kodowania (rozwiązuje błąd UnicodeDecodeError)
    df_bramki = pd.read_csv(BRAMKI_PATH)
    df_asysty = pd.read_csv(ASYSTY_PATH)

    # Łączenie tabel (outer join) i czyszczenie braków danych
    df_all = pd.merge(df_bramki, df_asysty, on='nazwisko', how='outer')
    df_all['liczba_bramek'] = df_all['liczba_bramek'].fillna(0).astype(int)
    df_all['liczba_asyst'] = df_all['liczba_asyst'].fillna(0).astype(int)
    df_all['suma'] = df_all['liczba_bramek'] + df_all['liczba_asyst']

    # Wczytanie obrazu tła raz (optymalizacja wydajności)
    try:
        bg_img = mpimg.imread(str(BG_PATH))
    except Exception as e:
        print(f"Ostrzeżenie: Nie udało się wczytać tła ({e}). Rysuję bez obrazka w tle.")
        bg_img = None

    # =========================================================================
    # WYKRES 1: KLASYFIKACJA KANADYJSKA (Bramki + Asysty)
    # =========================================================================
    print(" -> Generowanie klasyfikacji kanadyjskiej...")
    df_kan = df_all[df_all["suma"] > 0].sort_values(by=["suma", "liczba_bramek"], ascending=True)
    
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    if bg_img is not None:
        ax.imshow(bg_img, extent=[0, 1920, 0, 1080])
    else:
        ax.set_xlim(0, 1920)
        ax.set_ylim(0, 1080)

    ax.text(960, 1010, "KLASYFIKACJA KANADYJSKA: CENTRALNA LIGA JUNIORÓW U-17", color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")
    ax.text(960, 960, "BIAŁY = BRAMKI   |   SZARY = ASYSTY", color="#AAAAAA", fontsize=11, fontweight="bold", ha="center")

    ax_bars = fig.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars.set_facecolor("none")
    
    num_players = len(df_kan)
    ax_bars.barh(np.arange(num_players), df_kan["liczba_bramek"], color="#FFFFFF", height=0.55, edgecolor="none", zorder=3)
    ax_bars.barh(np.arange(num_players), df_kan["liczba_asyst"], left=df_kan["liczba_bramek"], color="#AAAAAA", height=0.55, edgecolor="none", zorder=3)

    for i, total in enumerate(df_kan["suma"]):
        ax_bars.text(total + 0.2, i, f"{total}", color="#00FF66", fontsize=10, fontweight="bold", ha="left", va="center", zorder=4)

    ax_bars.set_yticks(np.arange(num_players))
    ax_bars.set_yticklabels(df_kan["nazwisko"], color="#FFFFFF", fontsize=10, fontweight="bold", ha="right")
    max_pts = int(df_kan["suma"].max()) if num_players > 0 else 10
    ax_bars.set_xlim(0, max_pts + 1)
    ticks_step = 1 if max_pts <= 12 else 2
    ax_bars.set_xticks(np.arange(0, max_pts + 1, ticks_step))
    ax_bars.grid(axis="x", linestyle="--", alpha=0.15, color="#FFFFFF", zorder=1)
    for spine in ["top", "right", "left", "bottom"]: ax_bars.spines[spine].set_visible(False)
    ax_bars.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars.tick_params(axis="x", colors="#AAAAAA", pad=10)

    plt.savefig(PLOTS_DIR / "player_kanadyjska_clj_ranking.png", dpi=300, pad_inches=0, transparent=False)
    plt.close()

    # =========================================================================
    # WYKRES 2: KLASYFIKACJA STRZELCÓW (Tylko Bramki)
    # =========================================================================
    print(" -> Generowanie klasyfikacji strzelców...")
    df_goals = df_all[df_all["liczba_bramek"] > 0].sort_values(by="liczba_bramek", ascending=True)
    
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    if bg_img is not None:
        ax.imshow(bg_img, extent=[0, 1920, 0, 1080])
    else:
        ax.set_xlim(0, 1920)
        ax.set_ylim(0, 1080)

    ax.text(960, 1010, "KLASYFIKACJA STRZELCÓW: CENTRALNA LIGA JUNIORÓW U-17", color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    ax_bars = fig.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars.set_facecolor("none")
    
    num_players = len(df_goals)
    ax_bars.barh(np.arange(num_players), df_goals["liczba_bramek"], color="#FFFFFF", height=0.55, edgecolor="none", zorder=3)

    for i, val in enumerate(df_goals["liczba_bramek"]):
        ax_bars.text(val + 0.2, i, f"{val}", color="#00FF66", fontsize=10, fontweight="bold", ha="left", va="center", zorder=4)

    ax_bars.set_yticks(np.arange(num_players))
    ax_bars.set_yticklabels(df_goals["nazwisko"], color="#FFFFFF", fontsize=10, fontweight="bold", ha="right")
    max_vals = int(df_goals["liczba_bramek"].max()) if num_players > 0 else 10
    ax_bars.set_xlim(0, max_vals + 1)
    ticks_step = 1 if max_vals <= 12 else 2
    ax_bars.set_xticks(np.arange(0, max_vals + 1, ticks_step))
    ax_bars.grid(axis="x", linestyle="--", alpha=0.15, color="#FFFFFF", zorder=1)
    for spine in ["top", "right", "left", "bottom"]: ax_bars.spines[spine].set_visible(False)
    ax_bars.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars.tick_params(axis="x", colors="#AAAAAA", pad=10)

    plt.savefig(PLOTS_DIR / "player_goals_clj_ranking.png", dpi=300, pad_inches=0, transparent=False)
    plt.close()

    # =========================================================================
    # WYKRES 3: KLASYFIKACJA ASYSTENTÓW (Tylko Asysty)
    # =========================================================================
    print(" -> Generowanie klasyfikacji asystentów...")
    df_assists = df_all[df_all["liczba_asyst"] > 0].sort_values(by="liczba_asyst", ascending=True)
    
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    if bg_img is not None:
        ax.imshow(bg_img, extent=[0, 1920, 0, 1080])
    else:
        ax.set_xlim(0, 1920)
        ax.set_ylim(0, 1080)

    ax.text(960, 1010, "KLASYFIKACJA ASYSTENTÓW: CENTRALNA LIGA JUNIORÓW U-17", color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    ax_bars = fig.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars.set_facecolor("none")
    
    num_players = len(df_assists)
    ax_bars.barh(np.arange(num_players), df_assists["liczba_asyst"], color="#FFFFFF", height=0.55, edgecolor="none", zorder=3)

    for i, val in enumerate(df_assists["liczba_asyst"]):
        ax_bars.text(val + 0.2, i, f"{val}", color="#00FF66", fontsize=10, fontweight="bold", ha="left", va="center", zorder=4)

    ax_bars.set_yticks(np.arange(num_players))
    ax_bars.set_yticklabels(df_assists["nazwisko"], color="#FFFFFF", fontsize=10, fontweight="bold", ha="right")
    max_vals = int(df_assists["liczba_asyst"].max()) if num_players > 0 else 10
    ax_bars.set_xlim(0, max_vals + 1)
    ticks_step = 1 if max_vals <= 12 else 2
    ax_bars.set_xticks(np.arange(0, max_vals + 1, ticks_step))
    ax_bars.grid(axis="x", linestyle="--", alpha=0.15, color="#FFFFFF", zorder=1)
    for spine in ["top", "right", "left", "bottom"]: ax_bars.spines[spine].set_visible(False)
    ax_bars.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars.tick_params(axis="x", colors="#AAAAAA", pad=10)

    plt.savefig(PLOTS_DIR / "player_assists_clj_ranking.png", dpi=300, pad_inches=0, transparent=False)
    plt.close()
    
    print("\n🚀 Sukces! Wygenerowano 3 pliki graficzne w folderze docelowym.")

if __name__ == "__main__":
    generate_all_plots()