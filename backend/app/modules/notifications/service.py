from app.core.database import SessionLocal
from app.models.notification import Notification

class NotificationService:
    @staticmethod
    def create_notification(message: str, type: str = "INFO"):
        db = SessionLocal()
        try:
            db_notif = Notification(message=message, type=type)
            db.add(db_notif)
            db.commit()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Failed to create notification: {e}")
        finally:
            db.close()
