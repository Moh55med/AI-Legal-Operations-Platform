"""
Background job scheduler for deadline alerts.
Uses APScheduler to run periodic jobs.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.services.deadline_alerts import DeadlineAlertService
import logging
import sys

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler: BackgroundScheduler = None


def start_scheduler():
    """Initialize and start the background scheduler"""
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler already running")
        return
    
    try:
        scheduler = BackgroundScheduler()
        
        # Schedule daily alert job at 6 AM UTC
        scheduler.add_job(
            func=DeadlineAlertService.run_daily_alert_job,
            trigger=CronTrigger(hour=6, minute=0),
            id="daily_deadline_alerts",
            name="Daily Deadline Alerts",
            replace_existing=True,
        )
        
        # Schedule overdue check every 6 hours
        scheduler.add_job(
            func=DeadlineAlertService.mark_overdue_deadlines,
            trigger=CronTrigger(hour="*/6"),
            id="check_overdue_deadlines",
            name="Check Overdue Deadlines",
            replace_existing=True,
        )
        
        scheduler.start()
        logger.info("Background scheduler started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start scheduler: {str(e)}")
        raise


def stop_scheduler():
    """Stop the background scheduler"""
    global scheduler
    
    if scheduler is None:
        logger.warning("Scheduler not running")
        return
    
    try:
        scheduler.shutdown(wait=True)
        scheduler = None
        logger.info("Background scheduler stopped")
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")


def is_scheduler_running() -> bool:
    """Check if scheduler is currently running"""
    global scheduler
    return scheduler is not None and scheduler.running
