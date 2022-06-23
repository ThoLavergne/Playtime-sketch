from math import pi
from tracemalloc import start
from objects.Maneuver import *
import scipy.integrate as integrate
import scipy.special as special


class ZigZag(Maneuver):
    def __init__(self, fullname: str, speed: float,
                 altitude: float, gap: float, zone):
        self.length = zone[0]
        self.width = zone[1]
        if self.length < gap or self.width < gap:
            raise Exception("Length or width is too small")

        distance = self.calculate_distance(self.length, self.width, gap)
        print(distance)
        super().__init__(Maneuver_Mission.Zigzag, fullname, speed,
                         altitude, distance)

    def travel_plan(self) -> list:
        t_plan = []
        return t_plan

    def calculate_distance(self, length: float, width: float, gap: float):

        radius = gap / 2
        line = length - gap
        arc = pi * radius
        distance = 0
        width_traveled = radius
        # Start at half gap for the first line
        while width_traveled < width - radius:
            distance += line + arc
            width_traveled += gap

        return distance


class Spiral(Maneuver):
    def __init__(self, fullname: str, speed: float,
                 altitude: float, gap: float, zone):
        if zone[0] != zone[1]:
            raise Exception("The zone is not a square")

        self.length = zone[0]
        # Let's not do a spiral in a rectangle
        distance = self.calculate_distance(self.length, gap)
        super().__init__(Maneuver_Mission.Spiral, fullname, speed,
                         altitude, distance)

    def travel_plan(self) -> list:
        t_plan = []
        return t_plan

    def calculate_distance(self, length: float, gap: float):
        # Source : https://planetcalc.com/9063 (https://fr.planetcalc.com/9063)
        # https://www.intmath.com/blog/mathematics/length-of-an-archimedean-spiral-6595
        r = length - gap
        nb_rings = (r / (gap * 2))
        start_theta = 0
        end_theta = nb_rings * 2 * pi
        b = gap / (2 * pi)
        distance = integrate.quad(lambda theta:
                                  np.sqrt((b * theta) ** 2 + b ** 2),
                                  start_theta, end_theta)
        print(distance)
        return distance[0]


class ShowOfForce(Maneuver):
    # maxspeed: int, minspeed: int,
    def __init__(self, fullname: str):
        # Normally, there are constant values for everything in the show of
        # force. We can leave parameters but throw fixed value in super.

        super().__init__(Maneuver_Mission.ShowOfForce, fullname, 81,
                         2000, 24.7)

    def travel_plan(self) -> list:
        # Add few steps in the show of force : first is a line at meanspeed
        # and high altitude. Second is min speed and reducing altitude
        # Lastly, at a minimum altitude the plane go straight above the
        # objective at max speed.

        t_plan = []

        first = dict()
        first['Speed'] = self.meanspeed_kmh
        first['Distance'] = STRAIGHT_LINE_SF
        first['Altitude'] = self.altitude
        first['Time'] = STRAIGHT_LINE_SF / (self.meanspeed_kmh / 3600)
        t_plan.append(first)

        second = dict()
        second['Speed'] = self.minspeed_kmh
        second['Distance'] = 4.7
        second['Altitude'] = ((self.altitude * (3/2)) if (self.altitude * 3/2)
                              < self.maxaltitude else self.maxaltitude)
        second['Time'] = 2 / (self.minspeed_kmh / 3600)
        t_plan.append(second)

        third = dict()
        third['Speed'] = self.maxspeed_kmh
        third['Distance'] = STRAIGHT_LINE_SF
        third['Altitude'] = ((self.altitude / 2) if (self.altitude / 2) >
                             self.minaltitude else self.minaltitude)
        third['Time'] = third['Distance'] / (third['Speed'] / 3600)
        t_plan.append(third)

        return t_plan


# Particular maneuver : circle above the objective

class Wheel(Maneuver):
    # maxspeed: int, minspeed: int,
    def __init__(self, fullname: str, meanspeed: int, altitude: float,
                 distance: float,):
        super().__init__(Maneuver_Mission.Wheel, fullname, meanspeed,
                         altitude, distance,)

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
        second['Altitude'] = ((self.altitude / 2) if (self.altitude / 2) >
                              self.minaltitude else self.minaltitude)
        second['Time'] = 0.5 / (self.minspeed_kmh / 3600)
        t_plan.append(second)

        third = dict()
        third['Speed'] = self.maxspeed_kmh
        third['Distance'] = self.distance - MINDISTWHEEL - 0.5
        third['Altitude'] = ((self.altitude / 2) if (self.altitude / 2) >
                             self.minaltitude else self.minaltitude)
        third['Time'] = third['Distance'] / (third['Speed'] / 3600)
        t_plan.append(third)

        return t_plan
