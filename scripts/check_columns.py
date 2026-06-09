import pandas as pd
from pathlib import Path

# Ścieżka do Twojego pliku
path = Path("data/dfs/stats_full.csv")
df = pd.read_csv(path)
print("Dostępne kolumny w stats_full.csv:")
print(df.columns.tolist())