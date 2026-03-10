"""Cross-station alert detection logic (Layer 3)."""


def detect_cross_station_alerts(current_data: dict) -> list:
    """Detect alerts based on cross-station patterns.

    Args:
        current_data: dict with current station readings
            e.g. {'mira_kt_ramp_15m': -0.4, 'mira_dewpoint_depression': 1.5, ...}

    Returns:
        List of alert dicts with station, event, eta, confidence.
    """
    alerts = []

    # Solar ramp detected at coastal station
    if current_data.get("mira_kt_ramp_15m", 0) < -0.3:
        alerts.append({
            "station": "El Mirador (costa)",
            "event": "Caida de radiacion solar detectada",
            "detected_at": current_data.get("timestamp", ""),
            "eta_target_min": 45,
            "confidence": 0.78,
        })

    # Saturating air at coast (fog/low cloud incoming)
    if current_data.get("mira_dewpoint_depression", 10) < 2.0:
        alerts.append({
            "station": "El Mirador (costa)",
            "event": "Aire saturandose (dewpoint depression < 2C)",
            "detected_at": current_data.get("timestamp", ""),
            "eta_target_min": 60,
            "confidence": 0.65,
        })

    # Solar ramp at mid-elevation (closer to target)
    if current_data.get("merc_kt_ramp_15m", 0) < -0.3:
        alerts.append({
            "station": "Merceditas (media)",
            "event": "Caida de radiacion solar detectada",
            "detected_at": current_data.get("timestamp", ""),
            "eta_target_min": 28,
            "confidence": 0.82,
        })

    # High wind at summit
    if current_data.get("jun_wind_speed_ms", 0) > 10:
        alerts.append({
            "station": "El Junco (cumbre)",
            "event": "Viento fuerte (>10 m/s)",
            "detected_at": current_data.get("timestamp", ""),
            "eta_target_min": 0,
            "confidence": 0.90,
        })

    return alerts
