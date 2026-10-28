from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, NotificationCreate
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), limit: int = 50):
    return db.query(Notification).order_by(Notification.timestamp.desc()).limit(limit).all()

@router.post("/", response_model=NotificationResponse)
def create_notification(notif: NotificationCreate, db: Session = Depends(get_db)):
    db_notif = Notification(message=notif.message, type=notif.type, read=notif.read)
    db.add(db_notif)
    db.commit()
    db.refresh(db_notif)
    return db_notif

@router.put("/{notif_id}/read", response_model=NotificationResponse)
def mark_as_read(notif_id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == notif_id).first()
    if notif:
        notif.read = True
        db.commit()
        db.refresh(notif)
    return notif

@router.put("/read-all")
def mark_all_as_read(db: Session = Depends(get_db)):
    db.query(Notification).filter(Notification.read == False).update({"read": True})
    db.commit()
    return {"message": "All notifications marked as read"}
