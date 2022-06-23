from function.tools import KNOTS2KMH
import math
# average_fuel_consumption 	= 0.003923 l/s # this is highly relative, but good
# estimates are 36-40l/min = 28-31kg/min = 0.47-0.52kg/s
# -- 45l/min = 35kg/min = 0.583kg/s


FUEL_VOLUMIC_MASS = 0.803  # kg / l


# For ULM : 140 is optimal speed so let's say 50%
# 180 is 75% engine speed
# 200 is 100% engine speed

class Plane:
    def __init__(self, name: str = 'ULM',
                 fuel_consumption_rate: float = 0.0024791,
                 fuel_max: int = 130, V_OPT: float = 75,
                 V_3Quarter: float = 97, V_max: float = 107):

        self.name = name
        self.fuel_consumption_rate = fuel_consumption_rate  # l/s
        self.fuel_max = fuel_max  # En litres

        self.V_OPT = V_OPT  # Optimal speed in knots
        self.V_3Quarter = V_3Quarter
        self.V_max = V_max  # Max speed in knots
        self.V_Opt_kmh = round(self.V_OPT * KNOTS2KMH)
        self.V_3Quarter_kmh = round(self.V_3Quarter * KNOTS2KMH)
        self.V_max_kmh = round(self.V_max * KNOTS2KMH)
        self.max_flight_time = round(
            self.fuel_max / self.fuel_consumption_rate)
        print("Cet avion peut voler pendant ",
              self.max_flight_time,
              " s, soit ",
              math.floor(self.max_flight_time / 60),
              " min, soit",
              round((self.max_flight_time / 3600) * self.V_Opt_kmh),
              " km à une vitesse moyenne de ",
              self.V_Opt_kmh,
              " km/h et sa vitesse max sera de ",
              self.V_max_kmh,
              " km/h")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # Get consumption rate in kg/s

    def get_consumption_rate(self, speed: float) -> float:
        # Speed in m/s
        return self.fuel_consumption_rate * speed / (
                self.V_Opt_kmh ** 0.95
                )


ULM = Plane()
