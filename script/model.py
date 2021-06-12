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