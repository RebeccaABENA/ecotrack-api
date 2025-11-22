import csv
import logging
from datetime import datetime
from typing import IO, List, Dict, Any, Optional

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from .models import Indicator, Zone, Source

# Configuration basique du logging pour voir les erreurs dans la console
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_timestamp(raw: str) -> datetime:
    """
    Tente de parser une date/heure selon plusieurs formats courants.
    """
    if not raw:
        raise ValueError("Timestamp vide")

    raw = raw.strip()
    
    # 1. Essai ISO format (le plus rapide)
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        pass

    # 2. Liste de formats à tester (du plus précis au plus général)
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y/%m/%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",  # Format FR avec secondes
        "%d-%m-%Y %H:%M:%S",
        "%d/%m/%Y %H:%M",     # Format FR sans secondes
        "%d-%m-%Y %H:%M",
        "%Y-%m-%d",
        "%d/%m/%Y",           # Format FR date seule
        "%d-%m-%Y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

    raise ValueError(f"Format de date inconnu : {raw!r}")

def clean_float(value: Any) -> float:
    """
    Convertit une valeur en float en gérant la virgule et le point.
    Renvoie 0.0 si vide ou None.
    """
    if value is None:
        return 0.0
    
    s_val = str(value).strip()
    if not s_val:
        return 0.0
    
    # Remplacement virgule par point pour Python
    s_val = s_val.replace(",", ".")
    
    try:
        return float(s_val)
    except ValueError:
        raise ValueError(f"Valeur numérique invalide : {value}")

def normalize_csv_headers(fieldnames: List[str]) -> List[str]:
    """
    Nettoie les en-têtes CSV : enlève le BOM (\ufeff) et les espaces.
    """
    if not fieldnames:
        return []
    return [name.lstrip('\ufeff').strip() for name in fieldnames]

# --- FONCTIONS DB ---

def get_or_create_zone(db: Session, name: str) -> Zone:
    name = name.strip()
    zone = db.query(Zone).filter(Zone.name == name).first()
    if zone:
        return zone
    zone = Zone(name=name, postal_code=None)
    db.add(zone)
    # On utilise flush() pour avoir l'ID sans commiter définitivement la transaction globale
    db.flush() 
    db.refresh(zone)
    return zone

def get_or_create_source(
    db: Session,
    name: str,
    description: Optional[str] = "",
    url: Optional[str] = "",
) -> Source:
    name = name.strip()
    source = db.query(Source).filter(Source.name == name).first()
    if source:
        return source
    source = Source(name=name, description=description or "", url=url or "")
    db.add(source)
    db.flush()
    db.refresh(source)
    return source

# --- IMPORT GENERIC ---

def import_indicators_from_csv(
    db: Session,
    file_obj: IO[str],
) -> Dict[str, Any]:
    
    # Lecture initiale pour nettoyer les headers
    reader = csv.DictReader(file_obj, delimiter=",") # Par défaut virgule
    
    # Normalisation des headers (hack pour modifier le fieldnames du reader à la volée)
    if reader.fieldnames:
        reader.fieldnames = normalize_csv_headers(reader.fieldnames)

    required_cols = {"source_name", "zone_name", "type", "value", "unit", "timestamp"}
    missing = required_cols - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Colonnes manquantes (CSV Générique) : {missing}")

    inserted = 0
    errors: List[Dict[str, Any]] = []

    for idx, row in enumerate(reader, start=2):
        try:
            # Extraction et nettoyage
            source_name = row.get("source_name", "").strip()
            zone_name = row.get("zone_name", "").strip()
            type_ = row.get("type", "").strip()
            
            # Validations
            if not source_name: raise ValueError("source_name vide")
            if not zone_name: raise ValueError("zone_name vide")
            if not type_: raise ValueError("type vide")

            # Conversions
            value = clean_float(row.get("value"))
            ts = parse_timestamp(row.get("timestamp"))
            unit = row.get("unit", "").strip()
            metadata = row.get("metadata", None)

            # Logique DB
            source = get_or_create_source(db, source_name)
            zone = get_or_create_zone(db, zone_name)

            indicator = Indicator(
                source_id=source.id,
                zone_id=zone.id,
                type=type_,
                value=value,
                unit=unit,
                timestamp=ts,
                extra_metadata=metadata,
            )
            db.add(indicator)
            inserted += 1

        except Exception as e:
            # On capture l'erreur mais on continue le fichier
            errors.append({"line": idx, "error": str(e), "row": row})

    # Commit final de toutes les lignes valides
    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Erreur base de données lors du commit : {str(e)}")

    return {"inserted": inserted, "errors": errors}

# --- IMPORT FR_E2 ---

def import_fr_e2_dataset(
    db: Session,
    file_obj: IO[str],
) -> Dict[str, Any]:
    
    # Attention : le fichier FR_E2 utilise souvent le point-virgule
    reader = csv.DictReader(file_obj, delimiter=";")
    
    if reader.fieldnames:
        reader.fieldnames = normalize_csv_headers(reader.fieldnames)

    required_cols = {
        "Date de début", "Organisme", "Zas", 
        "Polluant", "valeur", "unité de mesure"
    }
    missing = required_cols - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Colonnes manquantes (FR_E2) : {missing}")

    inserted = 0
    errors: List[Dict[str, Any]] = []

    for idx, row in enumerate(reader, start=2):
        try:
            ts = parse_timestamp(row.get("Date de début"))
            
            source_name = (row.get("Organisme") or "").strip()
            zone_name = (row.get("Zas") or "").strip()
            type_ = (row.get("Polluant") or "").strip()

            if not source_name or not zone_name:
                raise ValueError("Organisme ou Zas vide")
            if not type_:
                raise ValueError("Polluant vide")

            # Utilisation de clean_float pour gérer la virgule française
            value = clean_float(row.get("valeur"))
            
            unit = (row.get("unité de mesure") or "").strip() or "µg/m³"

            # Métadonnées
            nom_site = row.get("nom site", "")
            type_implant = row.get("type d'implantation", "")
            type_influence = row.get("type d'influence", "")
            metadata = (
                f"nom_site={nom_site}; type_implantation={type_implant}; "
                f"type_influence={type_influence}"
            )

            source = get_or_create_source(
                db,
                name=source_name,
                description=f"Mesures horaires {source_name}",
            )
            zone = get_or_create_zone(db, zone_name)

            indicator = Indicator(
                source_id=source.id,
                zone_id=zone.id,
                type=type_,
                value=value,
                unit=unit,
                timestamp=ts,
                extra_metadata=metadata,
            )
            db.add(indicator)
            inserted += 1

        except Exception as e:
            errors.append({"line": idx, "error": str(e)})

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Erreur DB (FR_E2) : {str(e)}")

    return {"inserted": inserted, "errors": errors}

# --- IMPORT IND_ATMO ---

def import_ind_atmo_dataset(
    db: Session,
    file_obj: IO[str],
) -> Dict[str, Any]:
    
    # Fichier souvent en virgule
    reader = csv.DictReader(file_obj, delimiter=",")
    
    if reader.fieldnames:
        reader.fieldnames = normalize_csv_headers(reader.fieldnames)

    required_cols = {"lib_zone", "source", "date_ech", "code_qual", "lib_qual"}
    missing = required_cols - set(reader.fieldnames or [])
    if missing:
        raise ValueError(f"Colonnes manquantes (ind_atmo) : {missing}")

    inserted = 0
    errors: List[Dict[str, Any]] = []

    for idx, row in enumerate(reader, start=2):
        try:
            zone_name = (row.get("lib_zone") or "").strip()
            source_name = (row.get("source") or "").strip()
            date_ech_raw = (row.get("date_ech") or "").strip()

            if not zone_name or not source_name:
                raise ValueError("Zone ou Source vide")
            
            ts_date = parse_timestamp(date_ech_raw)
            
            # Type fixe pour ce dataset
            type_ = "atmo_index"
            
            value = clean_float(row.get("code_qual"))
            unit = "index"

            # Métadonnées dynamiques
            lib_qual = row.get("lib_qual", "")
            # On récupère les codes optionnels s'ils existent
            codes = {
                k: row.get(k, "") 
                for k in ["code_no2", "code_o3", "code_pm10", "code_pm25", "code_so2"]
                if row.get(k)
            }
            
            metadata_parts = [f"lib_qual={lib_qual}"]
            metadata_parts.extend([f"{k}={v}" for k, v in codes.items()])
            metadata = "; ".join(metadata_parts)

            source = get_or_create_source(
                db,
                name=source_name,
                description="Indice ATMO par commune",
            )
            zone = get_or_create_zone(db, zone_name)

            indicator = Indicator(
                source_id=source.id,
                zone_id=zone.id,
                type=type_,
                value=value,
                unit=unit,
                timestamp=ts_date,
                extra_metadata=metadata,
            )
            db.add(indicator)
            inserted += 1

        except Exception as e:
            errors.append({"line": idx, "error": str(e)})

    try:
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise ValueError(f"Erreur DB (Ind Atmo) : {str(e)}")

    return {"inserted": inserted, "errors": errors}