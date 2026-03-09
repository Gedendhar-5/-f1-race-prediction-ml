# F1 Race Prediction ML Model

A machine learning model that predicts Formula 1 race outcomes using real-time data fetched automatically before each Grand Prix.

---

## What It Does

- Predicts the podium and full top 10 finishing order for any upcoming F1 race
- Auto-fetches qualifying results, live weather, and driver form — no manual input needed
- Enforces a 12-hour prediction window before race start
- Generates a visual dashboard saved as a PNG file

---

## How To Run

```bash
pip install -r requirements.txt
python predictor.py
```

You will see a list of all 25 races. Type the short code (e.g. `CHN`) or round number (e.g. `2`) and the model does the rest.

---

## Features

**ML Model**
Gradient Boosting Regressor trained on historical F1 data. Predicts race finishing time per driver and ranks them to produce the final order.

**Auto Qualifying Fetch**
After Saturday qualifying, real lap times are pulled from the Ergast F1 API automatically. Before qualifying, the model uses projected times based on team performance.

**Live Weather**
Fetches real-time temperature, rain probability, wind speed, humidity, and track temperature at the circuit from Open-Meteo API.

**Driver Form Module**
Pulls the last 5 race finishing positions for every driver from Ergast after each completed round. Updates automatically every race weekend — no code changes needed.

**Tyre Strategy Simulator**
Simulates Soft, Medium, and Hard compound strategies across the full race distance and recommends the optimal pit stop plan.

**12-Hour Rule**
Predictions are only available more than 12 hours before race start. Once the window closes, the model blocks the prediction and tells you why.

**Gulf & Middle East Safety Status**
Displays a safety status flag for races in Bahrain, Saudi Arabia, Qatar, Abu Dhabi, and Azerbaijan.

---

## How Accuracy Improves Each Weekend

| When You Run It | Data Available | Accuracy |
|---|---|---|
| Before qualifying (Friday) | Projected times | ~60-70% |
| After qualifying (Saturday) | Real quali times | ~85%+ |

---

## 2026 Race Calendar

25 races from Australia (March) to Abu Dhabi (December). Gulf races marked with 🛡️.

---
## Sample Output
![Australian GP Prediction](f1_prediction_AUS_2026.png)

## Requirements

```
pandas
numpy
scikit-learn
matplotlib
requests
xgboost
```

---

## License
## License
MIT
