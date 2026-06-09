import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
from util import DATA_DIR, BG_PATH, PLOTS_DIR, add_club_logo, COLOR_WIN, COLOR_DRAW, COLOR_LOSS

STATS_FULL_PATH = DATA_DIR / "dfs" / "stats_full.csv"

def generate_passing_efficiency_plot():
    df = pd.read_csv(STATS_FULL_PATH)
    df["date_time"] = pd.to_datetime(df["date_time"])
    
    # Filtrujemy tylko mecze, gdzie mamy dane o podaniach
    df = df.sort_values("date_time").dropna(subset=["all_forward_passes"]).reset_index(drop=True)
    
    # Mapowanie kolumn podań do przodu
    df["all_fwd"] = df["all_forward_passes"].astype(int)
    df["suc_fwd"] = df["successful_forward_passes"].astype(int)
    df["acc_fwd"] = (df["suc_fwd"] / df["all_fwd"]) * 100
    
    df["g"] = df["goals"].astype(int)
    df["g_ag"] = df["goals_opponent"].astype(int)

    # Podział na wygrane i przegrane
    df_w = df[df["g"] > df["g_ag"]]
    df_l = df[df["g"] < df["g_ag"]]
    
    num_matches = len(df)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    ax.text(960, 1000, "PRODUKTYWNOŚĆ: PODANIA DO PRZODU (FORWARD PASSES)", 
            color="#FFFFFF", fontsize=24, fontweight="bold", ha="center")

    # DASHBOARD KOŁOWY
    def draw_3d_donut(pos, avg_w, avg_l, title):
        ax_d = fig.add_axes(pos)
        ax_d.pie([avg_w, avg_l], colors=[COLOR_WIN, COLOR_LOSS], 
                 startangle=140, wedgeprops=dict(width=0.4, edgecolor="#1A1A1A"), counterclock=False)
        ax_d.text(0, 0, f"{title}\nW:{avg_w:.1f}\nP:{avg_l:.1f}", 
                  color="#FFFFFF", fontsize=8, ha="center", va="center", fontweight="bold")

    donut_size = 0.18
    donut_height = 0.75
    draw_3d_donut([0.28 - donut_size/2, donut_height, donut_size, donut_size], df_w["all_fwd"].mean(), df_l["all_fwd"].mean(), "WSZYSTKIE")
    draw_3d_donut([0.48 - donut_size/2, donut_height, donut_size, donut_size], df_w["suc_fwd"].mean(), df_l["suc_fwd"].mean(), "CELNE")
    draw_3d_donut([0.68 - donut_size/2, donut_height, donut_size, donut_size], df_w["acc_fwd"].mean(), df_l["acc_fwd"].mean(), "CELNOŚĆ %")

    # SŁUPKI PODAŃ
    start_x, end_x = 220, 1720
    x_coords = np.linspace(start_x, end_x, num_matches)
    bar_width = 24
    y_floor = 250
    y_logo = 150
    
    max_fwd = df["all_fwd"].max()
    scale_y = 350 / max_fwd

    for idx, match in df.iterrows():
        cx = x_coords[idx]
        all_f = match["all_fwd"]
        suc_f = match["suc_fwd"]
        
        # Słupki: szary (wszystkie), zielony (celne)
        ax.fill_between([cx - bar_width/2, cx + bar_width/2], y_floor, y_floor + all_f*scale_y, color="#3A3A3A", zorder=2)
        ax.fill_between([cx - bar_width/2, cx + bar_width/2], y_floor, y_floor + suc_f*scale_y, color="#00FF66", zorder=3)

        # Liczby nad słupkami
        ax.text(cx, y_floor + all_f*scale_y + 15, str(all_f), color="#AAAAAA", fontsize=7, ha="center")
        ax.text(cx, y_floor + suc_f*scale_y + 5, str(suc_f), color="#00FF66", fontsize=8, fontweight="bold", ha="center")

        # Wynik
        dot_color = COLOR_WIN if match["g"] > match["g_ag"] else (COLOR_DRAW if match["g"] == match["g_ag"] else COLOR_LOSS)
        ax.scatter(cx, y_floor - 50, s=200, color=dot_color, edgecolors="#FFFFFF", linewidth=1, zorder=5)
        
        add_club_logo(ax, match["opponent"], cx, y_logo, zoom=0.45)

    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    plt.savefig(PLOTS_DIR / "forward_passing_timeline.png", dpi=300, pad_inches=0)
    plt.close()
    print("🚀 Gotowe! Wykres podań wygenerowany.")

if __name__ == "__main__":
    generate_passing_efficiency_plot()