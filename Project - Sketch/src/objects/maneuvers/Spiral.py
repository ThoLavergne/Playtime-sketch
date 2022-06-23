from Maneuver import *


class Spiral(Maneuver):
    def __init__(self, fullname: str):

        super().__init__(Maneuver_Mission.Spiral, fullname, 81,
                         2000, 24.7)
