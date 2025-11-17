from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import Base, engine, SessionLocal
from models import EvidenceLog
from utils import compute_hash

Base.metadata.create_all(bind=engine)

app = FastAPI(title="FAIoT Fog Node")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
class IoTData(BaseModel):
    device_id: str
    temperature: float
    humidity: float
    timestamp: str
    hash: str
    

@app.post("/receive")
def receive_data(data: IoTData, db: Session = Depends(get_db)):
    recalculated_hash = compute_hash(
        data.device_id, 
        data.temperature,
        data.humidity,
        data.timestamp
    )
    
    verified = (recalculated_hash == data.hash)
    
    if not verified:
        raise HTTPException(status_code=400, detail="Hash mismatch - possible tampering!")
    
    log_entry = EvidenceLog(
        device_id=data.device_id,
        temperature=data.temperature,
        humidity=data.humidity,
        timestamp=data.timestamp,
        hash=data.hash,
        verified=True
    )
    
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    
    return {
        "status": "success",
        "verified": verified,
        "id": log_entry.id
    }