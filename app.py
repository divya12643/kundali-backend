from flask import Flask, request, jsonify
import swisseph as swe
import datetime

app = Flask(__name__)

swe.set_ephe_path('.')

@app.route('/api/kundali', methods=['POST'])
def kundali():

    dob = request.form.get("dob")
    time = request.form.get("birth_time")

    if not dob or not time:
        return jsonify({"error": "missing data"})

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

    houses = swe.houses(jd, 18.5204, 73.8567)
    lagna = int(houses[0][0] / 30) + 1

    return jsonify({
        "lagna": lagna,
        "planets": planets
    })

app.run(host='0.0.0.0', port=10000)
