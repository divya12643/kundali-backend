from flask import Flask, request, jsonify
from flask_cors import CORS
import swisseph as swe
import datetime

app = Flask(__name__)
CORS(app)

swe.set_ephe_path('.')

@app.route('/')
def home():
    return "Kundali API running"

@app.route('/api/kundali', methods=['POST'])
def kundali():

    dob = request.form.get("dob")
    time = request.form.get("birth_time")

    if not dob or not time:
        return jsonify({"error": "missing data"})

    # ✅ FIXED TIME PARSE
    try:
        dt = datetime.datetime.strptime(dob + " " + time, "%Y-%m-%d %H:%M:%S")
    except:
        dt = datetime.datetime.strptime(dob + " " + time, "%Y-%m-%d %H:%M")

    jd = swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

    planets = {
        "sun": swe.calc_ut(jd, swe.SUN)[0][0],
        "moon": swe.calc_ut(jd, swe.MOON)[0][0],
        "mars": swe.calc_ut(jd, swe.MARS)[0][0],
        "mercury": swe.calc_ut(jd, swe.MERCURY)[0][0],
        "jupiter": swe.calc_ut(jd, swe.JUPITER)[0][0],
        "venus": swe.calc_ut(jd, swe.VENUS)[0][0],
        "saturn": swe.calc_ut(jd, swe.SATURN)[0][0],
    }

    rahu = swe.calc_ut(jd, swe.MEAN_NODE)[0][0]
    ketu = (rahu + 180) % 360

    planets["rahu"] = rahu
    planets["ketu"] = ketu

    # Pune (temporary fixed location)
    lat = 18.5204
    lon = 73.8567

    houses = swe.houses(jd, lat, lon)

    # ✅ RETURN DEGREE (IMPORTANT)
    lagna = houses[0][0]

    return jsonify({
        "lagna": lagna,
        "planets": planets
    })

if __name__ == "__main__":
    app.run()
