import math
# average_fuel_consumption 	= 0.003923 l/s # this is highly relative, but good
# estimates are 36-40l/min = 28-31kg/min = 0.47-0.52kg/s
# -- 45l/min = 35kg/min = 0.583kg/s


FUEL_VOLUMIC_MASS = 0.803  # kg / l
KNOTS2KMH = 1.852  # knots to km/h
KMH2KNOTS = 0.539957  # km/h to knots


# For ULM : 140 is optimal speed so let's say 50%
# 180 is 75% engine speed
# 200 is 100% engine speed

class Plane:
    def __init__(self, name: str = 'ULM',
                 fuel_consumption_rate: float = 0.0024791,
                 fuel_max: int = 130,  V_min: float = 100,
                 V_OPT: float = 140, V_3Quarter: float = 180,
                 V_max: float = 200, MINALTITUDE: int = 300,
                 MAXALTITUDE: int = 16500):

        self.name = name
        self.fuel_consumption_rate = fuel_consumption_rate  # l/s

        self.fuel_max = fuel_max  # Liters

        self.V_OPT = V_OPT  # Optimal speed in km/h
        self.V_3Quarter = V_3Quarter
        self.MAXSPEED = V_max  # Max speed in km/h
        self.MINSPEED = V_min
        # self.V_OPT = round(self.V_Opt_kmh * KMH2KNOTS)
        # self.V_3Quarter = round(self.V_3Quarter_kmh * KMH2KNOTS)
        # self.V_max = round(self.V_max_kmh * KMH2KNOTS)

        # TODO
        self.MINALTITUDE = MINALTITUDE  # feet :
        # will be set with the type of terrain
        self.MAXALTITUDE = MAXALTITUDE  # feet

        self.max_flight_time = round(
            self.fuel_max / self.fuel_consumption_rate)
        print("Cet avion peut voler pendant ",
              self.max_flight_time,
              " s, soit ",
              math.floor(self.max_flight_time / 60),
              " min, soit",
              round((self.max_flight_time / 3600) * self.V_OPT),
              " km à une vitesse moyenne de ",
              self.V_OPT,
              " km/h et sa vitesse max sera de ",
              self.MAXSPEED,
              " km/h")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # Get consumption rate in kg/s

    def get_consumption_rate(self, speed: float) -> float:
        # Speed in m/s
        return self.fuel_consumption_rate * speed / (
                self.V_OPT ** 0.95
                )


ULM = Plane()
