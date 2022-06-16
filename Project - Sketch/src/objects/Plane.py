from function.tools import KNOTS2KMH, KMH2KNOTS

# average_fuel_consumption 	= 0.302 # this is highly relative, but good
# estimates are 36-40l/min = 28-31kg/min = 0.47-0.52kg/s
# -- 45l/min = 35kg/min = 0.583kg/s


class Plane:
    def __init__(self, name: str = 'ULM',
                 fuel_consumption_rate: float = 0.11,
                 fuel_max: int = 130, V_OPT: int = 81, V_max: int = 108):

        self.name = name
        self.fuel_consumption_rate = fuel_consumption_rate
        self.fuel_max = fuel_max

        self.V_OPT = V_OPT  # Optimal speed in knots
        self.V_max = V_max  # Max speed in knots
        self.V_Opt_kmh = round(self.V_OPT * KNOTS2KMH)
        self.V_max_kmh = round(self.V_max * KNOTS2KMH)

        self.max_flight_time = round(
            self.fuel_max / self.fuel_consumption_rate)
        print("Cet avion peut voler pendant ", self.max_flight_time,
              " s, soit ", round(self.max_flight_time / 60),
              " min à une vitesse moyenne de ",
              self.V_Opt_kmh,
              " km/h et sa vitesse max sera de ",
              self.V_max_kmh,
              " km/h")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_consumption_rate(self, speed: float) -> float:
        return self.fuel_consumption_rate * speed / self.V_Opt_kmh
