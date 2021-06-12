import time

from flask import Flask, request
from flask_cors import CORS, cross_origin
from tensorflow import keras
import numpy as np

import threading

MODEL_PATH = "/opt/app/models/rnn"
#MODEL_PATH = "/home/mnowak/PycharmProjects/CudoFlash/models/rnn"

STR_LAC = {"min": 15., "max": 30.}

INIT_PARAMS = [0.5, 1., 0.33333333, 0.5, 1.,
             0.33333333, 0.5, 1., 0.33333333, 0.5,
             1., 0.33333333, 0.5, 1., 0.33333333,
             0.5, 1., 0.33333333, 0.5, 1.,
             0.33333333, 0.5, 1., 0.33333333, 0.5,
             1., 0.33333333, 0.5, 1., 0.33333333,
             0.5, 1., 0.33333333, 0.96186441, 1.,
             0.33333333, 0.5942623, 1., 0.33333333, 0.5,
             1., 0.33333333, 0.5, 1., 0.33333333,
             0.5, 1., 0.33333333, 0.5, 1.,
             0.33333333]

INIT_CURRENT = [0.5575735, 0.56391738, 0.56939228, 0.57108478,
             0.57059481, 0.56384293, 0.55546619, 0.54483481, 0.53149288,
             0.51672566, 0.5023793, 0.48594279, 0.4710405, 0.45771648,
             0.44826734, 0.44215476,
               0.50523842]

INIT_FUTURE = [0.49740808, 0.49089683,
        0.47843831, 0.47031688, 0.45894506, 0.45088889, 0.44068171,
        0.43309257, 0.4315533 , 0.43351652, 0.43816345, 0.44536682,
        0.45292717, 0.45602231, 0.45755672]


class Furnace:
    params = INIT_PARAMS
    current = INIT_CURRENT
    future = INIT_FUTURE
    running = False

    expected = 25.0


    def state_vector(self):
        v = np.array([self.params + self.current + self.future])
        v = v[:, :-1]
        v = v.reshape((v.shape[0], 1, v.shape[1]))
        return v

    def initialize(self):
        self.model = keras.models.load_model(MODEL_PATH)
        threading.Thread(target=self.simulation_start).start()
        print ("Model initialized")

    def denormalize(self, value):
        return value * (STR_LAC["max"] - STR_LAC["min"]) + STR_LAC["min"]

    def step(self):
        try:
            state = self.state_vector()
            predicted = self.model.predict(state)[0][0]
            self.current = self.current[1:] + [self.future[0]]
            self.future = self.future[1:] + [predicted]

            print(f"current loss: {self.denormalize(self.current[-1])}")
        except Exception as e:
            print("Simulation step failed")
            print(e)

    def simulation_start(self):
        while True:
            if self.running:
                self.step()
            time.sleep(3)

    def start_sim(self):
        self.running = True

    def stop_sim(self):
        self.running = False

    def current_parameters(self):
        total = self.denormalize(self.current[-1])
        return {
            "total": total,
            "s100": 0,
            "s200": 0,
            "s300": 0,
            "s400": 0,
            "s500": 0,
            "s600": 0
        }


class AppDefinition:

    def __init__(self):
        self.app = Flask(__name__)
        self.cors = CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self.furnace = Furnace()
        self.furnace.initialize()


app = AppDefinition()


@app.app.route("/expectedValue", methods=["GET", "POST"])
@cross_origin()
def desired_value():
    if request.method == "GET":
        return {"value": app.furnace.expected}
    elif request.method == "POST":
        app.furnace.expected = float(request.json["value"])
        return "ok"


@app.app.route("/current")
@cross_origin()
def current():
    return app.furnace.current_parameters()


@app.app.route("/start")
@cross_origin()
def start():
    app.furnace.start_sim()
    return "ok"


@app.app.route("/stop")
@cross_origin()
def stop():
    app.furnace.stop_sim()
    return "ok"



if __name__ == "__main__":
    app.app.run(host="0.0.0.0", port=2137)
