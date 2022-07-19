import itertools
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


KNOTS2KMH = 1.852  # knots to km/h
KMH2KNOTS = 0.539957  # km/h to knots
FT2M = 0.3048  # Feet to meters
M2FT = 3.281  # Meters to feet

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


def get_curve_value_alt(altitude: int, plane) -> float:
    alt = np.asarray(altitude - plane.MINALTITUDE, dtype=np.int32)
    f = np.linspace(0.90, 1.10, plane.MAXALTITUDE - plane.MINALTITUDE)

    return f[alt]


def get_key_from_value(d, val):
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None
