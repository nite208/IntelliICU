"""
Dashboard API
"""

from fastapi import APIRouter

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("/")
def get_dashboard():

    return {
        "total_patients": 48,
        "critical_patients": 12,
        "bed_occupancy": 85.7,
        "active_alerts": 7,
        "available_beds": 8,
        "icu_capacity": 56,
    }