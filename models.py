from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from database import Base
from datetime import datetime, timezone

class EvidenceLog(Base):
    __tablename__ = "evidence_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)
    timestamp = Column(String)
    hash = Column(String)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    