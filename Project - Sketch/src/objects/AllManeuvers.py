from math import pi
from objects.Maneuver import *
import scipy.integrate as integrate
from inspect import signature

# For all those maneuvers, check the Playtime's Miro to have more details
# Some parameters may differ.


# Recon maneuver, sweep / scan zone.

class ZigZag(Maneuver):
    def __init__(self, speed: float, altitude: float, gap: float,
                 zone_length: float, zone_width: float, plane: Plane):
        """Zigzag or Radiator maneuver

        Parameters
        ----------
        speed : float
            Mean speed for the maneuver (km/h)
        altitude : float
            Mean altitude for the maneuver (feet)
        gap : float
            Gap between each pass through (km)
        zone_length : float
            Length of the zone to scan (km)
        zone_width : float
            Width of the zone to scan (km)
        plane : Plane
            Type of plane

        Raises
        ------
        Exception
            If the length or the width is smaller than the gap
        """
        # Zone is literaly a zone for the zigzag,
        # can be a rectangle or square
        self.gap = gap
        self.length = zone_length
        self.width = zone_width
        if self.length < gap or self.width < gap:
            raise Exception("Length or width is too small")

        distance = self.calculate_distance(self.length, self.width, gap)
        super().__init__(Maneuver_Mission.Zigzag, speed,
                         altitude, distance, plane)

    # Calculate the total length of zigzag
    def calculate_distance(self, length: float, width: float,
                           gap: float) -> float:
        """Calculate the travelled distance for the zigzag / radiator

        Parameters
        ----------
        length : float
            Length of the zone to scan (km)
        width : float
            Width of the zone to scan (km)
        gap : float
            Gap between each pass through (km)

        Returns
        -------
        float
            Travelled distance
        """
        radius = gap / 2
        line = length - gap
        arc = pi * radius
        distance = 0
        width_travelled = radius
        # Start at half gap for the first line
        while width_travelled < width - radius:
            distance += line + arc
            width_travelled += gap

        return distance

    @classmethod
    def _nb_param_(cls) -> int:
        """Get number of param needed for the init

        Returns
        -------
        int
            Number of param
        """
        return len(signature(cls.__init__).parameters)


# Recon maneuver, sweep / scan zone.

class Spiral(Maneuver):

    def __init__(self, speed: float, altitude: float, gap: float,
                 zone_length: float, plane: Plane):
        """Spiral maneuver

        Parameters
        ----------
        speed : float
            Mean speed for the maneuver (km/h)
        altitude : float
            Mean altitude for the maneuver (feet)
        gap : float
            Gap between each pass through (km)
        zone_length : float
            Length and width of the zone to scan (km)
        plane : Plane
            Type of plane
        """
        # Zone is literaly a zone for the spiral, and has to be a square
        self.gap = gap
        self.length = zone_length
        # Let's not do a spiral in a rectangle
        distance = self.calculate_distance(self.length, self.gap)
        super().__init__(Maneuver_Mission.Spiral, speed,
                         altitude, distance, plane)

    def calculate_distance(self, length: float, gap: float) -> float:
        """Calculate the total length / travelled distance of the spiral

        Parameters
        ----------
        length : float
            Length and width of the zone to scan
        gap : float
            Gap between each pass through (km)

        Returns
        -------
        float
            Total length of the spiral
        """
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
        return distance[0]

    @classmethod
    def _nb_param_(cls):
        """Get number of param needed for the init

        Returns
        -------
        int
            Number of param
        """
        return len(signature(cls.__init__).parameters)


# Intimidation maneuver.

class ShowOfForce(Maneuver):
    # maxspeed: int, minspeed: int,
    def __init__(self, meanspeed: int, plane: Plane):
        """Create show of force maneuver, intimidation

        Parameters
        ----------
        meanspeed : int
            Mean speed used to make distance (km/h)
        plane : Plane
            Type of plane
        """
        # Normally, there are constant values for everything in the show of
        # force. We can leave parameters but throw fixed value in super.

        super().__init__(Maneuver_Mission.ShowOfForce, meanspeed,
                         2000, 24.7, plane)

    def total_fuel_consumption(self) -> float:
        """Calculate the total fuel consumption for this maneuver
        according to the travel plan.

        Returns
        -------
        float
            Total fuel consumption (liters)
        """
        return sum(p.total_fuel_consumption() for p in self.travel_plan())

    def travelled_time(self) -> float:
        """Calculate the total travelled time for this maneuver
        according to the travel plan.

        Returns
        -------
        float
            Total travelled time (seconds)
        """
        return sum(p.travelled_time() for p in self.travel_plan())

    def travel_plan(self) -> list:
        """Break down of the steps of this maneuver. See Miro for information

        Returns
        -------
        list
            List of SimpleMove (Maneuver), with unique speed, altitude and
            travelled distance. Used for the total travel time and
            total fuel consumption.
        """

        # Add few steps in the show of force : first is a line at meanspeed
        # and high altitude.

        t_plan = []
        first = Maneuver(Maneuver_Mission.SimpleMove, self.meanspeed,
                         self.altitude, STRAIGHT_LINE_SF, self.plane)
        t_plan.append(first)

        # Second is min speed and reducing altitude
        second_alt = ((self.altitude * (3/2)) if (self.altitude * 3/2)
                      < self.maxaltitude else self.maxaltitude)
        second = Maneuver(Maneuver_Mission.SimpleMove, self.minspeed,
                          second_alt, 4.7, self.plane)
        t_plan.append(second)

        # Lastly, at a minimum altitude the plane go straight above the
        # objective at max speed.
        third = Maneuver(Maneuver_Mission.SimpleMove, self.maxspeed,
                         self.minaltitude, STRAIGHT_LINE_SF, self.plane)
        t_plan.append(third)

        return t_plan

    @classmethod
    def _nb_param_(cls):
        """Get number of param needed for the init

        Returns
        -------
        int
            Number of param
        """
        return len(signature(cls.__init__).parameters)


# Circle above the objective : intimidation or attack maneuver

class Wheel(Maneuver):
    # maxspeed: int, minspeed: int,
    def __init__(self, meanspeed: int, altitude: float,
                 radius: float, plane: Plane):
        """Create Wheel maneuver, intimidation or attack.

        Parameters
        ----------
        meanspeed : int
            Mean speed used for the circle. (km/h)
        altitude : float
            Mean altitude used for the circle (feet)
        radius : float
            Radius of the circle (km)
        plane : Plane
            Type of plane
        """

        self.radius = radius
        distance = self.calculate_circle(radius) + STRAIGHT_LINE_WHEEL
        super().__init__(Maneuver_Mission.Wheel, meanspeed,
                         altitude, distance, plane)

    def total_fuel_consumption(self) -> float:
        """Calculate the total fuel consumption for this maneuver
        according to the travel plan.

        Returns
        -------
        float
            Total fuel consumption (liters)
        """
        return sum(p.total_fuel_consumption for p in self.travel_plan())

    def travelled_time(self) -> float:
        """Calculate the total travelled time for this maneuver
        according to the travel plan.

        Returns
        -------
        float
            Total travelled time (seconds)
        """
        return sum(p.travelled_time() for p in self.travel_plan())

    def travel_plan(self) -> list:
        """Break down of the steps of this maneuver. See Miro for information

        Returns
        -------
        list
            List of SimpleMove (Maneuver), with unique speed, altitude and
            travelled distance. Used for the total travel time and
            total fuel consumption.
        """

        # TODO : change for maneuvers
        t_plan = []
        # Add few steps in the wheel : first is a circle at meanspeed
        # and fixed altitude.
        first = Maneuver(Maneuver_Mission.SimpleMove, self.meanspeed,
                         self.altitude, self.calculate_circle(self.radius),
                         self.plane)
        t_plan.append(first)

        # Second is min speed to quit the circle.
        second_alt = ((self.altitude / 2) if (self.altitude / 2) >
                      self.minaltitude else self.minaltitude)
        second = Maneuver(Maneuver_Mission.SimpleMove, self.minspeed,
                          second_alt, STRAIGHT_LINE_WHEEL / 4, self.plane)
        t_plan.append(second)

        # Lastly, the plane go straight above the objective at max speed.
        third_alt = ((self.altitude / 2) if (self.altitude / 2) >
                     self.minaltitude else self.minaltitude)
        third = Maneuver(Maneuver_Mission.SimpleMove, self.maxspeed,
                         third_alt, STRAIGHT_LINE_WHEEL * 3 / 4, self.plane)
        t_plan.append(third)

        return t_plan

    # Calculate circle length
    def calculate_circle(self, radius: float, ) -> float:
        """Calculate the size of the circle

        Parameters
        ----------
        radius : float
            Radius of the circle
        Returns
        -------
        float
            Total size
        """
        return (2 * pi * radius)

    @classmethod
    def _nb_param_(cls):
        """Get number of param needed for the init

        Returns
        -------
        int
            Number of param
        """
        return len(signature(cls.__init__).parameters)


# List of all usable maneuver
# WIP

LIST_MAN = [Wheel, ShowOfForce, Spiral, ZigZag]
