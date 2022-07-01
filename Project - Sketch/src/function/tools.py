import itertools
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


KNOTS2KMH = 1.852  # knots to km/h
KMH2KNOTS = 0.539957  # km/h to knots
FT2M = 0.3048  # Feet to meters
M2FT = 3.281  # Meters to feet

MINALTITUDE = 300  # feet : will be set with the type of terrain
MAXALTITUDE = 40000  # feet : refer to M2000 max

# Get a list for all combinations in dict


def get_all_combinations(d: dict) -> dict:
    keys, values = zip(*d.items())
    ret = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return ret


def get_combinations(d: list):
    values = zip(*d)
    return np.asarray(list(values))


# Display correlation matrix


def showMatrix(matrix: list):

    matrice_corr = matrix.corr().round(2)
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(data=matrice_corr, cmap='RdBu', annot=True)

    plt.show()


def get_curve_value_alt(altitude: int) -> float:
    alt = np.asarray(altitude - 300, dtype=np.int32)
    f = np.linspace(0.90, 1.10, MAXALTITUDE - MINALTITUDE)

    return f[alt]


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
