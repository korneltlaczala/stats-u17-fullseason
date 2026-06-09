import os
from pathlib import Path
from PIL import Image
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Ścieżki bazowe wyciągane dynamicznie względem pliku util.py
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DFS_DIR = DATA_DIR / "dfs"
LOGOS_DIR = BASE_DIR / "sources" / "logos"
BG_PATH = BASE_DIR / "sources" / "background.png"
PLOTS_DIR = BASE_DIR / "plots"

# KLUCZOWA POPRAWKA: Definiujemy brakującą ścieżkę do pliku z meczami JSON
JSON_PATH = DATA_DIR / "played-matches.json"
MATCHES_CSV_PATH = DFS_DIR / "matches.csv"

# Globalny styl wizualny dopasowany do Polonii Warszawa i grafiki z DALL-E
FONT_COLOR = "#FFFFFF"
FONT_NAME = "sans-serif"  # Matplotlib domyślnie użyje bezpiecznego sans-serif

# Paleta kolorów meczowych (Neonowe, odcinające się od ciemnego tła)
COLOR_WIN = "#00FF66"      # Soczysty zielony
COLOR_DRAW = "#FFCC00"     # Złoty/Żółty
COLOR_LOSS = "#FF3333"     # Agresywny czerwony

def get_safe_team_name(team_name):
    """Konwertuje oficjalną nazwę zespołu na bezpieczny format nazwy pliku."""
    if not isinstance(team_name, str):
        return "unknown"
    name = team_name.replace(" S.A.", "").replace(" SA", "").strip()
    return (
        name.lower()
        .replace(" ", "_")
        .replace(".", "")
        .replace("-", "_")
        .replace("ł", "l")
        .replace("ó", "o")
        .replace("ś", "s")
        .replace("ą", "a")
        .replace("ę", "e")
        .replace("ć", "c")
        .replace("ń", "n")
        .replace("ź", "z")
        .replace("ż", "z")
    )

from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from PIL import Image, ImageDraw

def add_club_logo(ax, team_name, x, y, zoom=1.0, box_alignment=(0.5, 0.5)):
    """
    Wczytuje herb, wpisuje go w eleganckie białe kółko ze zmniejszonym marginesem.
    """
    safe_name = get_safe_team_name(team_name)
    logo_path = LOGOS_DIR / f"{safe_name}.png"
    
    if not logo_path.exists():
        return False

    try:
        logo_img = Image.open(logo_path).convert("RGBA")
        size = (120, 120)
        circle_img = Image.new("RGBA", size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(circle_img)
        
        draw.ellipse([0, 0, size[0]-1, size[1]-1], fill=(255, 255, 255, 255))
        
        # POPRAWKA: Margines zmniejszony z 16 na 10, aby logo zajmowało więcej miejsca
        margin = 10  
        max_logo_size = size[0] - (margin * 2)
        
        logo_img.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)
        
        logo_w, logo_h = logo_img.size
        offset_x = (size[0] - logo_w) // 2
        offset_y = (size[1] - logo_h) // 2
        
        circle_img.paste(logo_img, (offset_x, offset_y), logo_img)
        draw.ellipse([0, 0, size[0]-1, size[1]-1], outline=(40, 40, 40, 255), width=4)
        
        imagebox = OffsetImage(circle_img, zoom=zoom * 0.45)  # Dostosowany delikatnie zoom pod mniejsze kółka
        ab = AnnotationBbox(
            imagebox,
            (x, y),
            frameon=False,
            pad=0,
            box_alignment=box_alignment,
            zorder=5
        )
        ax.add_artist(ab)
        return True

    except Exception as e:
        print(f"Błąd przetwarzania herbu w kółku dla {team_name}: {e}")
        return False