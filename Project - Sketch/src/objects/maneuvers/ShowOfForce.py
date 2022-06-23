from Maneuver import *


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
