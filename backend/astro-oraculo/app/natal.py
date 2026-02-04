from fastapi.middleware.cors import CORSMiddleware

from fastapi import HTTPException
import datetime
import pytz
import os
import swisseph as swe
# Remove existing /natal GET route from astro_main if defined
for route in list(app.router.routes):
    if getattr(route, "path", None) == "/natal" and "GET" in getattr(route, "methods", {}):
        app.router.routes.remove(route)

# Import the existing app from astro_main (with daily endpoints)
from .astro_m"""
FastAPI module for calculating natal charts with planetary positions, Ascendant,
Midheaven, and the major aspects. This module does not depend on the rest of
astro_oraculo_api codebase and can be used as a standalone ASGI app or
integrated into an existing FastAPI application.

The endpoint `/natal-chart` expects the following query parameters:

* `date` (YYYY-MM-DD): Date of birth.
* `time` (HH:MM): Time of birth (24h format).
* `zone`: IANA timezone string (e.g. `America/Argentina/Buenos_Aires`).
* `lat`: Geographic latitude of the birthplace in decimal degrees (positive
  for north, negative for south).
* `lon`: Geographic longitude of the birthplace in decimal degrees (positive
  for east, negative for west).

It returns a JSON structure with the normalized longitude, zodiac sign, and
degree within the sign for each planet, plus the Ascendant and Midheaven,
and a list of aspects computed using the standard orbs defined below.

The aspect calculation includes: conjunction, sextile, square, trine, and
opposition. Conjunctions and oppositions use an 8° orb; the other aspects use
a 6° orb. Ascendant and Midheaven are treated like planets for aspect
purposes.

This module is designed to be easy to integrate: simply run it with Uvicorn
(`uvicorn natal_chart_module:api`) or mount the `api` variable in your
application. It sets up CORS to allow requests from any origin, making it
suitable for local development and browser-based clients.

Example usage:

    uvicorn natal_chart_module:api --reload

Then visit:

    http://localhost:8000/natal-chart?date=1982-04-12&time=02:30&zone=America/Argentina/Buenos_Aires&lat=-34.566&lon=-59.1

"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import datetime
import pytz
import os
import swisseph as swe

# Create a new FastAPI app instead of reusing the app from astro_main.
app = FastAPI()

# Enable CORS for all origins (for development and browser-based clients).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the path to the Swiss ephemeris files. You can override this path using
# the EPHE_PATH environment variable. In a deployed environment on Render, the
# ephemeris files should be stored under `/app/ephe` and EPHE_PATH should be
# set accordingly.
swe.set_ephe_path(os.getenv("EPHE_PATH", "/app/ephe"))

# Define the aspect types and their angle/orb in degrees. The key is the
# aspect name, and the value is a tuple of (exact_angle, orb).
ASPECT_TYPES = {
    "conjunction": (0, 8),
    "sextile": (60, 6),
    "square": (90, 6),
    "trine": (120, 6),
    "opposition": (180, 8),
}

# Mapping of planets to their Swiss ephemeris IDs.
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

# Zodiac signs in order. The index of the sign corresponds to the integer
# division of the longitude by 30.
SIGNS = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]


def _angle_diff(a1: float, a2: float) -> float:
    """Return the minimal difference between two angles in degrees."""
    diff = abs(a1 - a2) % 360
    return min(diff, 360 - diff)


@app.get("/natal-chart")
def natal_chart(
    date: str,
    time: str,
    zone: str,
    lat: float,
    lon: float,
):
    """
    Compute the natal chart for a given birth date, time, timezone, latitude,
    and longitude.

    Parameters:
        date: Date of birth (YYYY-MM-DD).
        time: Time of birth (HH:MM) in 24-hour format.
        zone: Timezone (IANA format, e.g. "America/Argentina/Buenos_Aires").
        lat: Latitude of birth place in decimal degrees (north positive).
        lon: Longitude of birth place in decimal degrees (east positive).

    Returns a JSON object containing the planetary positions, Ascendant,
    Midheaven, and aspects with orbs. If parsing fails or any error occurs,
    a 400 HTTP error is returned with the exception message.
    """
    try:
        # Parse the date and time into a datetime object
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        # Localize to the provided timezone
        tz = pytz.timezone(zone)
        dt_local = tz.localize(dt)
        # Convert to UTC for Swiss ephemeris
        dt_utc = dt_local.astimezone(pytz.utc)
        # Compute Julian day number for the given datetime
        jd = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
        )

        # Compute planetary positions
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

        # Compute Ascendant (ASC) and Midheaven (MC) using provided lat/lon
        # swe.houses returns (cusps, ascmc), where ascmc[0] = Ascendant,
        # ascmc[1] = Midheaven (MC). lat and lon are in degrees.
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

        # Compute aspects between all pairs of positions
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

# Configure CORS

# Remove existing /natal GET route from astro_main if defined
for route in list(app.router.routes):
    if getattr(route, "path", None) == "/natal" and "GET" in getattr(route, "methods", {}):
        app.router.routes.remove(route)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set the ephemeris path
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
    diff = abs(a1 - a2) % 360
    return diff if diff <= 180 else 360 - diff

@app.get("/natal")
def natal_chart(date: str, time: str, zone: str, lat: float, lon: float):
    """Return natal chart planetary positions, ascendant, midheaven and aspects for the given date, time and location."""
    try:
        # Parse date and time with timezone
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

        # Compute planetary positions
        positions = {}
        for name, pid in PLANET_IDS.items():
            result, _ = swe.calc_ut(jd, pid)
            lon_deg = result[0] % 360
            sign_index = int(lon_deg // 30)
            positions[name] = {
                "longitude": lon_deg,
                "sign": SIGNS[sign_index],
                "degree": lon_deg % 30,
            }

        # Compute houses to get Ascendant and Midheaven
        cusps, ascmc = swe.houses(jd, lat, lon)
        asc_lon = ascmc[0] % 360
        mc_lon = ascmc[1] % 360
        for label, lon_value in [("Ascendant", asc_lon), ("Midheaven", mc_lon)]:
            idx = int(lon_value // 30)
            positions[label] = {
                "longitude": lon_value,
                "sign": SIGNS[idx],
                "degree": lon_value % 30,
            }

        # Compute aspects
        aspects = []
        names = list(positions.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a1 = positions[names[i]]["longitude"]
                a2 = positions[names[j]]["longitude"]
                diff = _angle_diff(a1, a2)
                for aspect, (angle, orb) in ASPECT_TYPES.items():
                    if abs(diff - angle) <= orb:
                        aspects.append({
                            "planet1": names[i],
                            "planet2": names[j],
                            "aspect": aspect,
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

# Expose the FastAPI app for uvicorn
api = app
