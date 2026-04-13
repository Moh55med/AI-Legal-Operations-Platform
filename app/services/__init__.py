"""
Background job service for deadline alerts.
Handles periodic checking and notification creation for upcoming deadlines.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import SessionLocal, engine
from app.db.models import Deadline, DeadlineStatusEnum, Watcher, Notification
from app.crud import notifications as notifications_crud
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DeadlineAlertService:
    """Service for managing deadline alerts and background jobs"""

    # Default: alert users 3 days before deadline
    DEFAULT_ALERT_DAYS = 3

    @staticmethod
    def check_and_create_alerts(alert_days: int = DEFAULT_ALERT_DAYS) -> dict:
        """
        Check for upcoming deadlines and create notifications for watching users.
        
        **Parameters:**
        - **alert_days**: Number of days before deadline to create alert (default: 3)
        
        **Returns:** Dictionary with alert statistics
        """
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            alert_threshold = now + timedelta(days=alert_days)
            
            # Find deadlines coming up within alert_days
            upcoming_deadlines = (
                db.query(Deadline)
                .filter(
                    Deadline.due_date >= now,
                    Deadline.due_date <= alert_threshold,
                    Deadline.status == DeadlineStatusEnum.PENDING,
                )
                .all()
            )
            
            notifications_created = 0
            skipped_notifications = 0
            
            for deadline in upcoming_deadlines:
                # Find all users watching this case
                watchers = (
                    db.query(Watcher)
                    .filter(Watcher.case_id == deadline.case_id)
                    .all()
                )
                
                for watcher in watchers:
                    # Check if notification already exists for this user and deadline
                    existing = (
                        db.query(Notification)
                        .filter(
                            Notification.user_id == watcher.user_id,
                            Notification.deadline_id == deadline.id,
                            Notification.status != "dismissed",
                        )
                        .first()
                    )
                    
                    if not existing:
                        # Create new notification
                        notifications_crud.create_notification(
                            db,
                            user_id=watcher.user_id,
                            deadline_id=deadline.id,
                            status="unread",
                        )
                        notifications_created += 1
                    else:
                        skipped_notifications += 1
            
            logger.info(
                f"Deadline alerts processed: "
                f"{notifications_created} created, {skipped_notifications} skipped"
            )
            
            return {
                "success": True,
                "upcoming_deadlines_count": len(upcoming_deadlines),
                "notifications_created": notifications_created,
                "notifications_skipped": skipped_notifications,
            }
        
        except Exception as e:
            logger.error(f"Error checking deadline alerts: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }
        
        finally:
            db.close()

    @staticmethod
    def mark_overdue_deadlines() -> dict:
        """
        Check for overdue deadlines and mark them as missed.
        
        **Returns:** Dictionary with operation statistics
        """
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            
            # Find overdue deadlines still marked as pending
            overdue_deadlines = (
                db.query(Deadline)
                .filter(
                    Deadline.due_date < now,
                    Deadline.status == DeadlineStatusEnum.PENDING,
                )
                .all()
            )
            
            marked_missed = 0
            
            for deadline in overdue_deadlines:
                deadline.status = DeadlineStatusEnum.MISSED
                marked_missed += 1
            
            db.commit()
            
            logger.info(f"Marked {marked_missed} deadlines as missed")
            
            return {
                "success": True,
                "deadlines_marked_missed": marked_missed,
            }
        
        except Exception as e:
            logger.error(f"Error marking overdue deadlines: {str(e)}")
            return {
                "success": False,
                "error": str(e),
            }
        
        finally:
            db.close()

    @staticmethod
    def run_daily_alert_job(alert_days: int = DEFAULT_ALERT_DAYS) -> dict:
        """
        Run the complete daily alert job.
        Checks for upcoming deadlines and marks overdue ones.
        
        **Parameters:**
        - **alert_days**: Number of days before deadline to create alert (default: 3)
        
        **Returns:** Dictionary with job statistics
        """
        logger.info(f"Running daily deadline alert job (alert_days={alert_days})")
        
        alerts_result = DeadlineAlertService.check_and_create_alerts(alert_days)
        overdue_result = DeadlineAlertService.mark_overdue_deadlines()
        
        combined_result = {
            "success": alerts_result.get("success") and overdue_result.get("success"),
            "alerts": alerts_result,
            "overdue": overdue_result,
        }
        
        logger.info(f"Daily job completed: {combined_result}")
        return combined_result
