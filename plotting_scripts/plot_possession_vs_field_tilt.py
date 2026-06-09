import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
from util import DATA_DIR, BG_PATH, PLOTS_DIR, COLOR_WIN, COLOR_DRAW, COLOR_LOSS

STATS_FULL_PATH = DATA_DIR / "dfs" / "stats_full.csv"

def generate_possession_tilt_plot():
    df = pd.read_csv(STATS_FULL_PATH)
    df = df.dropna(subset=["possessions", "field_tilt"]).copy()

    def clean_pct(val):
        if isinstance(val, str):
            return float(val.replace('%', '').strip())
        return float(val)
    
    df["pos"] = df["possessions"].apply(clean_pct)
    df["tilt"] = df["field_tilt"].apply(clean_pct)
    
    # Logika wyniku: 1=Win, 0=Draw, -1=Loss
    df["res_code"] = df.apply(lambda row: 1 if row["goals"] > row["goals_opponent"] 
                              else (0 if row["goals"] == row["goals_opponent"] else -1), axis=1)
    
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")
    
    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    # 1. Tytuł
    ax.text(960, 950, "POSIADANIE PIŁKI A WYNIKI", 
            color="#FFFFFF", fontsize=28, fontweight="bold", ha="center")

    # 2. WYKRES SCATTER (Własne axes)
    ax_scatter = fig.add_axes([0.15, 0.10, 0.7, 0.7])  # [left, bottom, width, height] w proporcjach do figury
    
    # Linia trendu
    z = np.polyfit(df["pos"], df["tilt"], 1)
    p = np.poly1d(z)
    ax_scatter.plot([df["pos"].min(), df["pos"].max()], [p(df["pos"].min()), p(df["pos"].max())], 
                    color="#AAAAAA", linestyle="--", alpha=0.3, zorder=1)

    # Kropki meczowe z odpowiednią kolorystyką
    for _, match in df.iterrows():
        # Kolorowanie: 1=Zielony, 0=Żółty, -1=Czerwony
        if match["res_code"] == 1: color = COLOR_WIN
        elif match["res_code"] == 0: color = COLOR_DRAW
        else: color = COLOR_LOSS
            
        ax_scatter.scatter(match["pos"], match["tilt"], s=350, color=color, edgecolors="#FFFFFF", linewidth=1.2, zorder=3)
        ax_scatter.text(match["pos"], match["tilt"] + 1.8, match["opponent"][:3].upper(), 
                        color="#FFFFFF", fontsize=7, ha="center", alpha=0.9)

    # Stylizacja osi
    ax_scatter.set_facecolor("#1A1A1A")
    ax_scatter.grid(True, linestyle=":", alpha=0.2)
    ax_scatter.set_xlabel("POSIADANIE PIŁKI (%)", color="#FFFFFF", fontsize=14, fontweight="bold")
    ax_scatter.set_ylabel("FIELD TILT (%)", color="#FFFFFF", fontsize=14, fontweight="bold")
    ax_scatter.tick_params(axis='x', colors="#FFFFFF", labelsize=12)
    ax_scatter.tick_params(axis='y', colors="#FFFFFF", labelsize=12)
    
    plt.savefig(PLOTS_DIR / "possession_vs_tilt.png", dpi=300, pad_inches=0)
    plt.close()
    print("🚀 Wykres korelacji gotowy: Wygrane(Ziel), Remisy(Złoty), Przegrane(Czerw)!")

if __name__ == "__main__":
    generate_possession_tilt_plot()