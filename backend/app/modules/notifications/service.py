import logging
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta, timezone
from app.core.database import SessionLocal
from app.models.notification import Notification
from app.core.config import settings

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    def create_notification(message: str, type: str = "INFO", deduplicate_seconds: int = 30) -> bool:
        """
        Creates an audit notification in the database with duplicate suppression
        and optionally dispatches to configured external notification providers (e.g. SMTP).
        """
        db = SessionLocal()
        try:
            # Duplicate notification protection: skip if identical message created within window
            cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(seconds=deduplicate_seconds)
            duplicate = db.query(Notification).filter(
                Notification.message == message,
                Notification.type == type,
                Notification.timestamp >= cutoff
            ).first()

            if duplicate:
                logger.info(f"Suppressed duplicate notification: {message}")
                return True

            db_notif = Notification(message=message, type=type)
            db.add(db_notif)
            db.commit()
            logger.info(f"Recorded in-app notification [{type}]: {message}")

            # Dispatch external notification if SMTP credentials are provided
            if settings.SMTP_SERVER and settings.NOTIFICATION_EMAIL_TO:
                NotificationService._send_email_notification(message, type)

            return True
        except Exception as e:
            logger.error(f"Failed to create notification: {e}")
            return False
        finally:
            db.close()

    @staticmethod
    def _send_email_notification(message: str, type: str, max_retries: int = 2):
        """Dispatches an email notification with retries when configured."""
        sender = settings.NOTIFICATION_EMAIL_FROM or settings.SMTP_USER or "alerts@cloudchange.local"
        recipient = settings.NOTIFICATION_EMAIL_TO

        msg = MIMEText(message)
        msg["Subject"] = f"[CloudChange {type}] Deployment Notification"
        msg["From"] = sender
        msg["To"] = recipient

        for attempt in range(1, max_retries + 1):
            try:
                with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=5) as server:
                    if settings.SMTP_USER and settings.SMTP_PASSWORD:
                        server.starttls()
                        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                    server.send_message(msg)
                logger.info(f"Successfully sent email notification to {recipient} on attempt {attempt}")
                return True
            except Exception as e:
                logger.warning(f"SMTP notification attempt {attempt}/{max_retries} failed: {e}")
        return False
