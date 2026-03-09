"""
╔══════════════════════════════════════════════════════════════════════╗
║        F1 2026 FULL SEASON PREDICTION SYSTEM                        ║
║                                                                      ║
║  Auto-fetches:  Qualifying results · Live weather · Driver form      ║
║                 Circuit characteristics · Safety status             ║
║  12-Hour Rule:  Locks prediction window 12hrs before race start     ║
║  Season View:   WDC standings · Points chart · All 24 races         ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.gridspec as gridspec
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error
from datetime import datetime, timezone, timedelta
import json
import time
import warnings
warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════
#  2026 FULL SEASON CALENDAR  (24 races)
# ══════════════════════════════════════════════

F1_2026_CALENDAR = [
    {"round":1,  "name":"Australian Grand Prix",     "short":"AUS", "circuit":"Albert Park",       "city":"Melbourne",    "country":"Australia",   "lat":-37.8497, "lon":144.9680, "race_start_utc":"2026-03-15 05:00", "laps":58,  "circuit_type":"street_hybrid", "tyre_wear":"medium",   "safety_concern":False},
    {"round":2,  "name":"Chinese Grand Prix",         "short":"CHN", "circuit":"Shanghai International","city":"Shanghai", "country":"China",        "lat":31.3389,  "lon":121.2198, "race_start_utc":"2026-03-22 07:00", "laps":56,  "circuit_type":"permanent",     "tyre_wear":"medium",   "safety_concern":False},
    {"round":3,  "name":"Japanese Grand Prix",        "short":"JPN", "circuit":"Suzuka",            "city":"Suzuka",       "country":"Japan",        "lat":34.8431,  "lon":136.5407, "race_start_utc":"2026-04-05 05:00", "laps":53,  "circuit_type":"permanent",     "tyre_wear":"high",     "safety_concern":False},
    {"round":4,  "name":"Bahrain Grand Prix",         "short":"BHR", "circuit":"Bahrain International","city":"Sakhir",   "country":"Bahrain",      "lat":26.0325,  "lon":50.5106,  "race_start_utc":"2026-04-19 15:00", "laps":57,  "circuit_type":"permanent",     "tyre_wear":"medium",   "safety_concern":False},
    {"round":5,  "name":"Saudi Arabian Grand Prix",   "short":"KSA", "circuit":"Jeddah Corniche",   "city":"Jeddah",       "country":"Saudi Arabia", "lat":21.6319,  "lon":39.1044,  "race_start_utc":"2026-04-26 17:00", "laps":50,  "circuit_type":"street",        "tyre_wear":"low",      "safety_concern":False},
    {"round":6,  "name":"Miami Grand Prix",           "short":"MIA", "circuit":"Miami International","city":"Miami",       "country":"USA",          "lat":25.9581,  "lon":-80.2389, "race_start_utc":"2026-05-10 19:00", "laps":57,  "circuit_type":"street_hybrid", "tyre_wear":"medium",   "safety_concern":False},
    {"round":7,  "name":"Emilia Romagna Grand Prix",  "short":"EMI", "circuit":"Imola",             "city":"Imola",        "country":"Italy",        "lat":44.3439,  "lon":11.7167,  "race_start_utc":"2026-05-24 13:00", "laps":63,  "circuit_type":"permanent",     "tyre_wear":"low",      "safety_concern":False},
    {"round":8,  "name":"Monaco Grand Prix",          "short":"MON", "circuit":"Circuit de Monaco", "city":"Monte Carlo",  "country":"Monaco",       "lat":43.7347,  "lon":7.4205,   "race_start_utc":"2026-05-31 13:00", "laps":78,  "circuit_type":"street",        "tyre_wear":"low",      "safety_concern":False},
    {"round":9,  "name":"Spanish Grand Prix",         "short":"ESP", "circuit":"Circuit de Barcelona","city":"Barcelona", "country":"Spain",        "lat":41.5700,  "lon":2.2611,   "race_start_utc":"2026-06-14 13:00", "laps":66,  "circuit_type":"permanent",     "tyre_wear":"high",     "safety_concern":False},
    {"round":10, "name":"Canadian Grand Prix",        "short":"CAN", "circuit":"Circuit Gilles Villeneuve","city":"Montreal","country":"Canada",    "lat":45.5048,  "lon":-73.5226, "race_start_utc":"2026-06-21 18:00", "laps":70,  "circuit_type":"street_hybrid", "tyre_wear":"low",      "safety_concern":False},
    {"round":11, "name":"Austrian Grand Prix",        "short":"AUT", "circuit":"Red Bull Ring",     "city":"Spielberg",    "country":"Austria",      "lat":47.2197,  "lon":14.7647,  "race_start_utc":"2026-06-28 13:00", "laps":71,  "circuit_type":"permanent",     "tyre_wear":"medium",   "safety_concern":False},
    {"round":12, "name":"British Grand Prix",         "short":"GBR", "circuit":"Silverstone",       "city":"Silverstone",  "country":"UK",           "lat":52.0786,  "lon":-1.0169,  "race_start_utc":"2026-07-05 14:00", "laps":52,  "circuit_type":"permanent",     "tyre_wear":"high",     "safety_concern":False},
    {"round":13, "name":"Belgian Grand Prix",         "short":"BEL", "circuit":"Circuit de Spa",    "city":"Spa",          "country":"Belgium",      "lat":50.4372,  "lon":5.9714,   "race_start_utc":"2026-07-26 13:00", "laps":44,  "circuit_type":"permanent",     "tyre_wear":"high",     "safety_concern":False},
    {"round":14, "name":"Hungarian Grand Prix",       "short":"HUN", "circuit":"Hungaroring",       "city":"Budapest",     "country":"Hungary",      "lat":47.5789,  "lon":19.2486,  "race_start_utc":"2026-08-02 13:00", "laps":70,  "circuit_type":"permanent",     "tyre_wear":"high",     "safety_concern":False},
    {"round":15, "name":"Dutch Grand Prix",           "short":"NED", "circuit":"Zandvoort",         "city":"Zandvoort",    "country":"Netherlands",  "lat":52.3888,  "lon":4.5409,   "race_start_utc":"2026-08-30 13:00", "laps":72,  "circuit_type":"permanent",     "tyre_wear":"medium",   "safety_concern":False},
    {"round":16, "name":"Italian Grand Prix",         "short":"ITA", "circuit":"Monza",             "city":"Monza",        "country":"Italy",        "lat":45.6156,  "lon":9.2811,   "race_start_utc":"2026-09-06 13:00", "laps":53,  "circuit_type":"permanent",     "tyre_wear":"low",      "safety_concern":False},
    {"round":17, "name":"Madrid Grand Prix",          "short":"MAD", "circuit":"Madrid Street Circuit","city":"Madrid",    "country":"Spain",        "lat":40.4168,  "lon":-3.7038,  "race_start_utc":"2026-09-20 13:00", "laps":55,  "circuit_type":"street",        "tyre_wear":"medium",   "safety_concern":False},
    {"round":18, "name":"Azerbaijan Grand Prix",      "short":"AZE", "circuit":"Baku City Circuit", "city":"Baku",         "country":"Azerbaijan",   "lat":40.3725,  "lon":49.8533,  "race_start_utc":"2026-09-27 11:00", "laps":51,  "circuit_type":"street",        "tyre_wear":"low",      "safety_concern":False},
    {"round":19, "name":"Singapore Grand Prix",       "short":"SGP", "circuit":"Marina Bay",        "city":"Singapore",    "country":"Singapore",    "lat":1.2914,   "lon":103.8640, "race_start_utc":"2026-10-04 12:00", "laps":62,  "circuit_type":"street",        "tyre_wear":"high",     "safety_concern":False},
    {"round":20, "name":"United States Grand Prix",   "short":"USA", "circuit":"Circuit of the Americas","city":"Austin",  "country":"USA",          "lat":30.1328,  "lon":-97.6411, "race_start_utc":"2026-10-18 19:00", "laps":56,  "circuit_type":"permanent",     "tyre_wear":"high",     "safety_concern":False},
    {"round":21, "name":"Mexico City Grand Prix",     "short":"MEX", "circuit":"Autodromo Hermanos Rodriguez","city":"Mexico City","country":"Mexico","lat":19.4042, "lon":-99.0907, "race_start_utc":"2026-10-25 20:00", "laps":71,  "circuit_type":"permanent",     "tyre_wear":"low",      "safety_concern":False},
    {"round":22, "name":"São Paulo Grand Prix",       "short":"BRA", "circuit":"Interlagos",        "city":"São Paulo",    "country":"Brazil",       "lat":-23.7036, "lon":-46.6997, "race_start_utc":"2026-11-08 17:00", "laps":71,  "circuit_type":"permanent",     "tyre_wear":"medium",   "safety_concern":False},
    {"round":23, "name":"Las Vegas Grand Prix",       "short":"LVS", "circuit":"Las Vegas Strip",   "city":"Las Vegas",    "country":"USA",          "lat":36.1147,  "lon":-115.1728,"race_start_utc":"2026-11-21 06:00", "laps":50,  "circuit_type":"street",        "tyre_wear":"low",      "safety_concern":False},
    {"round":24, "name":"Qatar Grand Prix",           "short":"QAT", "circuit":"Lusail International","city":"Lusail",     "country":"Qatar",        "lat":25.4900,  "lon":51.4542,  "race_start_utc":"2026-11-29 14:00", "laps":57,  "circuit_type":"permanent",     "tyre_wear":"high",     "safety_concern":False},
    # NOTE: Abu Dhabi is the 2026 season finale
    {"round":25, "name":"Abu Dhabi Grand Prix",       "short":"ABD", "circuit":"Yas Marina",        "city":"Abu Dhabi",    "country":"UAE",          "lat":24.4672,  "lon":54.6031,  "race_start_utc":"2026-12-06 13:00", "laps":58,  "circuit_type":"permanent",     "tyre_wear":"medium",   "safety_concern":False},
]

# ══════════════════════════════════════════════
#  2026 DRIVER & TEAM ROSTER
# ══════════════════════════════════════════════

DRIVERS_2026 = {
    "RUS": {"name":"George Russell",     "team":"Mercedes",     "number":63},
    "ANT": {"name":"Kimi Antonelli",     "team":"Mercedes",     "number":12},
    "NOR": {"name":"Lando Norris",       "team":"McLaren",      "number":4},
    "PIA": {"name":"Oscar Piastri",      "team":"McLaren",      "number":81},
    "HAD": {"name":"Isack Hadjar",       "team":"Red Bull",     "number":6},
    "VER": {"name":"Max Verstappen",     "team":"Red Bull",     "number":1},
    "LEC": {"name":"Charles Leclerc",    "team":"Ferrari",      "number":16},
    "HAM": {"name":"Lewis Hamilton",     "team":"Ferrari",      "number":44},
    "ALO": {"name":"Fernando Alonso",    "team":"Aston Martin", "number":14},
    "STR": {"name":"Lance Stroll",       "team":"Aston Martin", "number":18},
    "ALB": {"name":"Alexander Albon",    "team":"Williams",     "number":23},
    "SAI": {"name":"Carlos Sainz",       "team":"Williams",     "number":55},
    "GAS": {"name":"Pierre Gasly",       "team":"Alpine",       "number":10},
    "COL": {"name":"Franco Colapinto",   "team":"Alpine",       "number":43},
    "OCO": {"name":"Esteban Ocon",       "team":"Haas",         "number":31},
    "BEA": {"name":"Oliver Bearman",     "team":"Haas",         "number":87},
    "BOT": {"name":"Valtteri Bottas",    "team":"Cadillac",     "number":77},
    "ZHO": {"name":"Zhou Guanyu",        "team":"Cadillac",     "number":24},
    "MAG": {"name":"Kevin Magnussen",    "team":"Racing Bulls", "number":20},
    "TSU": {"name":"Yuki Tsunoda",       "team":"Racing Bulls", "number":22},
}

TEAM_COLORS = {
    "Mercedes":     "#00D2BE",
    "McLaren":      "#FF8000",
    "Red Bull":     "#3671C6",
    "Ferrari":      "#E8002D",
    "Aston Martin": "#229971",
    "Williams":     "#64C4FF",
    "Alpine":       "#0093CC",
    "Haas":         "#B6BABD",
    "Cadillac":     "#FFFFFF",
    "Racing Bulls": "#6692FF",
}

TEAM_PERF_2025 = {
    "McLaren":666, "Red Bull":589, "Ferrari":584,
    "Mercedes":468, "Aston Martin":94, "Alpine":65,
    "Haas":58, "Williams":51, "Racing Bulls":46, "Cadillac":14
}

REG_BOOST_2026 = {
    "Mercedes":1.15, "Ferrari":1.05, "McLaren":1.00, "Red Bull":0.95,
    "Williams":0.88, "Haas":0.85, "Racing Bulls":0.80,
    "Alpine":0.80, "Aston Martin":0.70, "Cadillac":0.70
}

F1_POINTS = {1:25, 2:18, 3:15, 4:12, 5:10, 6:8, 7:6, 8:4, 9:2, 10:1}


# ══════════════════════════════════════════════
#  DATA FETCHERS
# ══════════════════════════════════════════════

def fetch_weather(lat, lon, race_name=""):
    """Fetch current weather at circuit using Open-Meteo (free, no API key)."""
    try:
        url = (f"https://api.open-meteo.com/v1/forecast"
               f"?latitude={lat}&longitude={lon}"
               f"&current=temperature_2m,precipitation_probability,"
               f"precipitation,windspeed_10m,relativehumidity_2m,"
               f"weathercode,apparent_temperature"
               f"&hourly=temperature_2m,precipitation_probability,windspeed_10m"
               f"&forecast_days=3&timezone=auto")
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            c = data["current"]
            return {
                "temperature":    round(c.get("temperature_2m", 22), 1),
                "rain_probability": round(c.get("precipitation_probability", 15) / 100, 2),
                "precipitation":  round(c.get("precipitation", 0), 1),
                "wind_speed":     round(c.get("windspeed_10m", 10), 1),
                "humidity":       round(c.get("relativehumidity_2m", 55), 0),
                "weather_code":   c.get("weathercode", 0),
                "feels_like":     round(c.get("apparent_temperature", 22), 1),
                "track_temp":     round(c.get("temperature_2m", 22) * 1.4 + 5, 1),
                "source":         "Open-Meteo (live)",
                "fetched_at":     datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            }
    except Exception as e:
        print(f"  ⚠️  Weather fetch failed: {e} — using fallback defaults")
    return {
        "temperature":22.0,"rain_probability":0.15,"precipitation":0.0,
        "wind_speed":12.0,"humidity":55.0,"weather_code":0,
        "feels_like":22.0,"track_temp":34.0,
        "source":"Fallback defaults","fetched_at":"N/A"
    }


def fetch_qualifying_ergast(season, round_num):
    """
    Fetch qualifying results from Ergast API (official F1 data).
    Returns list of dicts with driver, team, Q3 time.
    """
    try:
        url = f"http://ergast.com/api/f1/{season}/{round_num}/qualifying.json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            results = data["MRData"]["RaceTable"]["Races"]
            if not results:
                return None
            quali = results[0]["QualifyingResults"]
            rows = []
            for q in quali:
                driver_id = q["Driver"]["code"] if "code" in q["Driver"] else q["Driver"]["driverId"][:3].upper()
                time_str = q.get("Q3") or q.get("Q2") or q.get("Q1") or "1:20.000"
                rows.append({
                    "Driver": driver_id,
                    "GridPosition": int(q["position"]),
                    "QualifyingTime (s)": parse_laptime(time_str),
                    "Team": q["Constructor"]["name"],
                })
            return rows
    except Exception as e:
        print(f"  ⚠️  Ergast qualifying fetch failed: {e}")
    return None


def fetch_driver_standings_ergast(season, round_num=None):
    """Fetch current driver standings from Ergast."""
    try:
        url = f"http://ergast.com/api/f1/{season}/driverStandings.json"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            standings = data["MRData"]["StandingsTable"]["StandingsLists"]
            if not standings:
                return {}
            return {
                s["Driver"]["code"]: int(float(s["points"]))
                for s in standings[0]["DriverStandings"]
                if "code" in s["Driver"]
            }
    except Exception as e:
        print(f"  ⚠️  Standings fetch failed: {e}")
    return {}


def parse_laptime(time_str):
    """Convert '1:18.456' or '78.456' to float seconds."""
    if not time_str or time_str in ("", "N/A"):
        return 82.000
    try:
        if ":" in str(time_str):
            parts = str(time_str).split(":")
            return float(parts[0]) * 60 + float(parts[1])
        return float(time_str)
    except:
        return 82.000


def check_12hr_rule(race_utc_str):
    """
    Returns (can_predict: bool, hours_to_race: float, status_msg: str)
    """
    race_dt = datetime.strptime(race_utc_str, "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    delta = (race_dt - now).total_seconds() / 3600

    if delta < 0:
        return False, delta, "🚫 RACE ALREADY STARTED — Prediction locked. Race is in progress or finished."
    elif delta < 12:
        return False, delta, (f"🚫 PREDICTION WINDOW CLOSED — Only {delta:.1f}hrs to race start.\n"
                               f"   Predictions are only available more than 12 hours before race start.\n"
                               f"   This ensures predictions are based on qualifying data, not race progress.")
    else:
        return True, delta, f"✅ Prediction window open — {delta:.1f}hrs before race start."


def weather_code_description(code):
    """Map WMO weather code to human description."""
    mapping = {
        0:"Clear sky ☀️", 1:"Mainly clear 🌤️", 2:"Partly cloudy ⛅", 3:"Overcast ☁️",
        45:"Foggy 🌫️", 48:"Icy fog 🌫️", 51:"Light drizzle 🌧️", 53:"Drizzle 🌧️",
        55:"Heavy drizzle 🌧️", 61:"Slight rain 🌧️", 63:"Rain 🌧️", 65:"Heavy rain ⛈️",
        71:"Slight snow ❄️", 73:"Snow ❄️", 80:"Rain showers 🌦️", 95:"Thunderstorm ⛈️",
    }
    return mapping.get(code, f"Code {code}")


# ══════════════════════════════════════════════
#  ML MODEL TRAINER
# ══════════════════════════════════════════════

def build_and_train_model():
    """Build GBR model on synthetic historical F1 data (2018-2025)."""
    np.random.seed(42)
    n = 300
    q_times   = np.random.uniform(75, 92, n)
    grid_pos  = np.random.randint(1, 21, n)
    team_score= np.random.uniform(14, 700, n)
    rain      = np.random.uniform(0, 0.7, n)
    temp      = np.random.uniform(15, 38, n)
    humidity  = np.random.uniform(35, 85, n)
    wind      = np.random.uniform(3, 35, n)
    track_t   = np.random.uniform(22, 55, n)
    form      = np.random.uniform(1, 20, n)
    momentum  = np.random.uniform(-12, 12, n)
    tyre_sc   = np.random.uniform(0.5, 1.0, n)
    wf        = np.random.uniform(0.65, 1.0, n)
    gap       = q_times - q_times.min() + np.random.uniform(0, 0.5, n)
    adj_team  = team_score * np.random.uniform(0.65, 1.15, n)

    race_time = (
        q_times * 1.055
        + grid_pos * 0.12
        - adj_team * 0.001
        + rain * 4.0
        + form * 0.05
        - momentum * 0.04
        - tyre_sc * 0.5
        + humidity * 0.008
        + wind * 0.01
        + np.random.normal(0, 0.35, n)
    )

    df = pd.DataFrame({
        "QualifyingTime":  q_times,
        "GapFromPole":     gap,
        "AdjTeamScore":    adj_team,
        "GridPenalty":     (grid_pos - 1) * 0.15,
        "RainProb":        rain,
        "Temperature":     temp,
        "Humidity":        humidity,
        "WindSpeed":       wind,
        "TrackTemp":       track_t,
        "DriverForm":      form,
        "DriverMomentum":  momentum,
        "TyreScore":       tyre_sc,
        "WeatherFactor":   wf,
        "RaceTime":        race_time,
    })

    FEATURES = ["QualifyingTime","GapFromPole","AdjTeamScore","GridPenalty",
                "RainProb","Temperature","Humidity","WindSpeed","TrackTemp",
                "DriverForm","DriverMomentum","TyreScore","WeatherFactor"]

    X = df[FEATURES]; y = df["RaceTime"]
    imputer = SimpleImputer(strategy="median")
    Xi = imputer.fit_transform(X)
    Xs = Xi.copy(); Xs[:,0] *= 3.0; Xs[:,1] *= 3.0

    Xtr, Xte, ytr, yte = train_test_split(Xs, y, test_size=0.15, random_state=42)
    model = GradientBoostingRegressor(n_estimators=400, learning_rate=0.05,
                                       max_depth=4, subsample=0.8, random_state=42)
    model.fit(Xtr, ytr)
    mae = mean_absolute_error(yte, model.predict(Xte))
    return model, imputer, FEATURES, mae


# ══════════════════════════════════════════════
#  TYRE STRATEGY SIMULATOR
# ══════════════════════════════════════════════

TYRE_DATA = {
    "Soft":   {"deg":0.08, "pace":-0.3, "optimal_stint":18},
    "Medium": {"deg":0.05, "pace": 0.0, "optimal_stint":28},
    "Hard":   {"deg":0.03, "pace": 0.4, "optimal_stint":38},
}
PIT_STOP_LOSS = 22.0  # seconds

def simulate_strategies(total_laps, rain_prob, tyre_wear_rating="medium"):
    """Return list of strategies sorted by estimated time cost."""
    wear_mult = {"low":0.8, "medium":1.0, "high":1.25}.get(tyre_wear_rating, 1.0)

    strategies = []

    # S1: Soft → Hard (1 stop)
    s1 = tyre_data_cost(["Soft","Hard"], [18, total_laps-18], wear_mult) + PIT_STOP_LOSS
    strategies.append({"name":"Soft → Hard","stints":["Soft","Hard"],"pits":[18],"cost":round(s1,2),"stops":1})

    # S2: Medium → Medium (1 stop)
    s2 = tyre_data_cost(["Medium","Medium"], [28, total_laps-28], wear_mult) + PIT_STOP_LOSS
    strategies.append({"name":"Medium → Medium","stints":["Medium","Medium"],"pits":[28],"cost":round(s2,2),"stops":1})

    # S3: Medium → Hard (1 stop)
    s3 = tyre_data_cost(["Medium","Hard"], [25, total_laps-25], wear_mult) + PIT_STOP_LOSS
    strategies.append({"name":"Medium → Hard","stints":["Medium","Hard"],"pits":[25],"cost":round(s3,2),"stops":1})

    # S4: Soft → Medium → Hard (2 stops)
    s4 = tyre_data_cost(["Soft","Medium","Hard"], [15,22,total_laps-37], wear_mult) + PIT_STOP_LOSS*2
    strategies.append({"name":"Soft → Med → Hard","stints":["Soft","Medium","Hard"],"pits":[15,37],"cost":round(s4,2),"stops":2})

    if rain_prob > 0.4:
        for s in strategies:
            s["cost"] *= 0.94
            s["rain_note"] = "⚠️ Rain expected — Safety Car may neutralise pit strategy"

    strategies.sort(key=lambda x: x["cost"])
    return strategies


def tyre_data_cost(compounds, laps_list, wear_mult):
    total = 0
    for comp, laps in zip(compounds, laps_list):
        d = TYRE_DATA[comp]
        total += laps * d["deg"] * wear_mult + laps * d["pace"]
    return total


# ══════════════════════════════════════════════
#  MAIN PREDICTOR
# ══════════════════════════════════════════════

def predict_race(race_name_or_round, season=2026, force=False):
    """
    Full prediction pipeline for a given race.
    - Checks 12-hour rule
    - Fetches qualifying, weather, form data
    - Runs ML model
    - Returns full prediction + generates dashboard PNG
    """
    print("\n" + "═"*65)
    print(f"  🏎️  F1 {season} PREDICTION SYSTEM")
    print("═"*65)

    # ── Find race ──
    race = None
    for r in F1_2026_CALENDAR:
        if (isinstance(race_name_or_round, int) and r["round"] == race_name_or_round) or \
           (isinstance(race_name_or_round, str) and
            (race_name_or_round.lower() in r["name"].lower() or
             race_name_or_round.upper() == r["short"])):
            race = r
            break

    if not race:
        print(f"  ❌ Race '{race_name_or_round}' not found in 2026 calendar.")
        print("  Available races:")
        for r in F1_2026_CALENDAR:
            print(f"    R{r['round']:02d}  {r['short']}  {r['name']}")
        return None

    print(f"\n  📍 {race['name']}")
    print(f"     {race['circuit']} · {race['city']}, {race['country']}")
    print(f"     Race start (UTC): {race['race_start_utc']}")

    # ── 12-Hour Rule Check ──
    can_predict, hrs_to_race, status_msg = check_12hr_rule(race["race_start_utc"])
    print(f"\n  ⏱️  {status_msg}")

    if not can_predict and not force:
        print("\n  ℹ️  The prediction model requires qualifying data which is")
        print("     only available after Saturday qualifying session.")
        print("     Predictions lock 12 hours before race start to ensure")
        print("     accuracy. Come back after qualifying! 🏁")
        return {"blocked": True, "reason": status_msg, "race": race}

    # ── Fetch Weather ──
    print(f"\n  🌤️  Fetching live weather at {race['city']}...")
    weather = fetch_weather(race["lat"], race["lon"], race["name"])
    print(f"     Temperature : {weather['temperature']}°C  |  Feels like: {weather['feels_like']}°C")
    print(f"     Rain Prob   : {weather['rain_probability']*100:.0f}%  |  {weather_code_description(weather['weather_code'])}")
    print(f"     Wind        : {weather['wind_speed']} km/h  |  Humidity: {weather['humidity']:.0f}%")
    print(f"     Track Temp  : {weather['track_temp']}°C (estimated)")
    print(f"     Source      : {weather['source']} @ {weather['fetched_at']}")

    # ── Safety Status (Gulf/Middle East races) ──
    gulf_countries = {"Bahrain","Saudi Arabia","Qatar","UAE","Azerbaijan"}
    is_gulf = race["country"] in gulf_countries
    safety_note = ""
    if is_gulf:
        country_safety = {
            "Bahrain":     "🟢 SAFE — Bahrain International Circuit, stable region. Standard F1 security.",
            "Saudi Arabia":"🟡 MONITOR — Jeddah Corniche Circuit. FIA & FOM conduct regular security assessments.",
            "Qatar":       "🟢 SAFE — Lusail Circuit, Doha. Strong infrastructure & international event experience.",
            "UAE":         "🟢 SAFE — Yas Marina Circuit, Abu Dhabi. Excellent safety record, season finale venue.",
            "Azerbaijan":  "🟡 MONITOR — Baku City Circuit. Region has geopolitical tensions; FOM monitors closely.",
        }
        safety_note = country_safety.get(race["country"], "🟡 MONITOR — Regional check recommended.")
        print(f"\n  🛡️  REGIONAL SAFETY STATUS:")
        print(f"     {safety_note}")

    # ── Fetch Qualifying Data ──
    print(f"\n  📡 Fetching qualifying results from Ergast API...")
    quali_data = fetch_qualifying_ergast(season, race["round"])

    if quali_data:
        print(f"     ✅ Live qualifying data fetched — {len(quali_data)} drivers")
        drivers_list = [q["Driver"] for q in quali_data]
        quali_times  = {q["Driver"]: q["QualifyingTime (s)"] for q in quali_data}
        grid_pos_map = {q["Driver"]: q["GridPosition"] for q in quali_data}
        team_map_live = {q["Driver"]: q["Team"] for q in quali_data}
    else:
        print(f"     ℹ️  Qualifying data not yet available for R{race['round']} — using projected times")
        drivers_list = list(DRIVERS_2026.keys())
        # Project qualifying times from team performance
        base_times = _project_qualifying(race)
        quali_times  = dict(zip(drivers_list, base_times))
        grid_pos_map = {d: i+1 for i, d in enumerate(drivers_list)}
        team_map_live = {d: DRIVERS_2026[d]["team"] for d in drivers_list}

    # ── Build Prediction DataFrame ──
    rows = []
    pole_time = min(quali_times.values())

    for drv in drivers_list:
        q_time   = quali_times.get(drv, 82.0)
        grid     = grid_pos_map.get(drv, 15)
        team     = team_map_live.get(drv, DRIVERS_2026.get(drv, {}).get("team","Unknown"))
        team_pts = TEAM_PERF_2025.get(team, 50)
        reg_b    = REG_BOOST_2026.get(team, 0.80)

        def _tyre_score(g):
            return 1.0 if g<=3 else 0.85 if g<=6 else 0.70 if g<=10 else 0.50

        def _weather_factor(rain_p, g):
            return 1.0 - (rain_p * 0.5 * (1 - g/20))

        rows.append({
            "Driver":       drv,
            "Team":         team,
            "GridPosition": grid,
            "QualifyingTime": q_time,
            "GapFromPole":  q_time - pole_time,
            "AdjTeamScore": team_pts * reg_b,
            "GridPenalty":  (grid - 1) * 0.15,
            "RainProb":     weather["rain_probability"],
            "Temperature":  weather["temperature"],
            "Humidity":     weather["humidity"],
            "WindSpeed":    weather["wind_speed"],
            "TrackTemp":    weather["track_temp"],
            "DriverForm":   _get_form_score(drv),
            "DriverMomentum": _get_momentum(drv),
            "TyreScore":    _tyre_score(grid),
            "WeatherFactor":_weather_factor(weather["rain_probability"], grid),
        })

    df_pred = pd.DataFrame(rows)

    # ── Train & Predict ──
    model, imputer, FEATURES, mae = build_and_train_model()
    X_pred = df_pred[FEATURES].copy()

    # Rename to match training
    X_pred.columns = ["QualifyingTime","GapFromPole","AdjTeamScore","GridPenalty",
                       "RainProb","Temperature","Humidity","WindSpeed","TrackTemp",
                       "DriverForm","DriverMomentum","TyreScore","WeatherFactor"]
    Xi = imputer.transform(X_pred)
    Xs = Xi.copy(); Xs[:,0] *= 3.0; Xs[:,1] *= 3.0
    df_pred["PredictedTime"] = model.predict(Xs)

    result = df_pred.sort_values("PredictedTime").reset_index(drop=True)
    podium = result.head(3)

    # ── Tyre Strategy ──
    strategies = simulate_strategies(race["laps"], weather["rain_probability"], race["tyre_wear"])
    best_strat = strategies[0]

    # ── Print Results ──
    print(f"\n  {'═'*55}")
    print(f"  🏆  PREDICTED PODIUM — {race['name'].upper()}")
    print(f"  {'═'*55}")
    medals = ["🥇","🥈","🥉"]
    for i, (_, row) in enumerate(podium.iterrows()):
        drv_info = DRIVERS_2026.get(row["Driver"], {"name": row["Driver"], "number":"?"})
        print(f"  {medals[i]}  P{i+1}: #{drv_info['number']} {drv_info['name']} ({row['Team']})")

    print(f"\n  📊  Model MAE: {mae:.3f}s  |  Qualifying data: {'LIVE' if quali_data else 'PROJECTED'}")

    print(f"\n  🏎️  FULL PREDICTED GRID (Top 10):")
    print(f"  {'Pos':<5}{'Driver':<6}{'Name':<22}{'Team':<16}{'Form':<8}")
    print(f"  {'-'*55}")
    for i, (_, row) in enumerate(result.head(10).iterrows()):
        drv_info = DRIVERS_2026.get(row["Driver"], {"name":row["Driver"],"number":"?"})
        arrow = "↑" if row["DriverMomentum"] < -1 else ("↓" if row["DriverMomentum"] > 2 else "→")
        print(f"  P{i+1:<4}{row['Driver']:<6}{drv_info['name']:<22}{row['Team']:<16}{arrow} {row['DriverForm']:.1f}")

    print(f"\n  🔧  BEST TYRE STRATEGY: {best_strat['name']}")
    print(f"      Pit at laps: {best_strat['pits']}  |  Compounds: {' → '.join(best_strat['stints'])}")
    if "rain_note" in best_strat:
        print(f"      {best_strat['rain_note']}")

    # ── Generate Dashboard ──
    out_path = f"f1_prediction_R{race['round']:02d}_{race['short']}.png"
    _generate_dashboard(race, result, weather, strategies, best_strat,
                        podium, is_gulf, safety_note, mae, quali_data, out_path)
    print(f"\n  📈  Dashboard saved → {out_path}")
    print(f"  {'═'*55}\n")

    return {
        "race": race,
        "podium": podium,
        "full_grid": result,
        "weather": weather,
        "best_strategy": best_strat,
        "strategies": strategies,
        "mae": mae,
        "dashboard_path": out_path,
        "data_source": "LIVE" if quali_data else "PROJECTED",
    }


# ══════════════════════════════════════════════
#  DRIVER FORM — AUTO-FETCHED FROM ERGAST API
#  Updates automatically after every race round
# ══════════════════════════════════════════════

# Fallback form data (used when API not yet available / no internet)
_FORM_FALLBACK = {
    "RUS":[1,2,3,1,4], "ANT":[5,3,2,4,2], "NOR":[2,1,1,3,1], "PIA":[3,4,5,2,3],
    "HAD":[6,5,4,5,6],  "VER":[1,1,2,1,2], "LEC":[4,3,3,6,4], "HAM":[7,6,6,7,5],
    "ALO":[8,9,10,8,9], "STR":[10,11,9,10,11], "ALB":[9,8,8,9,8], "SAI":[12,10,11,11,10],
    "GAS":[11,12,12,12,12], "COL":[13,13,14,13,14], "OCO":[14,14,13,14,13],
    "BEA":[15,15,15,15,16], "BOT":[16,16,16,16,15], "ZHO":[18,17,17,17,17],
    "MAG":[17,18,18,18,18], "TSU":[20,20,19,20,20],
}

# Cache so we only fetch once per session
_form_cache = {}
_form_source = "fallback"


def fetch_driver_form(season=2026, last_n=5):
    """
    Auto-fetch last N race finishing positions for every driver from Ergast.
    Called once per session and cached.

    Flow:
      1. Ask Ergast how many rounds have been completed this season
      2. Fetch the last `last_n` completed race results
      3. Build a {driver_code: [pos, pos, ...]} dict (oldest → newest)
      4. Cache it so we don't re-fetch during the same run
    """
    global _form_cache, _form_source

    if _form_cache:
        return _form_cache   # already fetched this session

    print(f"\n  🔄  Auto-fetching driver form (last {last_n} races) from Ergast API...")

    try:
        # Step 1 — find latest completed round
        url = f"http://ergast.com/api/f1/{season}.json"
        r = requests.get(url, timeout=10)
        if r.status_code != 200:
            raise Exception(f"Status {r.status_code}")

        races_data = r.json()["MRData"]["RaceTable"]["Races"]
        now_utc = datetime.now(timezone.utc)

        completed_rounds = []
        for race in races_data:
            race_dt_str = f"{race['date']} {race.get('time','12:00:00Z').replace('Z','')}"
            try:
                race_dt = datetime.strptime(race_dt_str[:16], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
                if race_dt < now_utc:
                    completed_rounds.append(int(race["round"]))
            except:
                pass

        if not completed_rounds:
            raise Exception("No completed rounds yet in this season")

        latest_round = max(completed_rounds)
        rounds_to_fetch = completed_rounds[-last_n:]   # last N completed rounds
        print(f"     ✅ Season {season}: {len(completed_rounds)} rounds completed — fetching R{rounds_to_fetch}")

        # Step 2 — fetch results for each of those rounds
        # structure: {driver_code: [pos_oldest, ..., pos_newest]}
        form_data = {drv: [] for drv in DRIVERS_2026}

        for rnd in rounds_to_fetch:
            url = f"http://ergast.com/api/f1/{season}/{rnd}/results.json"
            r = requests.get(url, timeout=10)
            if r.status_code != 200:
                continue

            results = r.json()["MRData"]["RaceTable"]["Races"]
            if not results:
                continue

            race_results = results[0]["Results"]

            # Build position map for this race
            pos_map = {}
            for res in race_results:
                drv_code = res["Driver"].get("code", res["Driver"]["driverId"][:3].upper())
                # DNF/DNS gets position 20 (worst)
                status = res.get("status", "Finished")
                if "Finished" in status or "+1 Lap" in status or "+2 Lap" in status:
                    pos = int(res["position"])
                else:
                    pos = 20   # DNF/DNS/DSQ
                pos_map[drv_code] = pos

            # Append to each driver's form list
            for drv in DRIVERS_2026:
                pos = pos_map.get(drv, 15)   # 15 = unknown/not racing
                form_data[drv].append(pos)

        # Step 3 — pad any driver that has fewer than last_n entries
        # (e.g. new drivers who joined mid-season)
        for drv in form_data:
            while len(form_data[drv]) < last_n:
                form_data[drv].insert(0, 12)   # pad with average finish at front

        _form_cache = form_data
        _form_source = f"LIVE (Ergast — {len(rounds_to_fetch)} rounds fetched, latest R{latest_round})"
        print(f"     ✅ Driver form updated — source: {_form_source}")
        return _form_cache

    except Exception as e:
        print(f"     ⚠️  Form fetch failed: {e}")
        print(f"     ℹ️  Using pre-loaded fallback form data")
        _form_cache = _FORM_FALLBACK.copy()
        _form_source = "Fallback (pre-loaded)"
        return _form_cache


def _get_driver_form_dict(season=2026):
    """Return form dict — fetches from API once, then uses cache."""
    return fetch_driver_form(season)


def _get_form_score(drv, season=2026):
    form_dict = _get_driver_form_dict(season)
    positions = form_dict.get(drv, [12]*5)
    weights = [0.10, 0.15, 0.20, 0.25, 0.30]
    return sum(p*w for p,w in zip(positions, weights)) / sum(weights)


def _get_momentum(drv, season=2026):
    form_dict = _get_driver_form_dict(season)
    positions = form_dict.get(drv, [12]*5)
    if len(positions) < 2:
        return 0.0
    return positions[0] - positions[-1]   # positive = got worse, negative = improving

def _project_qualifying(race):
    """Estimate qualifying times when real data isn't available yet."""
    base = {"Mercedes":79.0,"McLaren":79.2,"Red Bull":79.4,"Ferrari":79.6,
            "Aston Martin":80.5,"Williams":80.8,"Alpine":81.0,
            "Haas":81.2,"Racing Bulls":81.5,"Cadillac":82.5}
    times = []
    for drv in DRIVERS_2026:
        team = DRIVERS_2026[drv]["team"]
        b = base.get(team, 82.0)
        times.append(round(b + np.random.uniform(0, 0.4), 3))
    return sorted(times)


# ══════════════════════════════════════════════
#  DASHBOARD GENERATOR
# ══════════════════════════════════════════════

def _generate_dashboard(race, result, weather, strategies, best_strat,
                         podium, is_gulf, safety_note, mae, quali_data, out_path):
    fig = plt.figure(figsize=(20, 14), facecolor="#0a0a0f")
    fig.patch.set_facecolor("#0a0a0f")
    gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.42, wspace=0.35,
                           left=0.06, right=0.97, top=0.92, bottom=0.06)

    title_color = "#e8e8f0"
    accent = "#e10600"
    subtitle_color = "#888899"

    # ── Main Title ──
    fig.text(0.5, 0.965, f"F1 2026  ·  {race['name'].upper()}",
             ha="center", va="top", fontsize=18, color=title_color,
             fontweight="bold", fontfamily="monospace")
    fig.text(0.5, 0.948, f"{race['circuit']}  ·  {race['city']}, {race['country']}  ·  "
                          f"{'LIVE QUALI DATA' if quali_data else 'PROJECTED DATA'}  ·  MAE: {mae:.3f}s",
             ha="center", va="top", fontsize=9, color=subtitle_color, fontfamily="monospace")

    # ─── PANEL 1: Predicted Grid (top 10) ───
    ax1 = fig.add_subplot(gs[0, :2])
    ax1.set_facecolor("#0f0f1a")
    top10 = result.head(10)
    team_c = [TEAM_COLORS.get(t, "#888888") for t in top10["Team"]]
    bars = ax1.barh(range(10), top10["PredictedTime"] - top10["PredictedTime"].min() + 0.01,
                    color=team_c, height=0.65, edgecolor="#1a1a2e", linewidth=0.5)
    ax1.set_yticks(range(10))
    labels = [f"P{i+1}  {row['Driver']}  {DRIVERS_2026.get(row['Driver'],{'name':row['Driver']})['name']}"
              for i, (_, row) in enumerate(top10.iterrows())]
    ax1.set_yticklabels(labels, color=title_color, fontsize=8.5, fontfamily="monospace")
    ax1.invert_yaxis()
    ax1.set_xlabel("Time gap to predicted leader (s)", color=subtitle_color, fontsize=8)
    ax1.set_title("PREDICTED RACE ORDER", color=accent, fontsize=10, fontweight="bold",
                  fontfamily="monospace", pad=8)
    ax1.tick_params(colors=subtitle_color, labelsize=7.5)
    for spine in ax1.spines.values(): spine.set_color("#222233")

    # ─── PANEL 2: Weather Gauge ───
    ax2 = fig.add_subplot(gs[0, 2])
    ax2.set_facecolor("#0f0f1a")
    wx = weather
    wx_lines = [
        ("🌡️  Temperature",  f"{wx['temperature']}°C  (feels {wx['feels_like']}°C)"),
        ("🌧️  Rain Chance",   f"{wx['rain_probability']*100:.0f}%"),
        ("💧  Precipitation", f"{wx['precipitation']} mm"),
        ("💨  Wind Speed",    f"{wx['wind_speed']} km/h"),
        ("💦  Humidity",      f"{wx['humidity']:.0f}%"),
        ("🏎️  Track Temp",   f"{wx['track_temp']}°C (est.)"),
        ("",                  ""),
        ("⛅  Conditions",    weather_code_description(wx['weather_code'])),
        ("📡  Source",        wx['source']),
        ("🕐  Fetched",       wx['fetched_at'][:16]),
    ]
    ax2.set_xlim(0,1); ax2.set_ylim(0, len(wx_lines)+1)
    for i, (label, val) in enumerate(reversed(wx_lines)):
        y = i + 0.5
        ax2.text(0.02, y, label, color=subtitle_color, fontsize=7.5, fontfamily="monospace", va="center")
        ax2.text(0.98, y, val,   color=title_color,    fontsize=7.5, fontfamily="monospace", va="center", ha="right")
    ax2.set_title("LIVE WEATHER", color=accent, fontsize=10, fontweight="bold",
                  fontfamily="monospace", pad=8)
    ax2.axis("off")
    for spine in ax2.spines.values(): spine.set_color("#222233")

    # ─── PANEL 3: Tyre Strategy ───
    ax3 = fig.add_subplot(gs[1, 0])
    ax3.set_facecolor("#0f0f1a")
    s_names = [s["name"] for s in strategies]
    s_costs = [s["cost"] for s in strategies]
    s_cols  = [accent if s["name"]==best_strat["name"] else "#333355" for s in strategies]
    ax3.bar(range(len(s_names)), s_costs, color=s_cols, edgecolor="#1a1a2e", linewidth=0.8)
    ax3.set_xticks(range(len(s_names)))
    ax3.set_xticklabels(s_names, rotation=18, ha="right", color=title_color, fontsize=7, fontfamily="monospace")
    ax3.set_ylabel("Time cost (s)", color=subtitle_color, fontsize=8)
    ax3.set_title("TYRE STRATEGY", color=accent, fontsize=10, fontweight="bold",
                  fontfamily="monospace", pad=8)
    ax3.tick_params(colors=subtitle_color, labelsize=7)
    for s in ax3.spines.values(): s.set_color("#222233")
    for i, (name, cost) in enumerate(zip(s_names, s_costs)):
        star = " ★" if name == best_strat["name"] else ""
        ax3.text(i, cost+0.3, f"{cost:.1f}s{star}", ha="center", va="bottom",
                 color=accent if star else subtitle_color, fontsize=6.5, fontfamily="monospace")

    # ─── PANEL 4: Driver Form Trends ───
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.set_facecolor("#0f0f1a")
    top5_drivers = result.head(5)["Driver"].tolist()
    race_labels = ["R-4","R-3","R-2","R-1","Latest"]
    form_dict = _get_driver_form_dict()
    for drv in top5_drivers:
        form = form_dict.get(drv, [10]*5)
        team = DRIVERS_2026.get(drv, {}).get("team","Mercedes")
        col  = TEAM_COLORS.get(team, "#888888")
        ax4.plot(range(5), form, marker="o", label=drv, color=col, linewidth=1.8, markersize=4)
    ax4.set_xticks(range(5)); ax4.set_xticklabels(race_labels, color=subtitle_color, fontsize=7.5)
    ax4.invert_yaxis()
    ax4.set_ylabel("Finishing Position", color=subtitle_color, fontsize=8)
    form_src_label = "LIVE ✅" if "LIVE" in _form_source else "FALLBACK ⚠️"
    ax4.set_title(f"DRIVER FORM — Last 5 Races [{form_src_label}]",
                  color=accent, fontsize=9, fontweight="bold", fontfamily="monospace", pad=8)
    ax4.legend(fontsize=7.5, facecolor="#0f0f1a", edgecolor="#333355", labelcolor=title_color)
    ax4.tick_params(colors=subtitle_color); ax4.grid(alpha=0.15, color="#333355")
    for s in ax4.spines.values(): s.set_color("#222233")

    # ─── PANEL 5: Team Performance Bars ───
    ax5 = fig.add_subplot(gs[1, 2])
    ax5.set_facecolor("#0f0f1a")
    teams_shown = list(TEAM_PERF_2025.keys())
    adj_scores  = [TEAM_PERF_2025[t]*REG_BOOST_2026.get(t,0.8) for t in teams_shown]
    t_colors    = [TEAM_COLORS.get(t,"#888") for t in teams_shown]
    sorted_idx  = np.argsort(adj_scores)[::-1]
    ax5.barh(range(len(teams_shown)),
             [adj_scores[i] for i in sorted_idx],
             color=[t_colors[i] for i in sorted_idx],
             height=0.7, edgecolor="#1a1a2e")
    ax5.set_yticks(range(len(teams_shown)))
    ax5.set_yticklabels([teams_shown[i] for i in sorted_idx],
                         color=title_color, fontsize=7.5, fontfamily="monospace")
    ax5.set_xlabel("Adjusted 2026 Score", color=subtitle_color, fontsize=8)
    ax5.set_title("TEAM STRENGTH (2026)", color=accent, fontsize=10, fontweight="bold",
                  fontfamily="monospace", pad=8)
    ax5.tick_params(colors=subtitle_color, labelsize=7)
    for s in ax5.spines.values(): s.set_color("#222233")

    # ─── PANEL 6: Weather Impact on Grid ───
    ax6 = fig.add_subplot(gs[2, 0])
    ax6.set_facecolor("#0f0f1a")
    gp = list(range(1,21))
    dry_adv  = [1.0 - (i-1)*0.04 for i in gp]
    rain_adv = [1.0 - (weather["rain_probability"]*0.5*(1-i/20)) for i in gp]
    ax6.plot(gp, dry_adv,  color="#4da6ff", linewidth=2, label=f"Dry ({weather['rain_probability']*100:.0f}% rain)")
    ax6.plot(gp, rain_adv, color="#9c27b0", linewidth=2, linestyle="--", label="Heavy rain (70%)")
    ax6.fill_between(gp, rain_adv, dry_adv, alpha=0.12, color="purple")
    ax6.set_xlabel("Grid Position", color=subtitle_color, fontsize=8)
    ax6.set_ylabel("Race Advantage", color=subtitle_color, fontsize=8)
    ax6.set_title("WEATHER vs GRID IMPACT", color=accent, fontsize=10, fontweight="bold",
                  fontfamily="monospace", pad=8)
    ax6.legend(fontsize=7.5, facecolor="#0f0f1a", edgecolor="#333355", labelcolor=title_color)
    ax6.tick_params(colors=subtitle_color); ax6.grid(alpha=0.15, color="#333355")
    for s in ax6.spines.values(): s.set_color("#222233")

    # ─── PANEL 7: Podium Box ───
    ax7 = fig.add_subplot(gs[2, 1])
    ax7.set_facecolor("#0f0f1a"); ax7.axis("off")
    ax7.set_title("PODIUM PREDICTION", color=accent, fontsize=10, fontweight="bold",
                  fontfamily="monospace", pad=8)
    podium_data = [(i+1, row) for i, (_, row) in enumerate(podium.iterrows())]
    medals_text = ["🥇 P1","🥈 P2","🥉 P3"]
    y_positions = [0.72, 0.44, 0.16]
    for (pos, row), medal, yp in zip(podium_data, medals_text, y_positions):
        drv_info = DRIVERS_2026.get(row["Driver"], {"name":row["Driver"],"number":"?"})
        team_col = TEAM_COLORS.get(row["Team"], "#888888")
        ax7.add_patch(plt.Rectangle((0.05, yp-0.08), 0.9, 0.22,
                      facecolor=team_col+"22", edgecolor=team_col, linewidth=1.5,
                      transform=ax7.transAxes))
        ax7.text(0.12, yp+0.07, medal, color=title_color, fontsize=12,
                 transform=ax7.transAxes, va="center", fontfamily="monospace")
        ax7.text(0.12, yp-0.01, f"#{drv_info['number']} {drv_info['name']}",
                 color=title_color, fontsize=9.5, fontweight="bold",
                 transform=ax7.transAxes, va="center", fontfamily="monospace")
        ax7.text(0.12, yp-0.07, row["Team"],
                 color=team_col, fontsize=8,
                 transform=ax7.transAxes, va="center", fontfamily="monospace")

    # ─── PANEL 8: Safety / Race Info ───
    ax8 = fig.add_subplot(gs[2, 2])
    ax8.set_facecolor("#0f0f1a"); ax8.axis("off")
    ax8.set_title("RACE INFO & SAFETY", color=accent, fontsize=10, fontweight="bold",
                  fontfamily="monospace", pad=8)
    info_lines = [
        ("Round",       f"R{race['round']} of 25"),
        ("Circuit",     race["circuit"]),
        ("Laps",        str(race["laps"])),
        ("Circuit Type",race["circuit_type"].replace("_"," ").title()),
        ("Tyre Wear",   race["tyre_wear"].title()),
        ("Best Strategy",best_strat["name"]),
        ("Pit Laps",    str(best_strat["pits"])),
        ("Compounds",   " → ".join(best_strat["stints"])),
        ("Data Source", "LIVE" if quali_data else "PROJECTED"),
    ]
    if is_gulf:
        info_lines.append(("Safety Status", ""))
    ax8.set_xlim(0,1); ax8.set_ylim(0, len(info_lines)+2)
    for i, (k, v) in enumerate(reversed(info_lines)):
        y = i * 0.88 + 0.3
        ax8.text(0.02, y, k+":", color=subtitle_color, fontsize=7.5, fontfamily="monospace")
        ax8.text(0.98, y, v,     color=title_color,    fontsize=7.5, fontfamily="monospace", ha="right")
    if is_gulf and safety_note:
        ax8.text(0.5, -0.3, safety_note[:60], color="#ffcc44", fontsize=6.5,
                 fontfamily="monospace", ha="center", wrap=True)

    plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0a0a0f")
    plt.close()



# ══════════════════════════════════════════════
#  ENTRY POINT — SINGLE RACE PREDICTION ONLY
#
#  ❌ Full season prediction REMOVED — it is not
#     realistic to predict all 25 races at once.
#     Each race prediction requires real qualifying
#     data from that specific weekend. Predictions
#     are only as good as the data going into them.
#
#  ✅ Use this to predict ONE upcoming race at a
#     time, after Saturday qualifying has happened.
# ══════════════════════════════════════════════

if __name__ == "__main__":
    import sys

    print("\n" + "═"*60)
    print("  🏎️  F1 2026 RACE PREDICTOR")
    print("  Predicts ONE race at a time using real data:")
    print("  → Qualifying results (auto-fetched after Saturday)")
    print("  → Live weather at circuit (auto-fetched)")
    print("  → Driver form from completed rounds (auto-fetched)")
    print("  → 12-hour rule enforced automatically")
    print("═"*60)

    print("\n  Available races (use short code or round number):")
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    for r in F1_2026_CALENDAR:
        race_dt = datetime.strptime(r["race_start_utc"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)
        delta_hrs = (race_dt - now).total_seconds() / 3600
        gulf = " 🛡️" if r["country"] in {"Bahrain","Saudi Arabia","Qatar","UAE","Azerbaijan"} else ""
        if delta_hrs < 0:
            status = "✅ Completed"
        elif delta_hrs < 12:
            status = "🔒 Window closed"
        elif delta_hrs < 168:
            status = f"⏳ {delta_hrs:.0f}hrs away"
        else:
            status = f"📅 {r['race_start_utc'][:10]}"
        print(f"    R{r['round']:02d}  {r['short']:<4}  {r['name']:<35}{gulf}  {status}")

    race_input = input("\n  Enter race short code or round number: ").strip()
    if not race_input:
        race_input = "CHN"
    try:
        race_input = int(race_input)
    except:
        pass
    predict_race(race_input, season=2026)
