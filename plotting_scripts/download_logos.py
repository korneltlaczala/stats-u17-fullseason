import json
import os
import requests
from util import JSON_PATH, LOGOS_DIR, get_safe_team_name

def download_logos():
    print(f"Rozpoczynam sprawdzanie i pobieranie herbów do folderu: {LOGOS_DIR}")
    LOGOS_DIR.mkdir(parents=True, exist_ok=True)

    if not JSON_PATH.exists():
        print(f"Błąd: Nie znaleziono pliku JSON z meczami w ścieżce: {JSON_PATH}")
        return

    with open(JSON_PATH, "r", encoding="utf-8") as f:
        matches_data = json.load(f)

    # Wyciągamy unikalne zespoły z bazy
    teams_logos = {}
    for match in matches_data:
        # Gospodarz
        h_name = match["host"]["name"].strip()
        teams_logos[h_name] = match["host"]["logo"]
        # Gość
        g_name = match["guest"]["name"].strip()
        teams_logos[g_name] = match["guest"]["logo"]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    success_count = 0
    exist_count = 0

    for team_name, url in teams_logos.items():
        safe_name = get_safe_team_name(team_name)
        file_path = LOGOS_DIR / f"{safe_name}.png"

        if file_path.exists():
            exist_count += 1
            continue

        try:
            print(f"  [GET] Pobieranie herbu: {team_name}...")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                with open(file_path, "wb") as img_f:
                    img_f.write(response.content)
                success_count += 1
            else:
                print(f"  [!] Problem z kodem HTTP dla {team_name}: {response.status_code}")
        except Exception as e:
            print(f"  [BŁĄD] Nie udało się pobrać loga dla {team_name}: {e}")

    print(f"\n⚡ Raport końcowy:")
    print(f"  - Herby już istniejące lokalnie: {exist_count}")
    print(f"  - Nowo pobrane herby: {success_count}")
    print("Wszystko gotowe do generowania wykresów!")

if __name__ == "__main__":
    download_logos()