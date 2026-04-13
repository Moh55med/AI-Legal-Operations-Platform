"""
FastAPI endpoints for user notifications.
Handles viewing and managing deadline alerts.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.crud import notifications as notifications_crud
from app.schemas import NotificationResponse

router = APIRouter()


@router.get("/user/{user_id}", response_model=List[NotificationResponse])
def get_user_notifications(
    user_id: int,
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Get notifications for a specific user.
    
    **Parameters:**
    - **user_id**: User ID (required)
    - **status**: Filter by status - 'unread', 'read', 'dismissed' (optional)
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Number of records to return (default: 100)
    
    **Returns:** List of notifications
    """
    notifications = notifications_crud.get_user_notifications(
        db, user_id, status=status, skip=skip, limit=limit
    )
    return notifications


@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_notification_read(notification_id: int, db: Session = Depends(get_db)):
    """
    Mark a notification as read.
    
    **Parameters:**
    - **notification_id**: Notification ID (required)
    
    **Returns:** Updated notification object
    """
    db_notification = notifications_crud.mark_notification_read(db, notification_id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    return db_notification


@router.put("/{notification_id}/dismiss", response_model=NotificationResponse)
def dismiss_notification(notification_id: int, db: Session = Depends(get_db)):
    """
    Dismiss a notification.
    
    **Parameters:**
    - **notification_id**: Notification ID (required)
    
    **Returns:** Updated notification object
    """
    db_notification = notifications_crud.mark_notification_dismissed(db, notification_id)
    if not db_notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
    return db_notification


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(notification_id: int, db: Session = Depends(get_db)):
    """
    Delete a notification.
    
    **Parameters:**
    - **notification_id**: Notification ID (required)
    
    **Returns:** No content
    """
    success = notifications_crud.delete_notification(db, notification_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Notification with ID {notification_id} not found"
        )
