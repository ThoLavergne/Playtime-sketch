from objects.Plane import Plane
from enum import Enum
from function.tools import KMH2KNOTS, KNOTS2KMH, FT2M, M2FT
import math

MINDISTWHEEL = 2.5  # KM : used for the straight line above the objective

STRAIGHT_LINE_SF = 10  # KM : used for the straight line to go next to the
ARC_SF = 4.7  # KM : used for the arc between the two straight lines
# objective and another one above the objective
MINALTITUDE = 0.2  # KM : will be set with the type of terrain
MAXALTITUDE = 18  # KM : refer to M2000 max

CONSTK1 = 0.00051

MINSPEED = 100  # KM/H : used for reference for ULM
MAXSPEED = 200  # KM/H : used for reference for ULM


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
                 distance: float,
                 #  efficiency: int = 50
                 ):
        #  maxspeed: int, minspeed: int,
        # if efficiency <= 100 and efficiency >= 0:
        #     self.efficiency = efficiency
        # else:
        #     self.efficiency = 50
        #     raise Exception("Efficiency is not valid, set to 0")
        self.name = name
        self.fullname = fullname

        self.meanspeed = meanspeed  # In knots
        self.meanspeed_kmh = round((self.meanspeed * KNOTS2KMH))
        self.maxspeed = round(MAXSPEED * KMH2KNOTS)
        # maxspeed
        self.maxspeed_kmh = MAXSPEED
        # maxspeed * KNOTS2KMH
        self.minspeed = round(MINSPEED * KMH2KNOTS)
        # minspeed
        self.minspeed_kmh = MINSPEED
        # minspeed * KNOTS2KMH

        self.altitude = altitude  # In KM
        self.minaltitude = MINALTITUDE
        self.maxaltitude = MAXALTITUDE
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
        total = sum(fuel_consumption_rate
                    (p['Speed'], p['Altitude'], plane)
                    * p['Time'] for p in self.plan)
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


# Particular maneuver : circle above the objective

class Wheel(Maneuver):
    # maxspeed: int, minspeed: int,
    def __init__(self, fullname: str, meanspeed: int, altitude: float,
                 distance: float,
                 #  efficiency: int = 50
                 ):
        super().__init__(Maneuver_Mission.Wheel, fullname, meanspeed,
                         altitude, distance,
                         #  efficiency
                         )
        #  maxspeed, minspeed,
        # if self.distance <= 2 * MINDISTWHEEL:
        #     raise Exception("Not enough distance, at least ",
        #                     MINDISTWHEEL * 2, " km for a nicely done wheel")

    def travel_plan(self) -> list:
        # Add few steps in the wheel : first is a circle at meanspeed
        # and fixed altitude. Second is min speed to quit the circle.
        # Lastly, the plane go straight above the objective at max speed.

        t_plan = []

        first = dict()
        first['Speed'] = self.meanspeed_kmh
        first['Distance'] = MINDISTWHEEL
        first['Altitude'] = self.altitude
        first['Time'] = MINDISTWHEEL / (self.meanspeed_kmh / 3600)
        t_plan.append(first)

        second = dict()
        second['Speed'] = self.minspeed_kmh
        second['Distance'] = 0.5
        second['Altitude'] = (self.altitude / 2)
        second['Time'] = 0.5 / (self.minspeed_kmh / 3600)
        t_plan.append(second)

        third = dict()
        third['Speed'] = self.maxspeed_kmh
        third['Distance'] = self.distance - MINDISTWHEEL - 0.5
        third['Altitude'] = (self.altitude / 2)
        third['Time'] = third['Distance'] / (third['Speed'] / 3600)
        t_plan.append(third)

        return t_plan


class ShowOfForce(Maneuver):
    # maxspeed: int, minspeed: int,
    def __init__(self, fullname: str):
        #  maxspeed, minspeed,
        # Normally, there are constant values for everything in the show of
        # force. We can leave parameters but throw fixed value in super.

        super().__init__(Maneuver_Mission.ShowOfForce, fullname, 81,
                         108, 50, (1500 * FT2M) / 1000, (1000 * FT2M) / 1000,
                         (2000 * FT2M) / 1000, 24.7)

    def travel_plan(self) -> list:
        # Add few steps in the show of force : first is a line at meanspeed
        # and high altitude. Second is min speed and reducing altitude
        # Lastly, at a minimum altitude the plane go straight above the
        # objective at max speed.

        t_plan = []

        first = dict()
        first['Speed'] = self.meanspeed_kmh
        first['Distance'] = STRAIGHT_LINE_SF
        first['Altitude'] = self.altitude * 3
        first['Time'] = STRAIGHT_LINE_SF / (self.meanspeed_kmh / 3600)
        t_plan.append(first)

        second = dict()
        second['Speed'] = self.minspeed_kmh
        second['Distance'] = 4.7
        second['Altitude'] = self.altitude * (3/2)
        second['Time'] = 2 / (self.minspeed_kmh / 3600)
        t_plan.append(second)

        third = dict()
        third['Speed'] = self.maxspeed_kmh
        third['Distance'] = STRAIGHT_LINE_SF
        third['Altitude'] = self.altitude
        third['Time'] = third['Distance'] / (third['Speed'] / 3600)
        t_plan.append(third)

        return t_plan


def fuel_consumption_rate(speed: float, altitude: float,
                          plane: Plane,) -> float:
    # Speed is in km/h, altitude in km, plane is the object Plane
    # Kg/s according to a plane's mean consumption rate, speed and altitude
    return (plane.get_consumption_rate((speed**3/2)) *
            math.exp(-CONSTK1 * altitude))
