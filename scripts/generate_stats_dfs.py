import pandas as pd
import os

DATA_DIR = "data"
DFS_DIR = os.path.join(DATA_DIR, "dfs")
os.makedirs(DFS_DIR, exist_ok=True)


def generate_stats_df(matches_df, name_suffix=""):

    print(f"Generating stats DataFrame with suffix '{name_suffix}'...")

    for match in matches_df.itertuples():
        file_name = f"game-{match.eyeball_id}-team-stats{name_suffix}.csv"
        file_path = os.path.join(DATA_DIR, "team_stats_eyeball", file_name)

        # if os.path.exists(file_path):
        #     print(f"🟩 File for match {match.home_away} {match.opponent} exists.")
        # else:
        #     print(f"🟥 Failed to find file for match {match.home_away} {match.opponent} does not exist.")

        eyeball_df = pd.read_csv(file_path, sep=";")
        is_home = match.home_away == "home"
   
        match_stats = {}
        for i, row in eyeball_df.iterrows():
            if i < 1:
                continue
            stat_category = row["Category"].replace(" ", "_").lower()
            stat_name = row["Statistic"].replace(" ", "_").lower()
            team_stat_value = row[2] if is_home else row[3]
            opponent_stat_value = row[3] if is_home else row[2]

            match_stats[f"{stat_name}"] = team_stat_value
            match_stats[f"{stat_name}_opponent"] = opponent_stat_value
        
        print(match_stats)
        return



if __name__ == "__main__":
    matches_df = pd.read_csv(os.path.join(DFS_DIR, "matches.csv"), dtype={"eyeball_id": str})
    full_stats_df = generate_stats_df(matches_df, name_suffix="")
    # h1_stats_df = generate_stats_df(matches_df, name_suffix=" (1)")
    # h2_stats_df = generate_stats_df(matches_df, name_suffix=" (2)")
    pass