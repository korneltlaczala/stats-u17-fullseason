import os
import pandas as pd
import json
import tqdm
from rapidfuzz import process, fuzz, utils

DATA_DIR = "data"
DF_OUTPUT_DIR = os.path.join(DATA_DIR, "dfs")
MY_TEAM_ROUGH_NAME = "Polonia Warszawa"


def get_team_name(rough_name, matches_data):
    first_match = matches_data[0]
    host = first_match["host"]["name"]
    guest = first_match["guest"]["name"]
    return process.extractOne(rough_name, [host, guest])[0]

def create_matches_df(matches_data):
    rows = []
    for match in matches_data:
        is_home = match["host"]["name"] == MY_TEAM_NAME
        score_full_time = match["scores"]["fullTime"]
        score_half_time = match["scores"]["half"]
        goals_home = score_full_time.split(":")[0]
        
        goals_away = score_full_time.split(":")[1]
        goals_home_half = score_half_time.split(":")[0]
        goals_away_half = score_half_time.split(":")[1]
        row = {
            "pzpn_id": match["matchId"],
            "date_time": match["dateTime"],
            "opponent": match["guest"]["name"] if is_home else match["host"]["name"],
            "home_away": "home" if is_home else "away",
            "goals_for": int(goals_home) if is_home else int(goals_away),
            "goals_against": int(goals_away) if is_home else int(goals_home),
            "goals_for_half": int(goals_home_half) if is_home else int(goals_away_half),
            "goals_against_half": int(goals_away_half) if is_home else int(goals_home_half), 
            "stadium": match["stadium"],
            "eyeball_id": None
        }
        rows.append(row)

    return pd.DataFrame(rows)

def assign_eyeball_ids(matches_df):
    team_stats_eyeball_dir = f"{DATA_DIR}/team_stats_eyeball"
    viable_files = [f for f in os.listdir(team_stats_eyeball_dir)
                    if "team-stats" in f and "(" not in f and f.endswith(".csv")]

    hard_mappings = {
        "LKS LODZ": "ŁKS Łódź S.A.",
        "AKS SMS LODZ": "AKS SMS GROT ŁÓDŹ",
        "WIDZEW LODZ": "Widzew Łódź SA",
        "STAL RZESZOW": "Stal Rzeszów S.A.",
        "RESOVIA RZESOW": "SMS Resovia Rzeszów",
        "WISLA PLOCK": "S.S.M. Wisła Płock"
    }

    pzpn_home_pairs = {}
    pzpn_away_pairs = {}
    for idx, match in matches_df.iterrows():
        if match["home_away"] == "home":
            pzpn_home_pairs[match["opponent"]] = match["pzpn_id"]
        else:
            pzpn_away_pairs[match["opponent"]] = match["pzpn_id"]

    for filename in viable_files:
        eyeball_id = filename.split("-")[1]
        df_headers = pd.read_csv(os.path.join(team_stats_eyeball_dir, filename), sep=";", nrows=0)
        host_name_eyeball = df_headers.columns[2]
        guest_name_eyeball = df_headers.columns[3]

        my_team_name_eyeball = process.extractOne(MY_TEAM_ROUGH_NAME, [host_name_eyeball, guest_name_eyeball], scorer=fuzz.WRatio, processor=utils.default_process)[0]
        is_home = my_team_name_eyeball == host_name_eyeball
        oponent_name_eyeball = guest_name_eyeball if is_home else host_name_eyeball
        choices_dict = pzpn_home_pairs if is_home else pzpn_away_pairs

        first_check = process.extractOne(
            oponent_name_eyeball,
            hard_mappings.keys(),
            scorer=fuzz.WRatio,
            processor=utils.default_process,
        )
        oponent_matched_name = hard_mappings[first_check[0]] if first_check and first_check[1] > 90 else oponent_name_eyeball

        best_pzpn_match = process.extractOne(
            oponent_matched_name,
            choices_dict.keys(),
            scorer=fuzz.token_set_ratio,
            processor=utils.default_process,
        )

        matched_pzpn_id = choices_dict[best_pzpn_match[0]]
        if best_pzpn_match[1] < 80:
            print(f"Low confidence match for eyeball ID {eyeball_id}:")
            print(f"  Eyeball opponent: {oponent_name_eyeball}")
            print(f"  Best PZPN match: {best_pzpn_match[0]} with score {best_pzpn_match[1]}")
            print(f"  Matched PZPN ID: {matched_pzpn_id}")

        pzpn_opponent_name = matches_df[matches_df["pzpn_id"] == matched_pzpn_id]["opponent"].values[0]
        pzpn_home_away = matches_df[matches_df["pzpn_id"] == matched_pzpn_id]["home_away"].values[0]

        # print(oponent_name_eyeball) 
        # print(f"Eyeball match:\t{"home" if is_home else "away"} {oponent_name_eyeball} -> \nPZPN match:\t{pzpn_home_away} {pzpn_opponent_name} with id {matched_pzpn_id}\n")

        matches_df.loc[matches_df["pzpn_id"] == matched_pzpn_id, "eyeball_id"] = eyeball_id
    return matches_df


if __name__ == "__main__":
    os.makedirs(DF_OUTPUT_DIR, exist_ok=True)

    with open(f"{DATA_DIR}/played-matches.json", "r", encoding="utf-8") as f:
        matches_data = json.load(f)

    MY_TEAM_NAME = get_team_name(MY_TEAM_ROUGH_NAME, matches_data)
    print(f"My team name: {MY_TEAM_NAME}")

    matches_df = create_matches_df(matches_data)
    matches_df = assign_eyeball_ids(matches_df)
    matches_df.to_csv(f"{DF_OUTPUT_DIR}/matches.csv", index=False)

