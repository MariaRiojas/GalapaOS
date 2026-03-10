"""GalapaOS FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from .api.routes_forecast import router as forecast_router
from .api.routes_stations import router as stations_router
from .api.routes_historical import router as historical_router
from .api.routes_model import router as model_router
from .config import FIGURES_DIR

app = FastAPI(
    title="GalapaOS API",
    version="1.0.0",
    description="Galapagos Operational Solar Nowcasting for Island Resilience",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(forecast_router)
app.include_router(stations_router)
app.include_router(historical_router)
app.include_router(model_router)

# Serve figures as static files
if FIGURES_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FIGURES_DIR)), name="static")


@app.get("/")
def root():
    return {
        "name": "GalapaOS",
        "version": "1.0.0",
        "description": "Galapagos Operational Solar Nowcasting",
        "status": "running",
    }
