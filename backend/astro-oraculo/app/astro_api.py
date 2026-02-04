"""
Unified FastAPI application providing endpoints for daily transits and natal charts.
This module consolidates functionality so that both `/transits/daily` and `/natal` endpoints are available from a single ASGI application.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import datetime
import pytz
import os
import swisseph as swe

app = FastAPI()

# enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# set swiss ephemeris path
swe.set_ephe_path(os.getenv("EPHE_PATH", "/app/ephe"))

# define aspects and orbs
ASPECT_TYPES = {
    "conjunction": (0, 8),
    "sextile": (60, 6),
    "square": (90, 6),
    "trine": (120, 6),
    "opposition": (180, 8),
}

# planet ids
PLANET_IDS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Uranus": swe.URANUS,
    "Neptune": swe.NEPTUNE,
    "Pluto": swe.PLUTO,
}

SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

def _angle_diff(a1: float, a2: float) -> float:
    diff = abs(a1 - a2) % 360
    return min(diff, 360 - diff)

def _compute_positions_and_aspects(jd: float, lat: float, lon: float):
    positions = {}
    # compute planet positions
    for name, pid in PLANET_IDS.items():
        result, _ = swe.calc_ut(jd, pid)
        lon_deg = result[0] % 360
        sign_index = int(lon_deg // 30)
        positions[name] = {
            "longitude": lon_deg,
            "sign": SIGNS[sign_index],
            "degree": lon_deg % 30,
        }
    # compute houses to get ascendant and midheaven
    cusps, ascmc = swe.houses(jd, lat, lon)
    asc_lon = ascmc[0] % 360
    mc_lon = ascmc[1] % 360
    positions["Ascendant"] = {
        "longitude": asc_lon,
        "sign": SIGNS[int(asc_lon // 30)],
        "degree": asc_lon % 30,
    }
    positions["Midheaven"] = {
        "longitude": mc_lon,
        "sign": SIGNS[int(mc_lon // 30)],
        "degree": mc_lon % 30,
    }
    # compute aspects
    aspects = []
    names = list(positions.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            lon1 = positions[names[i]]["longitude"]
            lon2 = positions[names[j]]["longitude"]
            diff = _angle_diff(lon1, lon2)
            for aspect_name, (angle, orb) in ASPECT_TYPES.items():
                if abs(diff - angle) <= orb:
                    aspects.append({
                        "planet1": names[i],
                        "planet2": names[j],
                        "aspect": aspect_name,
                        "orb": round(abs(diff - angle), 2),
                    })
                    break
    return positions, aspects

@app.get("/")
def read_root():
    return {"message": "Astro Oraculo API is running"}

@app.get("/transits/daily")
def transits_daily(date: str = None, time: str = "12:00", zone: str = "UTC"):
    """
    Return planetary positions, Ascendant and Midheaven, and aspects for a given date/time/timezone.
    """
    try:
        if not date:
            tz_current = pytz.timezone(zone)
            now = datetime.datetime.now(tz_current)
            date = now.strftime("%Y-%m-%d")
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        tz = pytz.timezone(zone)
        dt_local = tz.localize(dt)
        dt_utc = dt_local.astimezone(pytz.utc)
        jd = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
        )
        positions, aspects = _compute_positions_and_aspects(jd, 0.0, 0.0)
        return {
            "date": date,
            "time": time,
            "zone": zone,
            "positions": positions,
            "aspects": aspects,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/natal")
def natal(date: str, time: str, zone: str, lat: float, lon: float):
    """
    Calculate natal chart positions, including planets, Ascendant and Midheaven, and aspects for the given birth data.
    """
    try:
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        tz = pytz.timezone(zone)
        dt_local = tz.localize(dt)
        dt_utc = dt_local.astimezone(pytz.utc)
        jd = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
        )
        positions, aspects = _compute_positions_and_aspects(jd, lat, lon)
        return {
            "date": date,
            "time": time,
            "zone": zone,
            "lat": lat,
            "lon": lon,
            "positions": positions,
            "aspects": aspects,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# expose `api` for uvicorn
api = app
