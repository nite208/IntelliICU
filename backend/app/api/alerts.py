"""
Enterprise Alert API
"""

from fastapi import APIRouter, HTTPException

from app.alerts.manager import manager as alert_manager

router = APIRouter(
    prefix="/alerts",
    tags=["Alerts"],
)


@router.get("/")
async def get_alerts():
    """
    Get all active alerts.
    """

    return [
        alert.model_dump(mode="json")
        for alert in alert_manager.active_alerts()
    ]


@router.post("/acknowledge/{alert_id}")
async def acknowledge(alert_id: str):
    """
    Acknowledge an alert.
    """

    alert = next(
        (
            item
            for item in alert_manager.active_alerts()
            if item.id == alert_id
        ),
        None,
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    alert_manager.acknowledge(alert_id)

    return {
        "success": True,
        "message": "Alert acknowledged.",
        "alert_id": alert_id,
    }


@router.post("/resolve/{alert_id}")
async def resolve(alert_id: str):
    """
    Resolve an alert.
    """

    alert = next(
        (
            item
            for item in alert_manager.active_alerts()
            if item.id == alert_id
        ),
        None,
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    alert_manager.resolve(alert_id)

    return {
        "success": True,
        "message": "Alert resolved.",
        "alert_id": alert_id,
    }


@router.post("/escalate/{alert_id}")
async def escalate(alert_id: str):
    """
    Escalate an alert.
    """

    alert = next(
        (
            item
            for item in alert_manager.active_alerts()
            if item.id == alert_id
        ),
        None,
    )

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    alert_manager.escalate(alert_id)

    return {
        "success": True,
        "message": "Alert escalated.",
        "alert_id": alert_id,
    }