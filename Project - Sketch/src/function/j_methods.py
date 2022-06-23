import numpy as np
from objects.AllManeuvers import *
from objects.Plane import ULM

c0: float = 0
c1: float = 0


def compute_maneuver(speed: float, altitude: float,
                     distance: float, iter: int = 2):
    wheels = []
    for _ in range(iter):
        wheels.append(Wheel('Wheel', speed, altitude, distance))
    return (sum(w.total_fuel_consumption(ULM) for w in wheels),
            sum(w.travelled_time() for w in wheels))


# To minimize

def loss_fuel_min(fuel_found: int, fuel_wanted: int = 0) -> float:
    return np.sqrt((fuel_found - fuel_wanted) ** 2)


def loss_time_min(time_found: int, time_wanted: int = 0) -> float:
    return np.sqrt((time_found - time_wanted) ** 2)


# To maximize

def loss_fuel_max(fuel_found: int, fuel_wanted: int = 0) -> float:
    return 1 / np.sqrt((fuel_found - fuel_wanted) ** 2)


def loss_time_max(time_found: int, time_wanted: int = 0) -> float:
    return 1 / np.sqrt((time_found - time_wanted) ** 2)


loss_fuel = loss_fuel_max
loss_time = loss_time_max


# Methods to calculate and optimize J with single values

# Loss dependent on fuel and time


def J_time(x0: list) -> float:
    speed = x0[0]
    altitude = x0[1]
    distance = x0[2]
    # iter = math.ceil(x0[3])
    fuel_c, time = compute_maneuver(speed, altitude, distance)
    return loss_fuel(fuel_c, c0) / time


# Loss only dependent on fuel


def J_no_time(x0: list) -> float:
    speed = x0[0]
    altitude = x0[1]
    distance = x0[2]
    # iter = math.ceil(x0[3])
    fuel_c, time = compute_maneuver(speed, altitude, distance)
    return loss_fuel(fuel_c, c0)


# Loss only dependent on time


def J_only_time(x0: list):
    speed = x0[0]
    altitude = x0[1]
    distance = x0[2]
    # iter = math.ceil(x0[3])
    fuel_c, time = compute_maneuver(speed, altitude, distance)
    return loss_time(time, c1)

# Choose associated loss with time as 1, 2 or 3


def choose_J(time):
    if time == 1:
        return J_time
    elif time == 2:
        return J_no_time
    elif time == 3:
        return J_only_time
    else:
        raise Exception("Time is not valid")


# Methods to compute J into a graph

def get_values_from_list(x0: list):
    x = np.asarray(x0)
    values = []
    for spd, alt, dis in zip(x[0], x[1], x[2]):
        fuel_c, time = compute_maneuver(spd, alt, dis)
        values.append((fuel_c, time))
    return np.array(values)


# Dependent on time and fuel


def J_to_compute(x0: list) -> float:
    values = get_values_from_list(x0)
    return loss_fuel(values[:, 0], c0) / values[:, 1]

# Dependent only on fuel


def J_to_compute_no_time(x0: list) -> float:
    values = get_values_from_list(x0)
    return loss_fuel(values[:, 0], c0)


# Dependant only on time

def J_to_compute_only_time(x0: list):
    values = get_values_from_list(x0)
    return 1 / values[:, 1]

# Choose associated function to compute with time as 1, 2 or 3


def choose_J_to_compute(time: int):
    if time == 1:
        return J_to_compute
    elif time == 2:
        return J_to_compute_no_time
    elif time == 3:
        return J_to_compute_only_time
    else:
        raise Exception("Time not valid")


# Return the result of J if we exclude X, Y or Z depending of time and label

def J_to_compute_except(X, Y, Z, label: int, time: int = 2):
    if label == 1:
        method = J_to_compute_noX
    elif label == 2:
        method = J_to_compute_noY
    elif label == 3:
        method = J_to_compute_noZ
    else:
        raise Exception("Label not found, enter 1 for X, 2 for Y, 3 for Z")
    return method(X, Y, Z, time)


# Return the result of J if we exclude 2 dimensions of X, Y or Z
# depending of time and label


def J_to_compute_except2(X, Y, Z, label1: int, label2: int, time: int = 2):
    if (label1 == 1 and label2 == 2) or (label1 == 2 and label2 == 1):
        method = J_to_compute_noXY
    elif (label1 == 1 and label2 == 3) or (label1 == 3 and label2 == 1):
        method = J_to_compute_noXZ
    elif (label1 == 2 and label2 == 3) or (label1 == 3 and label2 == 2):
        method = J_to_compute_noYZ
    else:
        raise Exception("Label not found, enter 1 for X, 2 for Y, 3 for Z")
    return method(X, Y, Z, time)


# Return J with a 1D Z and 2D X and Y
def J_to_compute_noZ(X, Y, Z, time: int):
    method = choose_J(time)
    res = []
    for i, row in enumerate(list(zip(X, Y))):
        x, y = row
        res.append([])
        for xi, yi, zi in zip(x, y, Z):
            res[i].append(method([xi, yi, zi]))
    return res


# Return J with a 1D Y and 2D X and Z
def J_to_compute_noY(X, Y, Z, time: int):
    method = choose_J(time)
    res = []
    for i, row in enumerate(list(zip(X, Z))):
        x, z = row
        res.append([])
        for xi, yi, zi in zip(x, Y, z):
            res[i].append(method([xi, yi, zi]))
    return res


# Return J with a 1D X and 2D Y and Z
def J_to_compute_noX(X, Y, Z, time: int):
    method = choose_J(time)
    res = []
    for i, row in enumerate(list(zip(Y, Z))):
        y, z = row
        res.append([])
        for xi, yi, zi in zip(X, y, z):
            res[i].append(method([xi, yi, zi]))
    return res


# Return J with a 2D Z and 1D X and Y
def J_to_compute_noXY(X, Y, Z, time: int):
    method = choose_J(time)
    res = []
    for i, z in enumerate(Z):
        res.append([])
        for xi, yi, zi in zip(X, Y, z):
            res[i].append(method([xi, yi, zi]))
    return res


# Return J with a 2D X and 1D Y and Z
def J_to_compute_noYZ(X, Y, Z, time: int):
    method = choose_J(time)
    res = []
    for i, x in enumerate(X):
        res.append([])
        for xi, yi, zi in zip(x, Y, Z):
            res[i].append(method([xi, yi, zi]))
    return res


# Return J with a 2D Y and 1D X and Z
def J_to_compute_noXZ(X, Y, Z, time: int):
    method = choose_J(time)
    res = []
    for i, y in enumerate(Y):
        res.append([])
        for xi, yi, zi in zip(X, y, Z):
            res[i].append(method([xi, yi, zi]))
    return res
