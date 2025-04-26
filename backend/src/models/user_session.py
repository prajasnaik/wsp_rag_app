from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, BOOLEAN, DATETIME

from .base_model import Base
from sqlalchemy.sql import func

class UserSession(Base):
    __tablename__ = "user_session"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    refresh_token = Column(String, unique=True)
    revoked = Column(BOOLEAN, default=False)
    created_at = Column(DATETIME, default=func.now())
    expires_at = Column(DATETIME)
