from flask import Flask, request
from flask_cors import CORS, cross_origin

from script.model import Furnace


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