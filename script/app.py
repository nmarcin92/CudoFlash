from flask import Flask, request
from flask_cors import CORS, cross_origin
import random

class Piec:
    expected = 56.0

    def current(self):
        total = self.expected * (random.random() * 0.3 + 0.85)
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
        self.piec = Piec()


app = AppDefinition()


@app.app.route("/expectedValue", methods=["GET", "POST"])
@cross_origin()
def desired_value():
    if request.method == "GET":
        return {"value": app.piec.expected}
    elif request.method == "POST":
        app.piec.expected = float(request.json["value"])


@app.app.route("/current")
@cross_origin()
def current():
    return app.piec.current()


if __name__ == "__main__":
    app.app.run(host="0.0.0.0", port=2137)