from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
import datetime

app = Flask(__name__)
CORS(app)  # ✅ FIX: allow frontend requests

# Ephemeris path
swe.set_ephe_path('.')

# Vedic (Lahiri)
swe.set_sid_mode(swe.SIDM_LAHIRI)
FLAGS = swe.FLG_SIDEREAL


# ✅ Health check (optional but useful)
@app.route('/')
def home():
    return "Backend Running"


@app.route('/api/kundali', methods=['POST'])
def kundali():
    try:
        dob = request.form.get("dob")
        time = request.form.get("birth_time")

        if not dob or not time:
            return jsonify({"error": "missing data"})

        # Parse datetime
        try:
            dt = datetime.datetime.strptime(dob + " " + time, "%Y-%m-%d %H:%M:%S")
        except:
            dt = datetime.datetime.strptime(dob + " " + time, "%Y-%m-%d %H:%M")

        # IST → UTC
        dt_utc = dt - datetime.timedelta(hours=5, minutes=30)

        # Julian Day
        jd = swe.julday(
            dt_utc.year,
            dt_utc.month,
            dt_utc.day,
            dt_utc.hour + dt_utc.minute / 60.0
        )

        # Planets (SIDEREAL)
        planets = {
            "sun": swe.calc_ut(jd, swe.SUN, FLAGS)[0][0],
            "moon": swe.calc_ut(jd, swe.MOON, FLAGS)[0][0],
            "mars": swe.calc_ut(jd, swe.MARS, FLAGS)[0][0],
            "mercury": swe.calc_ut(jd, swe.MERCURY, FLAGS)[0][0],
            "jupiter": swe.calc_ut(jd, swe.JUPITER, FLAGS)[0][0],
            "venus": swe.calc_ut(jd, swe.VENUS, FLAGS)[0][0],
            "saturn": swe.calc_ut(jd, swe.SATURN, FLAGS)[0][0],
        }

        # Rahu / Ketu
        rahu = swe.calc_ut(jd, swe.MEAN_NODE, FLAGS)[0][0]
        ketu = (rahu + 180) % 360

        planets["rahu"] = rahu
        planets["ketu"] = ketu

        # Location (Pune for now)
        lat = 18.5204
        lon = 73.8567

       cusps, ascmc = swe.houses_ex(
    jd,
    lat,
    lon,
    b'P',
    swe.FLG_SIDEREAL
)

lagna = ascmc[0]

        return jsonify({
            "lagna": lagna,
            "planets": planets
        })

    except Exception as e:
        return jsonify({"error": str(e)})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=10000)
