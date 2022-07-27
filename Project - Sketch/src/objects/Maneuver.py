from objects.Plane import Plane
from enum import Enum
from function.tools import *
import math


STRAIGHT_LINE_WHEEL = 2  # KM : used for the straight line above the objective
RADIUS_MIN_WHEEL = 2  # KM
RADIUS_MAX_WHEEL = 5  # KM

STRAIGHT_LINE_SF = 10  # KM : used for the straight line to go next to the
ARC_SF = 4.7  # KM :
# used for the arc between the two straight lines
# objective and another one above the objective

# Deprecated
MINSPEED = 100  # KM/H : used for reference for ULM
MAXSPEED = 200  # KM/H : used for reference for ULM

# Deprecated, see C2030 for the consumption function.
CONSTK1 = 0.0049


# Every type of maneuver available

class Maneuver_Mission(Enum):
    """ Type of maneuver, to get a value, used for the name of value in
    Maneuver class."""
    Wheel = 1
    ShowOfForce = 2
    Spiral = 3
    Zigzag = 4
    SimpleMove = 5


# Every type of mission available, associated with maneuvers

class Mission_Maneuver(Enum):
    """Type of mission, with maneuvers needed

    Parameters
    ----------
    Enum : Int
        Value for the type of mission
    """
    SCAR = 1
    CAS = 2

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # Get the available maneuvers for the mission

    def getManeuvers(self):
        """Depending on the type of mission, some maneuvers are available.

        Returns
        -------
        List
            List of enum, type of maneuvers available
        """
        if self.value == 1:
            return [Maneuver_Mission.Wheel, Maneuver_Mission.ShowOfForce,
                    Maneuver_Mission.Spiral, Maneuver_Mission.Zigzag,
                    # Maneuver_Mission.SimpleMove
                    ]
        # No difference for now
        elif self.value == 2:
            return [Maneuver_Mission.Wheel, Maneuver_Mission.ShowOfForce,
                    Maneuver_Mission.Spiral, Maneuver_Mission.Zigzag,
                    # Maneuver_Mission.SimpleMove
                    ]

    def getMinManeuver(self):
        """Depending on the type of mission, it is mandatory to do
        at least a fixed number of certain maneuvers.

        Returns
        -------
        dict
            Dictionnary with as the key the name of the maneuver
            and as the value, the number of time it is needed.
        """
        if self.value == 1:
            return {Maneuver_Mission.ShowOfForce: 1, Maneuver_Mission.Wheel: 1}
        elif self.value == 2:
            return {Maneuver_Mission.Wheel: 2}


class Maneuver:
    """Maneuver associated with a speed, altitude, efficiency and plane,
    calculate fuel consumption and time."""
    def __init__(self, name: Maneuver_Mission,
                 meanspeed: int, altitude: float,
                 distance: float, plane: Plane
                 # TODO : add wind constraints
                 ):
        """Generate Maneuver object. At this level, it is simply a move
        according to a distance, at a certain speed

        Parameters
        ----------
        name : Maneuver_Mission
            name of the type of maneuver
        meanspeed : int
            Speed for the move (km/h)
        altitude : float
            Altitude for the move (feet)
        distance : float
            Distance travelled for the move (km)
        plane : Plane
            Type of plane
        """

        self.name = name
        self.plane = plane
        self.meanspeed = meanspeed  # In km/h
        # Add assert for interval maxspeed and minspeed ?
        # assert meanspeed < maxspeed and meanspeed > minspeed
        self.maxspeed = self.plane.MAXSPEED  # In km/h
        self.minspeed = self.plane.MINSPEED  # In km/h

        # Not used : speed in Knots
        # self.meanspeed = round((self.meanspeed_kmh * KMH2KNOTS))
        # self.maxspeed = round(self.plane.MAXSPEED * KMH2KNOTS)
        # self.minspeed = round(self.plane.MINSPEED * KMH2KNOTS)

        self.altitude = altitude
        # Add assert ?
        self.minaltitude = plane.MINALTITUDE
        self.maxaltitude = plane.MAXALTITUDE

        # This part is commented because there was conflict with optimization.

        # if altitude >= self.minaltitude and altitude <= self.maxaltitude:
        #     self.altitude = altitude  # In feet
        # else:
        #     raise Exception("Altitude is not between min and max : ",
        #     altitude)

        self.distance = round(distance, 2)  # In KM

    def travelled_time(self) -> float:
        """Calculate the total time travelled during the maneuver.

        Returns
        -------
        float
            travelled time
        """
        time = self.distance / (self.meanspeed / 3600)
        return round(time, 2)

    def total_fuel_consumption(self) -> float:
        """Calculate the total fuel consumption for the full maneuver.

        Returns
        -------
        float
            total fuel consumption (liters)
        """
        # Kg according to the travelled time.
        total = (fuel_consumption_rate
                 (self.meanspeed, self.altitude, self.plane)
                 * self.travelled_time())
        return round(total, 2)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name.name


def fuel_consumption_rate(speed: float, altitude: float,
                          plane: Plane,) -> float:
    """ Calculate fuel consumption rate according to speed, altitude,
    and the plane.
    TODO : This function is WIP, need to tweak the computation
    See todo in Plane.py

    Parameters
    ----------
    speed : float
        Speed used for the moment (km/h)
    altitude : float
        Altitude used for the moment (feet)
    plane : Plane
        Plane used to calculate the fuel consumption rate

    Returns
    -------
    float
        Fuel consumption rate (liters/s)
    """
    alt_ratio = get_curve_value_alt(altitude, plane)
    spd = speed ** 1.05
    fcr = (plane.get_consumption_rate(spd) / alt_ratio)
    # print(plane.get_consumption_rate(spd), fcr)
    return fcr

# TODO : Add units tests
