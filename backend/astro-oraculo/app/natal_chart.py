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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the path to the Swiss ephemeris files
swe.set_ephe_path(os.getenv("EPHE_PATH", "/app/ephe"))

# Aspect definitions: angle and orb in degrees
ASPECT_TYPES = {
    "conjunction": (0, 8),
    "sextile": (60, 6),
    "square": (90, 6),
    "trine": (120, 6),
    "opposition": (180, 8),
}

# Planet IDs for Swiss Ephemeris
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

# Zodiac signs
SIGNS = [
    "Aries","Taurus","Gemini","Cancer","Leo","Virgo",
    "Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces",
]

def _angle_diff(a1: float, a2: float) -> float:
    """Return the minimal difference between two angles in degrees."""
    diff = abs(a1 - a2) % 360
    return min(diff, 360 - diff)

@app.get("/natal")
def natal_chart(date: str, time: str, zone: str, lat: float, lon: float):
    """
    Compute the natal chart for a given birth date, time, timezone, latitude and longitude.
    Returns planetary positions, Ascendant, Midheaven and aspects.
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
        positions = {}
        for name, pid in PLANET_IDS.items():
            result, _ = swe.calc_ut(jd, pid)
            lon_deg = result[0] % 360
            sign_index = int(lon_deg // 30)
            degree = lon_deg % 30
            positions[name] = {
                "longitude": lon_deg,
                "sign": SIGNS[sign_index],
                "degree": degree,
            }
        # Compute Ascendant and Midheaven using provided lat/lon
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
        # Compute aspects
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

# Expose the app under the name `api` so that Uvicorn can find it.
api = app
