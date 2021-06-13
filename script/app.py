import time

from flask import Flask, request
from flask_cors import CORS, cross_origin
from tensorflow import keras
import numpy as np
import os

import threading

MODEL_PATH = "/opt/app/models/rnn"
#MODEL_PATH = "/home/mnowak/PycharmProjects/CudoFlash/models/rnn"

POW_DYST_NORM = {"min": 1900.,"max": 3500.} #
ZAW_TLE_NORM = {"min": 65., "max": 81.}     #
PRE_DMU = { "min": 40.,"max": 70.}          #
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

    expected = 22.0


    def state_vector(self, current_values = None):
        if current_values:
            v = np.array([self.params[3:] + current_values + self.current + self.future])
        else:
            v = np.array([self.params + self.current + self.future])
        v = v[:, :-1]
        v = v.reshape((v.shape[0], 1, v.shape[1]))
        return v

    def initialize(self):
        print("initializing...")
        print(f"model found: {os.path.exists(MODEL_PATH)}")
        self.model = keras.models.load_model(MODEL_PATH)
        threading.Thread(target=self.simulation_start).start()
        print ("Model initialized")

    def normalize(self, value):
        return (value - STR_LAC["min"]) / (STR_LAC["max"] - STR_LAC["min"])

    def denormalize(self, value):
        return value * (STR_LAC["max"] - STR_LAC["min"]) + STR_LAC["min"]

    def current_set_values(self):
        return self.params[-3:]

    def current_set_values_normalized(self):
        v = self.params[-3:]
        return [
            v[0] * (POW_DYST_NORM["max"] - POW_DYST_NORM["min"]) + POW_DYST_NORM["min"],
            v[1] * (ZAW_TLE_NORM["max"] - ZAW_TLE_NORM["min"]) + ZAW_TLE_NORM["min"],
            v[2] * (PRE_DMU["max"] - PRE_DMU["min"]) + PRE_DMU["min"]
        ]

    def set_values(self, new_values):
        print(f"Setting values from {self.params[-3:]} to {new_values}")
        self.params = self.params[3:] + list(new_values)

    def ml(self, x, y, z):
        state = self.state_vector([x, y, z])
        return self.model.predict(state)[0][0]

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
        print("Simulation thread initialized")
        while True:
            print(f"Simulation step; running: {self.running}")
            if self.running:
                self.step()
            print("Sleeping")
            try:
                time.sleep(5)
            except Exception as e:
                print ("ERROR")
                print (e)
            print("Waked up")

    def start_sim(self):
        self.running = True

    def stop_sim(self):
        self.running = False

    def current_parameters(self):
        total = self.denormalize(self.current[-1])
        return {
            "total": total,
            "s100": total * 0.317766301022455,
            "s300": total * 0.32312964196620214,
            "s500": total * 0.27303963791770425,
            "s600": total * 0.08606441909363872
        }

##################################################

import random
import math



class Controller:
    def __init__(self, furnace):
        self.furnace = furnace

    max_zmiana_powietrza = 0.1
    max_zmiana_tlenu = 0.1
    max_zmiana_podmuch = 0.1

    def initialize(self):
        threading.Thread(target=self.controller_start).start()

    def controller_start(self):
        while True:
            print("Controller step")
            time.sleep(4)

            if self.furnace.running:
                current_set_values = self.furnace.current_set_values()
                new_params = self.simulated_annealing(current_set_values[0], current_set_values[1], current_set_values[2])
                self.furnace.set_values(new_params)

    def wartosc_oczekiwana(self):
        return self.furnace.normalize(self.furnace.expected)

    # Przyjmuje nastaw i zwraca jaka dla nich wystąpi strata
    def ml(self, x, y, z):
        return self.furnace.ml(x, y, z)

    def random_sign(self):
        return 1 if random.random() < 0.5 else -1

    def get_cost(self, x):
        return (self.wartosc_oczekiwana() - x) ** 2


    def safe_val(self, v):
        return max(min(v, 1.0), 0.0)

    # X - Przepływ powietrza
    # Y - Zakres tlenu
    # Z - Predkosc dmuchu
    def get_random_neighbor(self, current_temp, currentX, currentY, currentZ):
        temp = current_temp / 100
        x = currentX + self.random_sign() * (random.random() * temp) * self.max_zmiana_powietrza
        y = currentY + self.random_sign() * (random.random() * temp) * self.max_zmiana_tlenu
        z = currentZ + self.random_sign() * (random.random() * temp) * self.max_zmiana_podmuch

        return (self.safe_val(x), self.safe_val(y), self.safe_val(z))

    def simulated_annealing(self, initX, initY, initZ):
        """Peforms simulated annealing to find a solution"""
        initial_temp = 90.0
        final_temp = .1
        alpha = 2.0

        current_temp = initial_temp

        # Start by initializing the current state with the initial state
        currentX = initX
        currentY = initY
        currentZ = initZ

        solution = (currentX, currentY, currentZ)
        initial_cost = self.get_cost(self.ml(currentX, currentY, currentZ))
        current_cost = initial_cost
        expected = 0

        print("Started sim an")
        while current_temp > final_temp:
            neighbor = self.get_random_neighbor(current_temp, currentX, currentY, currentZ)

            # Check if neighbor is best so far
            ml = self.ml(neighbor[0], neighbor[1], neighbor[2])
            new_cost = self.get_cost(ml)

            # if the new solution is better, accept it
            if new_cost < current_cost:
                print (new_cost)
                solution = neighbor
                current_cost = new_cost
                expected = ml
            # if the new solution is not better, accept it with a probability of e^(-cost/temp)
            else:
                if False and random.uniform(0, 1) < math.exp(-new_cost / current_temp):
                    solution = neighbor
                    current_cost = new_cost
                    expected = ml
            # decrement the temperature
            current_temp -= alpha
            # print(solution)
        print (f"SimAn done, expected: {expected}, wanted: {self.wartosc_oczekiwana()}")
        if current_cost < initial_cost:
            print("changed")
            return solution
        else:
            print("not changed")
            return (initX, initY, initZ)


###################################################


class AppDefinition:

    def __init__(self):
        self.app = Flask(__name__)
        self.cors = CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self.furnace = Furnace()
        self.furnace.initialize()
        self.controller = Controller(self.furnace)
        self.controller.initialize()


app = AppDefinition()


@app.app.route("/expectedValue", methods=["GET", "POST"])
@cross_origin()
def desired_value():
    if request.method == "GET":
        return {"value": app.furnace.expected}
    elif request.method == "POST":
        app.furnace.expected = float(request.json["value"])
        return {}


@app.app.route("/current")
@cross_origin()
def current():
    return app.furnace.current_parameters()


@app.app.route("/currentSetValues")
@cross_origin()
def current_set_values():
    return {"values": app.furnace.current_set_values_normalized()}


@app.app.route("/start/<expected>")
@cross_origin()
def start(expected):
    print(f"Setting expected to {expected}")
    app.furnace.expected = float(expected)
    app.furnace.start_sim()
    return {}


@app.app.route("/stop")
@cross_origin()
def stop():
    app.furnace.stop_sim()
    return {}



if __name__ == "__main__":
    app.app.run(host="0.0.0.0", port=2137)
