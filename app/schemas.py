from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class SignalReadingBase(BaseModel):
    latitude: float
    longitude: float
    signal_strength: float
    operator: str
    country: Optional[str] = None

class SignalReadingCreate(SignalReadingBase):
    pass

class SignalReading(SignalReadingBase):
    id: int
    timestamp: datetime
    user_id: Optional[int] = None
    
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    points: int
    rank: str

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
