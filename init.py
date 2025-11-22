from pathlib import Path

from app.database import SessionLocal
from app.importer import (
    import_ind_atmo_csv,
    import_fr_e2_csv,
)


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


def main():
    # Ouverture d'une session DB
    db = SessionLocal()

    try:
    
        ind_atmo_path = DATA_DIR / "ind_atmo_2021.csv"
        if ind_atmo_path.exists():
            print(f"[INIT] Import du fichier : {ind_atmo_path}")
            with ind_atmo_path.open("r", encoding="utf-8") as f:
                result = import_ind_atmo_csv(db, f)
            print(f"[INIT] ind_atmo_2021 → {result['inserted']} lignes insérées, {len(result['errors'])} erreurs")
        else:
            print(f"[INIT] Fichier ind_atmo_2021.csv introuvable dans {DATA_DIR}")

        fr_e2_path = DATA_DIR / "FR_E2_2025-01-01.csv"
        if fr_e2_path.exists():
            print(f"[INIT] Import du fichier : {fr_e2_path}")
            with fr_e2_path.open("r", encoding="utf-8") as f:
                result = import_fr_e2_csv(db, f)
            print(f"[INIT] FR_E2_2025-01-01 → {result['inserted']} lignes insérées, {len(result['errors'])} erreurs")
        else:
            print(f"[INIT] Fichier FR_E2_2025-01-01.csv introuvable dans {DATA_DIR}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
