from fastapi import FastAPI, HTTPException
import os
import datetime
import swisseph as swe
import pytz

# Initialize FastAPI app
app = FastAPI(title="Astro Oraculo API")
api = app

# Set path to Swiss ephemeris files from environment variable if provided
ephe_path = os.getenv("EPHE_PATH")
if ephe_path:
    swe.set_ephe_path(ephe_path)

@app.get("/")
def root():
    """Root endpoint to confirm the API is running."""
    return {"message": "Astro oráculo API is running"}

@app.get("/transits/daily")
def daily_transits(date: str = None, time: str = "12:00", zone: str = "UTC"):
    """Return planetary positions for a given date and time."""
    try:
        # If date not provided, use current date in given timezone
        if date is None:
            tz = pytz.timezone(zone)
            now = datetime.datetime.now(tz)
            date = now.strftime("%Y-%m-%d")

        # Parse the input date and time
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        # Localize to the specified timezone
        tz = pytz.timezone(zone)
        dt_local = tz.localize(dt)
        # Convert to UTC for Swiss Ephemeris
        dt_utc = dt_local.astimezone(pytz.utc)
        # Calculate Julian day
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day,
                        dt_utc.hour + dt_utc.minute/60.0 + dt_utc.second/3600.0)

        # Define planets to calculate
        planet_ids = {
            "Sun": swe.SUN,
            "Moon": swe.MOON,
            "Mercury": swe.MERCURY,
            "Venus": swe.VENUS,
            "Mars": swe.MARS,
            "Jupiter": swe.JUPITER,
            "Saturn": swe.SATURN,
            "Uranus": swe.URANUS,
            "Neptune": swe.NEPTUNE,
            "Pluto": swe.PLUTO
        }
        # Names of zodiac signs
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
            "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
        ]
        positions = {}
        for name, pid in planet_ids.items():
            result, _ = swe.calc_ut(jd, pid)
            lon = result[0] % 360  # longitude in degrees
            sign_index = int(lon // 30)
            deg_in_sign = lon % 30
            positions[name] = {
                "longitude": lon,
                "sign": signs[sign_index],
                "degree": deg_in_sign
            }

        return {
            "date": date,
            "time": time,
            "zone": zone,
            "positions": positions
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/natal")
def natal_chart():
    """
    Placeholder endpoint for natal chart calculations.
    It should accept birth details and return positions and aspects.
    """
    # TODO: implement natal chart computation using Swiss Ephemeris
    return {"message": "natal endpoint placeholder"}

@app.post("/oraculo/lectura")
def oraculo_lectura():
    """
    Placeholder endpoint for generating oracular readings based on astrological data.
    It should map positions and aspects to tarot cards using CSV correspondences.
    """
    # TODO: implement oracular reading logic

    return {"message": "oráculo lectura endpoint placeholder"}


@app.get("/transits/daily/full")
def daily_transits_full(date: str = None, time: str = "12:00", zone: str = "UTC"):
    """Return planetary positions and aspects for a given date and time, including Ascendant and Midheaven."""
    try:
        # If date is None: use the current date in the specified timezone
        if date is None:
            tz_current = pytz.timezone(zone)
            now = datetime.datetime.now(tz_current)
            date = now.strftime("%Y-%m-%d")
        # Parse date/time
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        tz = pytz.timezone(zone)
        dt_local = tz.localize(dt)
        # Convert to UTC for Swiss ephemeris
        dt_utc = dt_local.astimezone(pytz.utc)
        # Calculate Julian day
        jd = swe.julday(
            dt_utc.year, dt_utc.month, dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
        )

        # Planet IDs
        planet_ids = {
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
        signs = [
            "Aries", "Taurus", "Gemini", "Cancer",
            "Leo", "Virgo", "Libra", "Scorpio",
            "Sagittarius", "Capricorn", "Aquarius", "Pisces",
        ]

        # Planet positions
        positions = {}
        for name, pid in planet_ids.items():
            lon, _ = swe.calc_ut(jd, pid)
            lon = lon % 360
            sign_index = int(lon // 30)
            deg_in_sign = lon % 30
            positions[name] = {
                "longitude": lon,
                "sign": signs[sign_index],
                "degree": deg_in_sign,
            }

        # Ascendant and Midheaven using houses (0 lat & lon)
        cusps, ascmc = swe.houses(jd, 0.0, 0.0)
        asc_lon = ascmc[0] % 360
        mc_lon = ascmc[1] % 360
        for label, lon_val in [("Ascendant", asc_lon), ("Midheaven", mc_lon)]:
            sign_index = int(lon_val // 30)
            positions[label] = {
                "longitude": lon_val,
                "sign": signs[sign_index],
                "degree": lon_val % 30,
            }

        # Define aspects and orbs
        aspect_types = {
            "conjunction": (0, 8),
            "sextile": (60, 6),
            "square": (90, 6),
            "trine": (120, 6),
            "opposition": (180, 8),
        }

        def ang_diff(a1, a2):
            diff = abs(a1 - a2) % 360
            return min(diff, 360 - diff)

        # Compute aspects between all pairs including Asc & MC
        aspects = []
        names = list(positions.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a1 = positions[names[i]]["longitude"]
                a2 = positions[names[j]]["longitude"]
                d = ang_diff(a1, a2)
                for aspect, (angle, orb) in aspect_types.items():
                    if abs(d - angle) <= orb:
                        aspects.append({
                            "planet1": names[i],
                            "planet2": names[j],
                            "aspect": aspect,
                            "orb": round(abs(d - angle), 2),
                        })
                        break

        return {
            "date": date,
            "time": time,
            "zone": zone,
            "positions": positions,
            "aspects": aspects,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
