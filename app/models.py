from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    points = Column(Integer, default=0)
    rank = Column(String, default="Beginner")
    
    readings = relationship("SignalReading", back_populates="user")

class SignalReading(Base):
    __tablename__ = "signal_readings"
    
    # Standard columns
    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    signal_strength = Column(Float, nullable=False)
    operator = Column(String, nullable=False)
    country = Column(String, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Geospatial column
    geom = Column(Geometry('POINT', srid=4326))
    
    user = relationship("User", back_populates="readings")
