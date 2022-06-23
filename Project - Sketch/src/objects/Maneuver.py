from objects.Plane import Plane
from enum import Enum
from function.tools import *
import math


MINDISTWHEEL = 2.5  # KM : used for the straight line above the objective

STRAIGHT_LINE_SF = 10  # KM : used for the straight line to go next to the
ARC_SF = 4.7  # KM : used for the arc between the two straight lines
# objective and another one above the objective


MINSPEED = 100  # KM/H : used for reference for ULM
MAXSPEED = 245  # KM/H : used for reference for ULM

CONSTK1 = 0.0049


# Every type of maneuver available

class Maneuver_Mission(Enum):
    Wheel = 1
    ShowOfForce = 2
    Spiral = 3
    Zigzag = 4


# Every type of mission available, associated with maneuvers

class Mission_Maneuver(Enum):
    SCAR = 1
    CAS = 2

    def __repr__(self):
        return self.name

    def __str__(self):
        return self.name

    # Get the available maneuvers for the mission

    def getManeuver(self):
        if self.value == 1:
            return [Maneuver_Mission.Wheel, Maneuver_Mission.ShowOfForce]
        elif self.value == 2:
            return [Maneuver_Mission.Wheel, Maneuver_Mission.ShowOfForce]

    def getMinManeuver(self):
        if self.value == 1:
            return {Maneuver_Mission.Wheel: 2}
        elif self.value == 2:
            return {Maneuver_Mission.ShowOfForce: 1, Maneuver_Mission.Wheel: 1}


# Maneuver associated with a speed, altitude, efficiency
# and calculate fuel consumption

class Maneuver:

    def __init__(self, name: Maneuver_Mission, fullname: str,
                 meanspeed: int, altitude: float,
                 distance: float,):
        self.name = name
        self.fullname = fullname

        self.meanspeed = meanspeed  # In knots
        self.meanspeed_kmh = round((self.meanspeed * KNOTS2KMH))

        self.maxspeed = round(MAXSPEED * KMH2KNOTS)
        self.maxspeed_kmh = MAXSPEED

        self.minspeed = round(MINSPEED * KMH2KNOTS)
        self.minspeed_kmh = MINSPEED

        self.minaltitude = MINALTITUDE
        self.maxaltitude = MAXALTITUDE
        self.altitude = altitude
        # if altitude >= self.minaltitude and altitude <= self.maxaltitude:
        #     self.altitude = altitude  # In feet
        # else:
        #     raise Exception("Altitude is not between min and max : ",
        #     altitude)

        self.distance = distance  # In KM
        # self.available_mission = name.value
        self.plan = self.travel_plan()

    # Calculate the total time travelled during the maneuver

    def travelled_time(self) -> float:
        time = sum(p['Time'] for p in self.plan)  # (lambda x : ,)
        return time

    # Calculate the total fuel consumption for the full maneuver

    def total_fuel_consumption(self, plane: Plane) -> float:
        # Kg according to the travelled time.
        total = sum((fuel_consumption_rate
                    (p['Speed'], p['Altitude'], plane)
                    * p['Time']) for p in self.plan)
        return total

    def __repr__(self):
        return self.fullname

    def __str__(self):
        return self.fullname

    # Return a list of sequence for the maneuver with an associated speed,
    # distance, altitude and time for each sequence.
    # Used to calculate the cost for every sequence.

    def travel_plan(self) -> list:
        t_plan = []
        plan = dict()
        plan['Speed'] = self.meanspeed_kmh
        plan['Distance'] = self.distance
        plan['Altitude'] = self.altitude
        plan['Time'] = plan['Speed'] / plan['Distance'] / 3600
        t_plan.append(plan)

        return t_plan


# Calculate fuel consumption

def fuel_consumption_rate(speed: float, altitude: float,
                          plane: Plane,) -> float:
    # Speed is in km/h, altitude in feet, plane is the object Plane
    # Kg/s according to a plane's mean consumption rate, speed and altitude
    alt_ratio = get_curve_value_alt(altitude)
    spd = speed ** 1.05  # round(speed * KMH2KNOTS)
    # spd = (speed * 0.2778) ** 2  # **   # m/s
    fcr = (plane.get_consumption_rate(spd) / alt_ratio)
    # print(plane.get_consumption_rate(spd), fcr)
    return fcr
