"""GET /api/stations -- current status of all 4 stations."""

from fastapi import APIRouter
from ..services.forecast_service import get_stations

router = APIRouter()


@router.get("/api/stations")
def stations():
    return get_stations()
