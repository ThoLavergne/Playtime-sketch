from Maneuver import *


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
