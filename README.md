# GalapaOS

**Solar nowcasting for an island microgrid that cannot afford to guess.**

San Cristóbal Island, Galápagos, runs on an isolated microgrid. Solar generation there is
volatile: cloud cover moves fast, and a ramp the operator did not see coming has to be
absorbed by diesel backup. Every unforecast ramp costs fuel, money, and emissions — on an
archipelago whose entire point is not burning things.

GalapaOS forecasts short-horizon solar generation so operators can schedule around ramps
instead of reacting to them — using only the weather instruments the island already has.
No satellite imagery, no numerical weather models, no new sensors.

---

## Result

Six independent XGBoost models, one per forecast horizon (30 to 180 minutes), evaluated
against standard persistence and climatology baselines. Mean Absolute Error, in W/m²:

| Horizon | GalapaOS | Persistence | Climatology |
|---|---|---|---|
| +30 min | **34.57** | 44.70 | 80.85 |
| +60 min | **45.77** | 73.80 | 81.43 |
| +90 min | **50.21** | 99.12 | 82.82 |
| +120 min | **56.56** | 121.14 | 85.22 |
| +150 min | **58.23** | 139.07 | 88.99 |
| +180 min | **61.74** | 153.06 | 94.02 |

The framework beats both baselines at every horizon. It also degrades far more gracefully:
error grows 79% from the 30- to the 180-minute horizon, versus 242% for persistence.

Second place, SALA 2026 Hackathon (Quito, March 2026).

---

## How it works

- **Data:** ~10 years of 15-minute meteorological observations (Jun 2015–Mar 2026) from
  the El Junco station, San Cristóbal — a single existing weather station at ~700 m a.s.l.
- **Preprocessing:** resampled to 30-minute frequency; restricted to daylight hours;
  incomplete rows dropped rather than interpolated, to preserve physical integrity.
- **Features:** 49 engineered features embedding physical knowledge — cyclical time
  (sin/cos of hour and day), ramp mechanics (velocity, acceleration, rolling variance of
  irradiance), humidity-solar risk indices, wind vector decomposition, and lag memory.
- **Model:** six independent XGBoost regressors, one per horizon, each trained to predict
  the *ramp* (ΔG) rather than absolute irradiance — focusing learning on cloud dynamics.
  Pseudo-Huber loss for robustness to abrupt cloud-driven outliers.
- **Interpretability:** SHAP analysis confirms the models rely on physically coherent
  drivers (time-of-day and recent irradiance dominate). See `feature_importance.png`.

The design is deliberately hardware-efficient: it runs on the infrastructure a
resource-constrained microgrid already has, which is what makes it replicable elsewhere.

---

## Repository

```
pipeline/     data ingestion and feature engineering
dashboard/    operator-facing interface
notebooks/    model development and evaluation
```

## Reproduce

```bash
git clone https://github.com/MariaRiojas/GalapaOS
cd GalapaOS
pip install -r requirements.txt
```

Open the notebook at the repo root to run model development and evaluation end to end.

---

## Paper

*XGBoost-based Solar Forecasting for the Galápagos Islands.* In preparation.

## Team

Built by an 8-person international team during the SALA 2026 Hackathon.
Project lead: María Jesús Riojas Concha.
