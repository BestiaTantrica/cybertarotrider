from fastapi import FastAPI, HTTPException
import os
import datetime
import pytz
import swisseph as swe

app = FastAPI()
api = app

# Set Swiss ephemeris path from environment
EPHE_PATH = os.getenv("EPHE_PATH")
if EPHE_PATH:
    swe.set_ephe_path(EPHE_PATH)

@app.get("/")
def root():
    return {"message": "Astro oráculo API is running"}

@app.get("/transits/daily")
def daily_transits(date: str = None, time: str = "12:00", zone: str = "UTC"):
    """Return planetary positions, including Ascendant & Midheaven, and major aspects for the given date/time/zone."""
    try:
        # Default to current date if not provided
        if date is None:
            tz_current = pytz.timezone(zone)
            now = datetime.datetime.now(tz_current)
            date = now.strftime("%Y-%m-%d")

        # Parse provided date and time
        dt = datetime.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
        tz = pytz.timezone(zone)
        dt_local = tz.localize(dt)
        dt_utc = dt_local.astimezone(pytz.utc)

        # Compute Julian day
        jd = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0,
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
        signs = [
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
        positions = {}

        # Calculate planetary positions
        for name, pid in planet_ids.items():
            result, _ = swe.calc_ut(jd, pid)
            lon = result[0] % 360  # first element is longitude
            sign_index = int(lon // 30)
            positions[name] = {
                "longitude": lon,
                "sign": signs[sign_index],
                "degree": lon % 30,
            }

        # Ascendant and Midheaven (lat=0, lon=0 for general transit)
        cusps, ascmc = swe.houses(jd, 0.0, 0.0)
        asc_lon = ascmc[0] % 360
        mc_lon = ascmc[1] % 360
        for label, lon_value in [("Ascendant", asc_lon), ("Midheaven", mc_lon)]:
            sign_index = int(lon_value // 30)
            positions[label] = {
                "longitude": lon_value,
                "sign": signs[sign_index],
                "degree": lon_value % 30,
            }

        # Define aspect angles and orbs
        aspect_types = {
            "conjunction": (0, 8),
            "sextile": (60, 6),
            "square": (90, 6),
            "trine": (120, 6),
            "opposition": (180, 8),
        }

        def angle_diff(a1, a2):
            diff = abs(a1 - a2) % 360
            return min(diff, 360 - diff)

        aspects = []
        names = list(positions.keys())
        for i in range(len(names)):
            for j in range(i + 1, len(names)):
                a1 = positions[names[i]]["longitude"]
                a2 = positions[names[j]]["longitude"]
                d = angle_diff(a1, a2)
                for asp, (angle, orb) in aspect_types.items():
                    if abs(d - angle) <= orb:
                        aspects.append(
                            {
                                "planet1": names[i],
                                "planet2": names[j],
                                "aspect": asp,
                                "orb": round(abs(d - angle), 2),
                            }
                        )
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


@app.get("/natal")
def natal_chart():
    """Placeholder for natal chart computation."""
    return {"message": "Natal chart endpoint not implemented yet"}


@app.get("/oraculo/lectura")
def oraculo_lectura():
    """Placeholder for oraculo reading."""
    return {"message": "Oraculo lectura endpoint not implemented yet"}
