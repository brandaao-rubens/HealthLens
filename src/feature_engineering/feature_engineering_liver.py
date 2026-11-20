import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
INPUT_PATH = ROOT / "data" / "processed" / "liver_clean.csv"
OUTPUT_PATH = ROOT / "data" / "processed" / "liver_features.csv"

def engineer_features():
    print("⚙️ Feature Engineering LIVER...")
    df = pd.read_csv(INPUT_PATH)
    
    # 1. Relação TGO/TGP (Razão de Ritis)
    # Importante marcador: >1 indica cirrose/alcoolismo, <1 esteatose
    df['ast_alt_ratio'] = df['sgot'] / (df['sgpt'] + 0.1)
    
    # 2. Globulinas (Proteínas - Albumina)
    df['globulin'] = df['proteins'] - df['albumin']
    
    # 3. Bilirrubina Indireta (Total - Direta)
    df['bilirubin_indirect'] = df['bilirubin_total'] - df['bilirubin_direct']
    
    df.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ Features salvas em: {OUTPUT_PATH}")

if __name__ == "__main__":
    engineer_features()