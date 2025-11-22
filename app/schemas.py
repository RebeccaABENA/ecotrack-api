from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    email: str
    role: str = "user"
    is_active: bool = True


class UserCreate(BaseModel):
    email: str
    password: str = Field(..., min_length=6)
    role: str = "user"

class UserRead(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
class ZoneBase(BaseModel):
    name: str
    postal_code: Optional[str] = None


class ZoneCreate(ZoneBase):
    pass


class ZoneRead(ZoneBase):
    id: int

    class Config:
        orm_mode = True


class SourceBase(BaseModel):
    name: str
    description: Optional[str] = None
    url: Optional[str] = None


class SourceCreate(SourceBase):
    pass


class SourceRead(SourceBase):
    id: int

    class Config:
        orm_mode = True



class IndicatorBase(BaseModel):
    source_id: int
    zone_id: int
    type: str
    value: float
    unit: str
    timestamp: datetime
    extra_metadata: Optional[str] = None


class IndicatorCreate(IndicatorBase):
    pass

class IndicatorUpdate(BaseModel):
    source_id: Optional[int] = Field(None, ge=1)
    zone_id: Optional[int] = Field(None, ge=1)
    type: Optional[str] = Field(None, min_length=1, max_length=100)
    value: Optional[float] = None
    unit: Optional[str] = None
    timestamp: Optional[datetime] = None
    extra_metadata: Optional[str] = None

    class Config:
        from_attributes = True

class IndicatorRead(IndicatorBase):
    id: int

    class Config:
        orm_mode = True
        
class IndicatorStats(BaseModel):
    count: int
    min_value: float | None
    max_value: float | None
    avg_value: float | None