import os
import pandas as pd

# Ścieżki do folderów
DATA_DIR = "data"
DFS_DIR = os.path.join(DATA_DIR, "dfs")
PLAYER_STATS_DIR = os.path.join(DATA_DIR, "player_stats_eyeball")

# Tworzymy folder na ramki danych, jeśli nie istnieje
os.makedirs(DFS_DIR, exist_ok=True)


def generate_player_stats_df(matches_df, name_suffix=""):
    print(f"Generowanie DataFrame statystyk zawodników z sufiksem '{name_suffix}'...")
    all_player_rows = []

    for match in matches_df.itertuples():
        # Podstawowe dane z PZPN i matches.csv, które chcemy mieć w każdym wierszu zawodnika
        base_info = {
            "pzpn_id": match.pzpn_id,
            "eyeball_id": match.eyeball_id,
            "home_away": match.home_away,
            "opponent": match.opponent,
            "date_time": match.date_time,
        }

        # Jeśli mecz nie ma eyeball_id, tworzymy pusty rekord zawodnika (same dane PZPN)
        # To zapewni spójność i obecność meczu w bazie danych
        if pd.isna(match.eyeball_id) or match.eyeball_id == "":
            # Dodajemy jeden pusty wiersz "brak danych" dla tego meczu, żeby zachować go na osi czasu
            empty_row = {**base_info, "Player name": "BRAK_DANYCH_EYEBALL"}
            all_player_rows.append(empty_row)
            continue

        # Budujemy nazwę pliku, np. game-58937-player-stats (1).csv lub game-58937-player-stats.csv
        file_name = f"game-{match.eyeball_id}-player-stats{name_suffix}.csv"
        file_path = os.path.join(PLAYER_STATS_DIR, file_name)

        if not os.path.exists(file_path):
            print(f"  Brak pliku ze statystykami zawodników dla meczu z: {match.opponent} ({file_name})")
            # Jeśli pliku fizycznie nie ma, traktujemy to jako brak danych
            empty_row = {**base_info, "Player name": "BRAK_PLIKU_STATS"}
            all_player_rows.append(empty_row)
            continue

        try:
            # Wczytujemy plik zawodników. Pliki zawodników używają średnika (;) jako separatora
            player_df = pd.read_csv(file_path, sep=";")
            
            # Filtrujemy, aby wyciągnąć tylko zawodników Polonii Warszawa
            # Eyeball czasami zapisuje to jako "MKS POLONIA WARSZAWA" lub "POLONIA WARSZAWA"
            player_df = player_df[player_df["Team"].str.contains("POLONIA WARSZAWA", case=False, na=False)]

            # Iterujemy po każdym zawodniku w tym meczu
            for _, row in player_df.iterrows():
                # Zamieniamy wiersz z pliku na słownik
                player_stats = row.to_dict()
                
                # Łączymy dane meczu (PZPN) ze statystykami konkretnego zawodnika
                combined_row = {**base_info, **player_stats}
                all_player_rows.append(combined_row)

        except Exception as e:
            print(f"  Błąd podczas przetwarzania pliku {file_name}: {e}")
            continue

    # Tworzymy końcowy DataFrame
    if all_player_rows:
        return pd.DataFrame(all_player_rows)
    else:
        return pd.DataFrame()


if __name__ == "__main__":
    # Wczytujemy bazę meczów (musi zawierać zmapowane eyeball_id!)
    matches_df_path = os.path.join(DFS_DIR, "matches.csv")
    
    if not os.path.exists(matches_df_path):
        print(f"Błąd: Nie znaleziono pliku {matches_df_path}. Uruchom najpierw skrypt prep_matches_df.py!")
    else:
        matches_df = pd.read_csv(matches_df_path, dtype={"eyeball_id": str})

        # 1. Całe mecze
        player_full_df = generate_player_stats_df(matches_df, name_suffix="")
        if not player_full_df.empty:
            player_full_df.to_csv(os.path.join(DFS_DIR, "player_stats_full.csv"), index=False)
            print(f"Zapisano: player_stats_full.csv ({len(player_full_df)} wierszy)")

        # 2. Pierwsza połowa
        player_h1_df = generate_player_stats_df(matches_df, name_suffix=" (1)")
        if not player_h1_df.empty:
            player_h1_df.to_csv(os.path.join(DFS_DIR, "player_stats_half1.csv"), index=False)
            print(f"Zapisano: player_stats_half1.csv ({len(player_h1_df)} wierszy)")

        # 3. Druga połowa
        player_h2_df = generate_player_stats_df(matches_df, name_suffix=" (2)")
        if not player_h2_df.empty:
            player_h2_df.to_csv(os.path.join(DFS_DIR, "player_stats_half2.csv"), index=False)
            print(f"Zapisano: player_stats_half2.csv ({len(player_h2_df)} wierszy)")

        print("\nWszystkie dane zawodników zostały pomyślnie przetworzone!")