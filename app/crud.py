from typing import Optional
from sqlalchemy.orm import Session
from . import schemas
from .models import User,Zone, Source, Indicator
from datetime import datetime
from sqlalchemy import func

def get_user_by_email(db: Session, email: str) -> Optional[User]:
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user_in: schemas.UserCreate, hashed_password: str) -> User:
    user = User(
        email=user_in.email,
        password=hashed_password,
        role=user_in.role or "user",
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
def create_zone(db: Session, zone_in: schemas.ZoneCreate) -> Zone:
    zone = Zone(
        name=zone_in.name,
        postal_code=zone_in.postal_code,
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


def get_zone(db: Session, zone_id: int) -> Optional[Zone]:
    return db.query(Zone).filter(Zone.id == zone_id).first()


def list_zones(db: Session) -> list[Zone]:
    return db.query(Zone).all()


def create_source(db: Session, source_in: schemas.SourceCreate) -> Source:
    source = Source(
        name=source_in.name,
        description=source_in.description,
        url=source_in.url,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return source


def get_source(db: Session, source_id: int) -> Optional[Source]:
    return db.query(Source).filter(Source.id == source_id).first()


def list_sources(db: Session) -> list[Source]:
    return db.query(Source).all()

def create_indicator(db: Session, indicator_in: schemas.IndicatorCreate) -> Indicator:
    indicator = Indicator(
        source_id=indicator_in.source_id,
        zone_id=indicator_in.zone_id,
        type=indicator_in.type,
        value=indicator_in.value,
        unit=indicator_in.unit,
        timestamp=indicator_in.timestamp,
        extra_metadata=indicator_in.metadata,
    )
    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


def get_indicator(db: Session, indicator_id: int) -> Optional[Indicator]:
    return db.query(Indicator).filter(Indicator.id == indicator_id).first()


def list_indicators(
    db: Session,
    type: Optional[str] = None,
    zone_id: Optional[int] = None,
    source_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Indicator]:
    query = db.query(Indicator)

    if type:
        query = query.filter(Indicator.type == type)
    if zone_id:
        query = query.filter(Indicator.zone_id == zone_id)
    if source_id:
        query = query.filter(Indicator.source_id == source_id)
    if date_from:
        query = query.filter(Indicator.timestamp >= date_from)
    if date_to:
        query = query.filter(Indicator.timestamp <= date_to)

    return query.offset(skip).limit(limit).all()

def indicator_stats(
    db: Session,
    type: Optional[str] = None,
    zone_id: Optional[int] = None,
    source_id: Optional[int] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
):
    """
    Retourne des stats agrégées sur les indicateurs :
    - count, min(value), max(value), avg(value)
    avec les mêmes filtres que list_indicators.
    """
    query = db.query(
        func.count(Indicator.id),
        func.min(Indicator.value),
        func.max(Indicator.value),
        func.avg(Indicator.value),
    )

    if type:
        query = query.filter(Indicator.type == type)
    if zone_id:
        query = query.filter(Indicator.zone_id == zone_id)
    if source_id:
        query = query.filter(Indicator.source_id == source_id)
    if date_from:
        query = query.filter(Indicator.timestamp >= date_from)
    if date_to:
        query = query.filter(Indicator.timestamp <= date_to)

    count, min_value, max_value, avg_value = query.one()

    # On renvoie un dict compatible avec IndicatorStats
    return {
        "count": count or 0,
        "min_value": min_value,
        "max_value": max_value,
        "avg_value": avg_value,
    }
    
def update_indicator(
    db: Session,
    indicator: Indicator,
    indicator_in: schemas.IndicatorUpdate,
) -> Indicator:
    """
    Met à jour seulement les champs fournis dans indicator_in.
    """
    data = indicator_in.model_dump(exclude_unset=True)

    for field, value in data.items():
        if hasattr(indicator, field):
            setattr(indicator, field, value)

    db.add(indicator)
    db.commit()
    db.refresh(indicator)
    return indicator


def delete_indicator(db: Session, indicator: Indicator) -> None:
    db.delete(indicator)
    db.commit()

