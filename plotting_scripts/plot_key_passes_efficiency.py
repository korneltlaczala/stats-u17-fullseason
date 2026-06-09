import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import pandas as pd
import numpy as np
from util import DATA_DIR, BG_PATH, PLOTS_DIR, add_club_logo, COLOR_WIN, COLOR_DRAW, COLOR_LOSS

STATS_FULL_PATH = DATA_DIR / "dfs" / "stats_full.csv"

def generate_key_passes_plot():
    df = pd.read_csv(STATS_FULL_PATH)
    df["date_time"] = pd.to_datetime(df["date_time"])
    df = df.sort_values("date_time").dropna(subset=["key_passes"]).reset_index(drop=True)
    
    # Mapowanie kolumn podań kluczowych
    df["all_kp"] = df["key_passes"].astype(int)
    # W danych Eyeballa mamy 'key_passes' (total) oraz 'key_passes_opponent'
    # Przyjmujemy 'key_passes' jako kluczowe podania, a jako "celne/udane" 
    # potraktujemy je w odniesieniu do akcji (z braku dedykowanej kolumny successful_key)
    # Jeśli masz dedykowaną kolumnę 'successful_key_passes', podmień poniżej:
    df["suc_kp"] = df["key_passes"].astype(int) # Tu dopasuj, jeśli masz dane o celności
    
    df["g"] = df["goals"].astype(int)
    df["g_ag"] = df["goals_opponent"].astype(int)

    df_w = df[df["g"] > df["g_ag"]]
    df_l = df[df["g"] < df["g_ag"]]
    
    num_matches = len(df)
    fig, ax = plt.subplots(figsize=(16, 9), dpi=300)
    fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
    ax.axis("off")

    bg_img = mpimg.imread(str(BG_PATH))
    ax.imshow(bg_img, extent=[0, 1920, 0, 1080])

    ax.text(960, 1020, "PRODUKTYWNOŚĆ: KLUCZOWE PODANIA (KEY PASSES)", 
            color="#FFFFFF", fontsize=24, fontweight="bold", ha="center")

    # DASHBOARD KOŁOWY (Zmieniony pod kluczowe podania)
    def draw_3d_donut(pos, avg_w, avg_l, title):
        ax_d = fig.add_axes(pos)
        ax_d.pie([avg_w, avg_l], colors=[COLOR_WIN, COLOR_LOSS], 
                 startangle=140, wedgeprops=dict(width=0.4, edgecolor="#1A1A1A"), counterclock=False)
        ax_d.text(0, 0, f"{title}\nW:{avg_w:.1f}\nP:{avg_l:.1f}", 
                  color="#FFFFFF", fontsize=9, ha="center", va="center", fontweight="bold")

    draw_3d_donut([0.30 - 0.09, 0.75, 0.18, 0.18], df_w["all_kp"].mean(), df_l["all_kp"].mean(), "KLUCZOWE")
    draw_3d_donut([0.50 - 0.09, 0.75, 0.18, 0.18], df_w["g"].mean(), df_l["g"].mean(), "BRAMKI")
    # Trzecie koło jako wskaźnik ogólnej kreatywności
    draw_3d_donut([0.70 - 0.09, 0.75, 0.18, 0.18], df_w["all_kp"].sum()/len(df_w), df_l["all_kp"].sum()/len(df_l), "ŚR. NA MECZ")

    # SŁUPKI
    start_x, end_x = 220, 1720
    x_coords = np.linspace(start_x, end_x, num_matches)
    bar_width = 24
    y_floor = 250
    y_logo = 150
    max_kp = df["all_kp"].max()
    scale_y = 300 / max_kp

    for idx, match in df.iterrows():
        cx = x_coords[idx]
        all_kp = match["all_kp"]
        
        ax.fill_between([cx - bar_width/2, cx + bar_width/2], y_floor, y_floor + all_kp*scale_y, color="#3A3A3A", zorder=2)
        ax.text(cx, y_floor + all_kp*scale_y + 15, str(all_kp), color="#00FF66", fontsize=8, fontweight="bold", ha="center")

        dot_color = COLOR_WIN if match["g"] > match["g_ag"] else (COLOR_DRAW if match["g"] == match["g_ag"] else COLOR_LOSS)
        ax.scatter(cx, y_floor - 50, s=250, color=dot_color, edgecolors="#FFFFFF", linewidth=1, zorder=5)
        ax.text(cx, y_floor - 50, "W" if match["g"] > match["g_ag"] else ("R" if match["g"] == match["g_ag"] else "P"), 
                color="#000000", fontsize=7, fontweight="bold", ha="center", va="center", zorder=6)

        add_club_logo(ax, match["opponent"], cx, y_logo, zoom=0.45)

    ax.set_xlim(0, 1920)
    ax.set_ylim(0, 1080)
    plt.savefig(PLOTS_DIR / "key_passes_timeline.png", dpi=300, pad_inches=0)
    plt.close()
    print("🚀 Wygenerowano dashboard podań kluczowych!")

if __name__ == "__main__":
    generate_key_passes_plot()