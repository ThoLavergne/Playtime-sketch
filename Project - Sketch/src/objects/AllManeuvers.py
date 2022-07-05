from math import pi
from objects.Maneuver import *
import scipy.integrate as integrate
from inspect import signature


class ZigZag(Maneuver):
    def __init__(self, speed: float,
                 altitude: float, gap: float,
                 zone_length: float, zone_width: float):
        # Zone is literaly a zone for the zigzag,
        # can be a rectangle or square
        self.length = zone_length
        self.width = zone_width
        if self.length < gap or self.width < gap:
            raise Exception("Length or width is too small")

        distance = self.calculate_distance(self.length, self.width, gap)
        print(distance)
        super().__init__(Maneuver_Mission.Zigzag, speed,
                         altitude, distance)

    # Calculate the total length of zigzag
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

    def travel_plan(self) -> list:
        return super().travel_plan()

    @classmethod
    def _nb_param_(cls):
        return len(signature(cls.__init__).parameters)


class Spiral(Maneuver):

    def __init__(self, speed: float,
                 altitude: float, gap: float,
                 zone_length: float):

        # Zone is literaly a zone for the spiral, and has to be a square
        self.length = zone_length
        # Let's not do a spiral in a rectangle
        distance = self.calculate_distance(self.length, gap)
        super().__init__(Maneuver_Mission.Spiral, speed,
                         altitude, distance)

    def travel_plan(self) -> list:
        return super().travel_plan()

    # Calculate the total length of Spiral
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

    @classmethod
    def _nb_param_(cls):
        return len(signature(cls.__init__).parameters)


class ShowOfForce(Maneuver):
    # maxspeed: int, minspeed: int,
    def __init__(self):
        # Normally, there are constant values for everything in the show of
        # force. We can leave parameters but throw fixed value in super.

        super().__init__(Maneuver_Mission.ShowOfForce, 150,
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

    @classmethod
    def _nb_param_(cls):
        return len(signature(cls.__init__).parameters)


# Particular maneuver : circle above the objective

class Wheel(Maneuver):
    # maxspeed: int, minspeed: int,
    def __init__(self, meanspeed: int, altitude: float,
                 radius: float,):
        self.radius = radius
        distance = self.calculate_circle(radius) + STRAIGHT_LINE_WHEEL
        super().__init__(Maneuver_Mission.Wheel, meanspeed,
                         altitude, distance,)

    def travel_plan(self) -> list:
        # Add few steps in the wheel : first is a circle at meanspeed
        # and fixed altitude. Second is min speed to quit the circle.
        # Lastly, the plane go straight above the objective at max speed.

        t_plan = []

        first = dict()
        first['Speed'] = self.meanspeed_kmh
        first['Distance'] = self.calculate_circle(self.radius)
        first['Altitude'] = self.altitude
        first['Time'] = first['Distance'] / (self.meanspeed_kmh / 3600)
        t_plan.append(first)

        second = dict()
        second['Speed'] = self.minspeed_kmh
        second['Distance'] = STRAIGHT_LINE_WHEEL / 4
        second['Altitude'] = ((self.altitude / 2) if (self.altitude / 2) >
                              self.minaltitude else self.minaltitude)
        second['Time'] = second['Distance'] / (self.minspeed_kmh / 3600)
        t_plan.append(second)

        third = dict()
        third['Speed'] = self.maxspeed_kmh
        third['Distance'] = STRAIGHT_LINE_WHEEL * 3 / 4
        third['Altitude'] = ((self.altitude / 2) if (self.altitude / 2) >
                             self.minaltitude else self.minaltitude)
        third['Time'] = third['Distance'] / (third['Speed'] / 3600)
        t_plan.append(third)

        return t_plan

    # Calculate circle length
    def calculate_circle(self, radius: float, ):
        return (2 * pi * radius)

    @classmethod
    def _nb_param_(cls):
        return len(signature(cls.__init__).parameters)


LIST_MAN = [Wheel, ShowOfForce, Spiral, ZigZag]
