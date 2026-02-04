"""
Unified FastAPI application providing endpoints for daily transits, natal charts,
comparison endpoints (transit vs natal, synastry, transit vs transit),
and aspects using Swiss Ephemeris.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import datetime
import pytz
import os
import swisseph as swe

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

# Set Swiss ephemeris path
swe.set_ephe_path(os.getenv("EPHE_PATH", "/app/ephe"))

# Aspect definitions: exact angle and orb
ASPECT_TYPES = {
    "conjunction": (0, 8),
    "sextile": (60, 6),
    "square": (90, 6),
    "trine": (120, 6),
    "opposition": (180, 8),
}

# Planet IDs
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
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _angle_diff(a1: float, a2: float) -> float:
    diff = abs(a1 - a2) % 360
    return min(diff, 360 - diff)


def _compute_positions_and_aspects(jd: float, lat: float, lon: float):
    positions = {}
    for name, pid in PLANET_IDS.items():
        result, _ = swe.calc_ut(jd, pid)
        lon_deg = result[0] % 360
        positions[name] = {
            "longitude": lon_deg,
            "sign": SIGNS[int(lon_deg // 30)],
            "degree": lon_deg % 30,
        }
    # Ascendant and Midheaven
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
    aspects = []
    names = list(positions.keys())
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            lon1 = positions[names[i]]["longitude"]
            lon2 = positions[names[j]]["longitude"]
            diff = _angle_diff(lon1, lon2)
            for aspect, (angle, orb) in ASPECT_TYPES.items():
                if abs(diff - angle) <= orb:
                    aspects.append({
                        "planet1": names[i],
                        "planet2": names[j],
                        "aspect": aspect,
                        "orb": round(abs(diff - angle), 2),
                    })
                    break
    return positions, aspects


@app.get("/")
def root():
    return {"message": "Astro Oraculo API is running"}


@app.get("/transits/daily")
def daily_transits(date: str = None, time: str = "12:00", zone: str = "UTC"):
    """Positions and aspects for a given date/time using lat/lon = 0."""
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
    """Natal chart positions and aspects for given birth data."""
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


# Comparison helper functions

def _jd_from_local(date: str, time: str, zone: str) -> float:
    dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    tz = pytz.timezone(zone)
    dt_local = tz.localize(dt)
    dt_utc = dt_local.astimezone(pytz.utc)
    return swe.julday(
        dt_utc.year,
        dt_utc.month,
        dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
    )


def _positions_for(jd: float, lat: float, lon: float):
    positions = {}
    for name, pid in PLANET_IDS.items():
        result, _ = swe.calc_ut(jd, pid)
        lon_deg = result[0] % 360
        positions[name] = {
            "longitude": lon_deg,
            "sign": SIGNS[int(lon_deg // 30)],
            "degree": lon_deg % 30,
        }
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
    return positions


def _cross_aspects(posA: dict, posB: dict):
    pairs = []
    for a_name, a in posA.items():
        for b_name, b in posB.items():
            if a_name == b_name and posA is posB:
                continue
            diff = _angle_diff(a["longitude"], b["longitude"])
            for aspect, (angle, orb) in ASPECT_TYPES.items():
                if abs(diff - angle) <= orb:
                    pairs.append({
                        "from": a_name,
                        "to": b_name,
                        "aspect": aspect,
                        "orb": round(abs(diff - angle), 2),
                    })
                    break
    return pairs


@app.get("/compare/transit-against-natal")
def compare_transit_against_natal(
    t_date: str, t_time: str, t_zone: str,
    n_date: str, n_time: str, n_zone: str, n_lat: float, n_lon: float
):
    jd_t = _jd_from_local(t_date, t_time, t_zone)
    pos_t = _positions_for(jd_t, 0.0, 0.0)
    jd_n = _jd_from_local(n_date, n_time, n_zone)
    pos_n = _positions_for(jd_n, n_lat, n_lon)
    aspects = _cross_aspects(pos_t, pos_n)
    return {
        "transit": {"date": t_date, "time": t_time, "zone": t_zone, "positions": pos_t},
        "natal": {
            "date": n_date,
            "time": n_time,
            "zone": n_zone,
            "lat": n_lat,
            "lon": n_lon,
            "positions": pos_n,
        },
        "aspects": aspects,
    }


@app.get("/compare/synastry")
def compare_synastry(
    a_date: str, a_time: str, a_zone: str, a_lat: float, a_lon: float,
    b_date: str, b_time: str, b_zone: str, b_lat: float, b_lon: float
):
    jd_a = _jd_from_local(a_date, a_time, a_zone)
    pos_a = _positions_for(jd_a, a_lat, a_lon)
    jd_b = _jd_from_local(b_date, b_time, b_zone)
    pos_b = _positions_for(jd_b, b_lat, b_lon)
    aspects = _cross_aspects(pos_a, pos_b)
    return {
        "chartA": {
            "date": a_date,
            "time": a_time,
            "zone": a_zone,
            "lat": a_lat,
            "lon": a_lon,
            "positions": pos_a,
        },
        "chartB": {
            "date": b_date,
            "time": b_time,
            "zone": b_zone,
            "lat": b_lat,
            "lon": b_lon,
            "positions": pos_b,
        },
        "aspects": aspects,
    }


@app.get("/compare/transit-vs-transit")
def compare_transit_vs_transit(
    a_date: str, a_time: str, a_zone: str,
    b_date: str, b_time: str, b_zone: str
):
    jd_a = _jd_from_local(a_date, a_time, a_zone)
    pos_a = _positions_for(jd_a, 0.0, 0.0)
    jd_b = _jd_from_local(b_date, b_time, b_zone)
    pos_b = _positions_for(jd_b, 0.0, 0.0)
    aspects = _cross_aspects(pos_a, pos_b)
    return {
        "transitA": {"date": a_date, "time": a_time, "zone": a_zone, "positions": pos_a},
        "transitB": {"date": b_date, "time": b_time, "zone": b_zone, "positions": pos_b},
        "aspects": aspects,
    }


# Expose api for uvicorn
api = app

