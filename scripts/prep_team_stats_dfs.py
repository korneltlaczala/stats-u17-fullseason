import pandas as pd
import os

DATA_DIR = "data"
DFS_DIR = os.path.join(DATA_DIR, "dfs")
os.makedirs(DFS_DIR, exist_ok=True)


def generate_stats_df(matches_df, name_suffix=""):

    print(f"Generating stats DataFrame with suffix '{name_suffix}'...")

    rows_list = []
    for match in matches_df.itertuples():
        file_name = f"game-{match.eyeball_id}-team-stats{name_suffix}.csv"
        file_path = os.path.join(DATA_DIR, "team_stats_eyeball", file_name)

        if name_suffix == "":
            true_goals = match.goals_for
            true_goals_opponent = match.goals_against
        elif name_suffix == " (1)":
            true_goals = match.goals_for_half
            true_goals_opponent = match.goals_against_half
        elif name_suffix == " (2)":
            true_goals = match.goals_for - match.goals_for_half
            true_goals_opponent = match.goals_against - match.goals_against_half
        else:
            raise ValueError(f"Invalid name_suffix: {name_suffix}")
        true_goals = str(true_goals)
        true_goals_opponent = str(true_goals_opponent)

        if not os.path.exists(file_path):
            # print(f"🟨 Skipping match {match.home_away} {match.opponent} due to missing file with Eyeball stats.")
            print(f"🟨 No eyeball stats for match {match.home_away} {match.opponent}. Filling with NULL values")
            stats_row = {
                "pzpn_id": match.pzpn_id,
                "eyeball_id": match.eyeball_id,
                "home_away": match.home_away,
                "opponent": match.opponent,
                "date_time": match.date_time,
                "true_goals": true_goals,
                "true_goals_opponent": true_goals_opponent,
            }
            rows_list.append(stats_row)
            continue
        # if os.path.exists(file_path):
        #     print(f"🟩 File for match {match.home_away} {match.opponent} exists.")
        # else:
        #     print(f"🟥 Failed to find file for match {match.home_away} {match.opponent} does not exist.")

        eyeball_df = pd.read_csv(file_path, sep=";")
        is_home = match.home_away == "home"
   
        match_stats = {}
        for i, row in eyeball_df.iterrows():
            # if i < 1:
            #     continue
            stat_category = row["Category"].replace(" ", "_").lower()
            stat_name = row["Statistic"].replace(" ", "_").lower()
            team_stat_value = row.iloc[2] if is_home else row.iloc[3]
            opponent_stat_value = row.iloc[3] if is_home else row.iloc[2]

            match_stats[f"{stat_name}"] = team_stat_value
            match_stats[f"{stat_name}_opponent"] = opponent_stat_value

        all_goals_recognized = (match_stats["goals"] == true_goals) and (match_stats["goals_opponent"] == true_goals_opponent)
        # print(f"Match {match.home_away} {match.opponent} - True goals: {true_goals}, Recognized goals: {match_stats['goals']}, True goals opponent: {true_goals_opponent}, Recognized goals opponent: {match_stats['goals_opponent']}, All goals recognized: {all_goals_recognized}")

        stats_row = {
            "pzpn_id": match.pzpn_id,
            "eyeball_id": match.eyeball_id,
            "home_away": match.home_away,
            "opponent": match.opponent,
            "date_time": match.date_time,
            "true_goals": true_goals,
            "true_goals_opponent": true_goals_opponent,
            **match_stats,
            "all_goals_recognized": all_goals_recognized
        }
        rows_list.append(stats_row)

    stats_df = pd.DataFrame(rows_list)
    return stats_df



if __name__ == "__main__":
    matches_df = pd.read_csv(os.path.join(DFS_DIR, "matches.csv"), dtype={"eyeball_id": str})
    full_stats_df = generate_stats_df(matches_df, name_suffix="")
    h1_stats_df = generate_stats_df(matches_df, name_suffix=" (1)")
    h2_stats_df = generate_stats_df(matches_df, name_suffix=" (2)")
    full_stats_df.to_csv(os.path.join(DFS_DIR, "stats_full.csv"), index=False)
    h1_stats_df.to_csv(os.path.join(DFS_DIR, "stats_half1.csv"), index=False)
    h2_stats_df.to_csv(os.path.join(DFS_DIR, "stats_half2.csv"), index=False)