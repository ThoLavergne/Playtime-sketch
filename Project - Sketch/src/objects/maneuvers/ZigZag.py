from Maneuver import *


class ZigZag(Maneuver):
    def __init__(self, fullname: str):

        super().__init__(Maneuver_Mission.Zigzag, fullname, 81,
                         2000, 24.7)
