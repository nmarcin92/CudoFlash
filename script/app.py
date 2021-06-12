from flask import Flask, request
from flask_cors import CORS, cross_origin

import random


class Furnace:
    expected = 56.0

    def step(self):
        print("Simulation step...")

    def current_parameters(self):
        total = self.expected * (random.random() * 0.7 + 0.35)
        return {
            "total": total,
            "s100": total/6.0 * (random.random() * 0.3 + 0.85),
            "s200": total/6.0 * (random.random() * 0.3 + 0.85),
            "s300": total/6.0 * (random.random() * 0.3 + 0.85),
            "s400": total/6.0 * (random.random() * 0.3 + 0.85),
            "s500": total/6.0 * (random.random() * 0.3 + 0.85),
            "s600": total/6.0 * (random.random() * 0.3 + 0.85)
        }

class AppDefinition:

    def __init__(self):
        self.app = Flask(__name__)
        self.cors = CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self.furnace = Furnace()


app = AppDefinition()


@app.app.route("/expectedValue", methods=["GET", "POST"])
@cross_origin()
def desired_value():
    if request.method == "GET":
        return {"value": app.furnace.expected}
    elif request.method == "POST":
        app.furnace.expected = float(request.json["value"])


@app.app.route("/current")
@cross_origin()
def current():
    return app.furnace.current_parameters()


if __name__ == "__main__":
    app.app.run(host="0.0.0.0", port=2137)