import itertools
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


KNOTS2KMH = 1.852  # knots to km/h
KMH2KNOTS = 0.539957  # km/h to knots
FT2M = 0.3048  # Feet to meters
M2FT = 3.281  # Meters to feet


def get_all_combinations(d: dict) -> dict:
    """Get all unique combinations for every value in the dictionnary

    Parameters
    ----------
    d : dict
        (String, list)
        Dictionnary with all the combinations we want

    Returns
    -------
    List of dictionnary
        List of every combinations
    """
    keys, values = zip(*d.items())
    ret = [dict(zip(keys, v)) for v in itertools.product(*values)]
    return ret


def get_curve_value_alt(altitude: int, plane) -> float:
    """Get an augmentation or diminution of consumption
    depending on the altitude
    TODO : change for the curve in src/test_conso.ipynb

    Parameters
    ----------
    altitude : int
        Altitude (feet)
    plane : Plane
        Object plane (for min and max altitude)

    Returns
    -------
    float
        Ratio according to the curve of the altitude
    """
    alt = np.asarray(altitude - plane.MINALTITUDE, dtype=np.int32)
    f = np.linspace(0.90, 1.10, plane.MAXALTITUDE - plane.MINALTITUDE)

    return f[alt]


def get_key_from_value(d: dict, val):
    """Get the key for a value in a dictionnary

    Parameters
    ----------
    d : dict

    val : same type as values in dict d
        Value for which we are looking for the key

    Returns
    -------
    key
        Key of the value
    """
    keys = [k for k, v in d.items() if v == val]
    if keys:
        return keys[0]
    return None
