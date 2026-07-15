# GalapaOS

**Solar nowcasting for an island microgrid that cannot afford to guess.**

San Cristóbal Island, Galápagos, runs on an isolated microgrid. Solar generation there is
volatile: cloud cover moves fast, and a ramp the operator did not see coming has to be
absorbed by diesel backup. Every unforecast ramp costs fuel, money, and emissions — on an
archipelago whose entire point is not burning things.

GalapaOS forecasts short-horizon solar generation so operators can schedule around ramps
instead of reacting to them.

---

## Result

| | Forecast error |
|---|---|
| Baseline | ~40% |
| GalapaOS | **~17%** |

METRIC USED (nRMSE / MAPE / other) AND FORECAST HORIZON — FILL IN
Second place, SALA 2026 Hackathon (Quito, March 2026).

---

## How it works

DESCRIBE THE PIPELINE IN 3–5 BULLETS: DATA SOURCES, FEATURES, MODEL, HORIZON, HOW IT IS SERVED.
KEEP IT HONEST — NAME THE MODEL YOU ACTUALLY USED.

- **Data:** WHICH SOURCES
- **Features:** WHICH ONES MATTERED (see `feature_importance.png`)
- **Model:** WHICH MODEL
- **Horizon:** HOW FAR AHEAD
- **Output:** dashboard for grid operators

---

## Repository

```
pipeline/       data ingestion and feature engineering
dashboard/      operator-facing interface
notebooks/      model development and evaluation
```

## Reproduce

```bash
git clone https://github.com/MariaRiojas/GalapaOS
cd GalapaOS
pip install -r requirements.txt
```

DATA ACCESS: SAY WHERE THE DATA COMES FROM AND WHETHER IT IS REDISTRIBUTABLE.
IF IT IS NOT, SHIP A SMALL SAMPLE SO THE NOTEBOOK RUNS END TO END.

---

## Paper

A technical paper is in preparation. LINK IT WHEN AVAILABLE.

## Team

Built by an 8-person international team. LIST THEM — CREDIT IS FREE AND IT MATTERS.
Technical lead: María Jesús Riojas Concha.

## License

CHOOSE ONE — MIT OR APACHE-2.0. A REPO WITHOUT A LICENSE IS LEGALLY UNUSABLE BY ANYONE ELSE.
