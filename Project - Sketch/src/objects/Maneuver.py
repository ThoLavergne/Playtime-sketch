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


MINSPEED = 100  # KM/H : used for reference for ULM
MAXSPEED = 200  # KM/H : used for reference for ULM

CONSTK1 = 0.0049


# Every type of maneuver available

class Maneuver_Mission(Enum):
    Wheel = 1
    ShowOfForce = 2
    Spiral = 3
    Zigzag = 4
    SimpleMove = 5


# Every type of mission available, associated with maneuvers

class Mission_Maneuver(Enum):
    SCAR = 1
    CAS = 2

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # Get the available maneuvers for the mission

    def getManeuvers(self):
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
        if self.value == 1:
            return {Maneuver_Mission.Wheel: 2}
        elif self.value == 2:
            return {Maneuver_Mission.ShowOfForce: 1, Maneuver_Mission.Wheel: 1}


# Maneuver associated with a speed, altitude, efficiency
# and calculate fuel consumption

class Maneuver:

    def __init__(self, name: Maneuver_Mission,
                 meanspeed: int, altitude: float,
                 distance: float, plane: Plane
                 ):
        self.name = name
        self.plane = plane

        self.meanspeed = meanspeed  # In kmh
        # self.meanspeed = round((self.meanspeed_kmh * KMH2KNOTS))

        self.maxspeed = self.plane.MAXSPEED  # In kmh
        # self.maxspeed = round(self.plane.MAXSPEED * KMH2KNOTS)

        self.minspeed = self.plane.MINSPEED  # In kmh
        # self.minspeed = round(self.plane.MINSPEED * KMH2KNOTS)

        self.minaltitude = plane.MINALTITUDE
        self.maxaltitude = plane.MAXALTITUDE
        self.altitude = altitude

        # if altitude >= self.minaltitude and altitude <= self.maxaltitude:
        #     self.altitude = altitude  # In feet
        # else:
        #     raise Exception("Altitude is not between min and max : ",
        #     altitude)

        self.distance = round(distance, 2)  # In KM
        self.plan = self.travel_plan()

    # Calculate the total time travelled during the maneuver

    def travelled_time(self) -> float:
        time = sum(p['Time'] for p in self.plan)  # (lambda x : ,)
        return round(time, 2)

    # Calculate the total fuel consumption for the full maneuver

    def total_fuel_consumption(self) -> float:
        # Kg according to the travelled time.
        total = sum((fuel_consumption_rate
                    (p['Speed'], p['Altitude'], self.plane)
                    * p['Time']) for p in self.plan)
        return round(total, 2)

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name.name

    # Return a list of sequence for the maneuver with an associated speed,
    # distance, altitude and time for each sequence.
    # Used to calculate the cost for every sequence.
    def travel_plan(self) -> list:
        t_plan = []
        plan = dict()
        plan['Speed'] = self.meanspeed
        plan['Distance'] = self.distance
        plan['Altitude'] = self.altitude
        plan['Time'] = plan['Distance'] / (plan['Speed'] / 3600)
        t_plan.append(plan)

        return t_plan


# Calculate fuel consumption

def fuel_consumption_rate(speed: float, altitude: float,
                          plane: Plane,) -> float:
    # Speed is in km/h, altitude in feet, plane is the object Plane
    # Kg/s according to a plane's mean consumption rate, speed and altitude
    alt_ratio = get_curve_value_alt(altitude, plane)
    spd = speed ** 1.05  # round(speed * KMH2KNOTS)
    # spd = (speed * 0.2778) ** 2  # **   # m/s
    fcr = (plane.get_consumption_rate(spd) / alt_ratio)
    # print(plane.get_consumption_rate(spd), fcr)
    return fcr
