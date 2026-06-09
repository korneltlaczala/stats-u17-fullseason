import os
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np

# Infrastruktura z util.py (katalogi, tło)
from util import DATA_DIR, BG_PATH, PLOTS_DIR

MOTOR_STATS_PATH = DATA_DIR / "dfs" / "motor_stats_full.csv"

def generate_player_motor_records():
    print("Agregowanie rekordów indywidualnych i sumarycznych dystansów (300 DPI)...")
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    if not MOTOR_STATS_PATH.exists():
        print(f"Błąd: Brak pliku {MOTOR_STATS_PATH}!")
        return

    # 1. WCZYTANIE I PRZYGOTOWANIE DANYCH
    df = pd.read_csv(MOTOR_STATS_PATH)
    df = df[df["Split Name"] == "all"].copy() # Tylko pełne mecze
    
    # Obliczamy HSR (Strefa 3 + Strefa 4) w metrach oraz Sprint w metrach
    # df["HSR_m"] = (df["Distance in Speed Zone 3  (km)"].astype(float) + df["Distance in Speed Zone 4  (km)"].astype(float)) * 1000
    df["HSR_m"] = (df["Distance in Speed Zone 3  (km)"].astype(float)) * 1000
    df["Sprint_m"] = df["Sprint Distance (m)"].astype(float)
    df["Distance_km"] = df["Distance (km)"].astype(float)
    
    # Czyszczenie nazwisk z ewentualnych spacji
    df["Player Name"] = df["Player Name"].str.strip()

    # Agregacja: szukamy maksa dla PB (rekordów) oraz sumy dla globalnego dystansu
    df_pb = df.groupby("Player Name").agg({
        "Sprint_m": "max",
        "HSR_m": "max",
        "Distance_km": "sum"
    }).reset_index()

    # Usuwamy ewentualne puste rekordy lub zerowe występy
    df_pb = df_pb[df_pb["Distance_km"] > 0]

    # Podkłady graficzne wspólne dla każdego slajdu
    bg_img = mpimg.imread(str(BG_PATH))

    # =========================================================================
    # WYKRES 1: REKORD SEZONU W SPRINTACH (PERSONAL BEST)
    # =========================================================================
    df_sprint = df_pb.sort_values(by="Sprint_m", ascending=True) # od dołu do góry w barh
    players_spr = df_sprint["Player Name"].values
    vals_spr = df_sprint["Sprint_m"].values
    n_players = len(players_spr)

    fig1, ax1 = plt.subplots(figsize=(16, 9), dpi=300)
    fig1.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax1.axis("off")
    ax1.imshow(bg_img, extent=[0, 1920, 0, 1080])

    ax1.text(960, 1010, "REKORDY SEZONU: MAKSYMALNY DYSTANS SPRINTU W JEDNYM MECZU (M)", 
             color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    ax_bars1 = fig1.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars1.set_facecolor("none")
    
    # Słupki sprintu na neonową zieleń Polonii
    bars1 = ax_bars1.barh(np.arange(n_players), vals_spr, color="#00FF66", height=0.55, edgecolor="none", zorder=3)
    for bar in bars1:
        w = bar.get_width()
        ax_bars1.text(w + 10, bar.get_y() + bar.get_height()/2, f"{int(w)} m", color="#FFFFFF", fontsize=8, fontweight="bold", ha="left", va="center")

    ax_bars1.set_yticks(np.arange(n_players))
    ax_bars1.set_yticklabels(players_spr, color="#FFFFFF", fontsize=9, fontweight="bold", ha="right")
    ax_bars1.set_xlim(0, max(vals_spr) * 1.1)
    ax_bars1.grid(axis="x", linestyle="--", alpha=0.12, color="#FFFFFF", zorder=1)
    for s in ["top", "right", "left", "bottom"]: ax_bars1.spines[s].set_visible(False)
    ax_bars1.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars1.tick_params(axis="x", colors="#AAAAAA")

    fig1.savefig(PLOTS_DIR / "player_motor_pb_sprint.png", dpi=300, pad_inches=0)
    plt.close(fig1)

    # =========================================================================
    # WYKRES 2: REKORD SEZONU W HIGH-SPEED RUNNING (PERSONAL BEST)
    # =========================================================================
    df_hsr = df_pb.sort_values(by="HSR_m", ascending=True)
    players_hsr = df_hsr["Player Name"].values
    vals_hsr = df_hsr["HSR_m"].values

    fig2, ax2 = plt.subplots(figsize=(16, 9), dpi=300)
    fig2.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax2.axis("off")
    ax2.imshow(bg_img, extent=[0, 1920, 0, 1080])

    ax2.text(960, 1010, "REKORDY SEZONU: MAKSYMALNY DYSTANS HIGH-SPEED RUNNING W JEDNYM MECZU (M)", 
             color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    ax_bars2 = fig2.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars2.set_facecolor("none")
    
    # Słupki HSR na czystą biel
    bars2 = ax_bars2.barh(np.arange(n_players), vals_hsr, color="#FFFFFF", height=0.55, edgecolor="none", zorder=3)
    for bar in bars2:
        w = bar.get_width()
        ax_bars2.text(w + 30, bar.get_y() + bar.get_height()/2, f"{int(w)} m", color="#FFFFFF", fontsize=8, fontweight="bold", ha="left", va="center")

    ax_bars2.set_yticks(np.arange(n_players))
    ax_bars2.set_yticklabels(players_hsr, color="#FFFFFF", fontsize=9, fontweight="bold", ha="right")
    ax_bars2.set_xlim(0, max(vals_hsr) * 1.1)
    ax_bars2.grid(axis="x", linestyle="--", alpha=0.12, color="#FFFFFF", zorder=1)
    for s in ["top", "right", "left", "bottom"]: ax_bars2.spines[s].set_visible(False)
    ax_bars2.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars2.tick_params(axis="x", colors="#AAAAAA")

    fig2.savefig(PLOTS_DIR / "player_motor_pb_hsr.png", dpi=300, pad_inches=0)
    plt.close(fig2)

    # =========================================================================
    # WYKRES 3: SUMA PRZEBIEGNIĘTEGO DYSTANSU W SEZONIE (RAZEM KM)
    # =========================================================================
    df_total = df_pb.sort_values(by="Distance_km", ascending=True)
    players_tot = df_total["Player Name"].values
    vals_tot = df_total["Distance_km"].values

    fig3, ax3 = plt.subplots(figsize=(16, 9), dpi=300)
    fig3.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax3.axis("off")
    ax3.imshow(bg_img, extent=[0, 1920, 0, 1080])

    ax3.text(960, 1010, "SUMA PRZEBIEGNIĘTEGO DYSTANSU WE WSZYSTKIECH MECZACH SEZONU (KM)", 
             color="#FFFFFF", fontsize=22, fontweight="bold", ha="center")

    ax_bars3 = fig3.add_axes([0.22, 0.08, 0.72, 0.84])
    ax_bars3.set_facecolor("none")
    
    # Słupki globalnego przebiegu na czystą biel
    bars3 = ax_bars3.barh(np.arange(n_players), vals_tot, color="#FFFFFF", height=0.55, edgecolor="none", zorder=3)
    for bar in bars3:
        w = bar.get_width()
        ax_bars3.text(w + 1.5, bar.get_y() + bar.get_height()/2, f"{w:.1f} km", color="#FFFFFF", fontsize=8, fontweight="bold", ha="left", va="center")

    ax_bars3.set_yticks(np.arange(n_players))
    ax_bars3.set_yticklabels(players_tot, color="#FFFFFF", fontsize=9, fontweight="bold", ha="right")
    ax_bars3.set_xlim(0, max(vals_tot) * 1.1)
    ax_bars3.grid(axis="x", linestyle="--", alpha=0.12, color="#FFFFFF", zorder=1)
    for s in ["top", "right", "left", "bottom"]: ax_bars3.spines[s].set_visible(False)
    ax_bars3.tick_params(axis="y", colors="#FFFFFF", pad=15)
    ax_bars3.tick_params(axis="x", colors="#AAAAAA")

    fig3.savefig(PLOTS_DIR / "player_motor_total_distance.png", dpi=300, pad_inches=0)
    plt.close(fig3)

    print("🚀 Sukces! Wygenerowano 3 nowe, niezależne rankingi indywidualne w plots/!")

if __name__ == "__main__":
    generate_player_motor_records()