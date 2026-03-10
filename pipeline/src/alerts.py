"""Cross-station alert detection logic."""

from .config import KT_RAMP_THRESHOLD


def detect_alerts(current_data: dict, lags_json: dict = None) -> list:
    """Detect alerts based on cross-station patterns.

    Args:
        current_data: dict with current station readings
        lags_json: dict from cross_station_lags.json

    Returns:
        List of alert dicts.
    """
    if lags_json is None:
        lags_json = {}
    alerts = []

    # Solar ramp at coastal station
    if current_data.get("mira_kt_ramp_15m", 0) < KT_RAMP_THRESHOLD:
        lag = lags_json.get("mira_to_jun", {}).get("lag_min", 45)
        alerts.append({
            "station": "El Mirador (costa)",
            "event": "Solar radiation drop detected",
            "eta_min": lag,
            "confidence": 0.78,
            "severity": "warning",
        })

    # Thermal inversion at summit
    if current_data.get("jun_temp_lapse_deviation", 0) > 1.5:
        alerts.append({
            "station": "El Junco (summit)",
            "event": "Thermal inversion -- garua likely",
            "eta_min": 0,
            "confidence": 0.65,
            "severity": "info",
        })

    # Humidity gradient rising
    if current_data.get("rh_gradient_coast_summit", 0) > 20:
        alerts.append({
            "station": "Transect",
            "event": "Humidity gradient rising -- clouds forming",
            "eta_min": 30,
            "confidence": 0.60,
            "severity": "info",
        })

    # Solar ramp at mid-elevation
    if current_data.get("merc_kt_ramp_15m", 0) < KT_RAMP_THRESHOLD:
        lag = lags_json.get("merc_to_jun", {}).get("lag_min", 28)
        alerts.append({
            "station": "Merceditas (mid)",
            "event": "Solar radiation drop detected",
            "eta_min": lag,
            "confidence": 0.82,
            "severity": "warning",
        })

    return alerts
