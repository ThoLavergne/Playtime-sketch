import math

# Source ULM:
# https://www.xl8.fr/uploads/files/XL8_plaquette_2014-format_A4_300dpi.pdf
# https://www.xl8.fr/caracteristiques.html
# TODO : change fuel consumption rate
FUEL_VOLUMIC_MASS = 0.803  # kg / l
KNOTS2KMH = 1.852  # knots to km/h
KMH2KNOTS = 0.539957  # km/h to knots


class Plane:
    """This class represent an object plane to use for Playtime prediction
    """
    def __init__(self, name: str = 'ULM',
                 fuel_consumption_rate: float = 0.003,
                 fuel_max: int = 120,  S_min: float = 140,
                 S_OPT: float = 180, S_max: float = 220,
                 MINALTITUDE: int = 300, MAXALTITUDE: int = 16500,
                 verbose: int = 0):
        """Generate Plane object. Default values are ULM parameters.

        Parameters
        ----------
        name : str, optional
            Name of the plane, by default 'ULM'
        fuel_consumption_rate : float, optional
            Consumption rate of the plane (related to S_OPT)
            by default 0.003 (liters/s)
        fuel_max : int, optional
            Tank max capacity, by default 120 (liters)
        S_min : float, optional
            Minimum speed usable in flight, by default 140 (km/h)
        S_OPT : float, optional
            Optimal speed in flight, by default 180 (km/h)
        S_max : float, optional
            Maximum speed usable in flight, by default 220 (km/h)
        MINALTITUDE : int, optional
            Service floor for the plane, by default 300 (feet)
        MAXALTITUDE : int, optional
            Service ceiling for the plane, by default 16500 (feet)
        verbose : int, optional
            Verbose mode, display data for the plane, by default 0 (False)
        """

        self.name = name
        self.fuel_consumption_rate = fuel_consumption_rate  # l/s

        self.fuel_max = fuel_max  # Liters

        self.S_OPT = S_OPT  # Optimal speed in km/h
        self.MAXSPEED = S_max  # Max speed in km/h
        self.MINSPEED = S_min

        # Not used : speed in Knots
        # self.S_OPT = round(self.V_Opt_kmh * KMH2KNOTS)
        # self.V_3Quarter = round(self.V_3Quarter_kmh * KMH2KNOTS)
        # self.S_max = round(self.V_max_kmh * KMH2KNOTS)

        # TODO will be set with the type of field
        self.MINALTITUDE = MINALTITUDE  # feet
        self.MAXALTITUDE = MAXALTITUDE  # feet

        self.max_flight_time = round(
            self.fuel_max / self.fuel_consumption_rate)
        if verbose:
            print("Cet avion peut voler pendant ",
                  self.max_flight_time,
                  " s, soit ",
                  math.floor(self.max_flight_time / 60),
                  " min, soit",
                  round((self.max_flight_time / 3600) * self.S_OPT),
                  " km à une vitesse moyenne de ",
                  self.S_OPT,
                  " km/h et sa vitesse max sera de ",
                  self.MAXSPEED,
                  " km/h")

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_consumption_rate(self, speed: float) -> float:
        """Get consumption rate depending on speed for the current plane.
        TODO Convert using data from src/test_conso.ipynb

        Parameters
        ----------
        speed : float
            Speed used (km/h)

        Returns
        -------
        float
            Consumption rate in liters/s
        """
        return self.fuel_consumption_rate * speed / (
                self.S_OPT ** 0.95
                )
