import numpy as np
from objects.AllManeuvers import *
from objects.Plane import *


"""This file contains methods used in Maneuver.ipynb but is deprecated.
    Most function won't be usable, a lot of function / objects
    have been changed.
"""


def compute_maneuver(speed: float, altitude: float,
                     distance: float, iter: int = 1):
    """ Calculate fuel consumption and time for a number of wheel
    with same parameters

    Parameters
    ----------
    speed : float
        Speed for the Wheel (km/h)
    altitude : float
        Altitude for the Wheel (feet)
    distance : float
        Deprecated : distance for the wheel (now the radius) (km)
    iter : int, optional
        Number of wheel to add, by default 1

    Returns
    -------
    (float, float)
        Sum of both fuel consumption and travelled time
    """
    wheels = []
    for _ in range(iter):
        wheels.append(Wheel(speed, altitude, distance))
    return (sum(w.total_fuel_consumption() for w in wheels),
            sum(w.travelled_time() for w in wheels))

# To minimize


"""Those function are used for minimization"""


def loss_fuel_min(fuel_found: int, fuel_wanted: int = 0) -> float:
    """ Difference between fuel found and fuel wanted

    Parameters
    ----------
    fuel_found : int
        in liters
    fuel_wanted : int, optional
        in liters, by default 0

    Returns
    -------
    float
        Difference
    """
    value = np.sqrt((fuel_found - fuel_wanted) ** 2)
    return value


def loss_time_min(time_found: int, time_wanted: int = 0) -> float:
    """Difference between time found and time wanted

    Parameters
    ----------
    time_found : int
        in seconds
    time_wanted : int, optional
        in seconds, by default 0

    Returns
    -------
    float
        _description_
    """
    value = np.sqrt((time_found - time_wanted) ** 2)
    return value


"""Those function are used for maximization"""


def loss_fuel_max(fuel_found: int, fuel_wanted: int = 0) -> float:
    """ Invert of the difference (close difference = high return) for
        fuel.

    Parameters
    ----------
    fuel_found : int
        in liters
    fuel_wanted : int, optional
        in liters, by default 0

    Returns
    -------
    float
        Invert of the difference
    """
    value = 1 / np.sqrt((fuel_found - fuel_wanted) ** 2)
    return value


def loss_time_max(time_found: int, time_wanted: int = 0) -> float:
    """Invert of the difference (close difference = high return) for time.

    Parameters
    ----------
    time_found : int
        in seconds
    time_wanted : int, optional
        in seconds, by default 0

    Returns
    -------
    float
        Invert of the difference
    """
    value = 1 / np.sqrt((time_found - time_wanted) ** 2)
    return value


# Class for Factory method

class LossFunction:
    def __init__(self, c0: int, c1: int, min_max: int):
        """Used for optimization, we define the function we are going to use
        according to the parameters.

        Parameters
        ----------
        c0 : int
            Quantity of fuel we want (fuel_wanted)
        c1 : int
            Time we want (time_wanted)
        For the two above, see loss_fuel and loss_time function above

        min_max : int
            Minimization = 0, Maximization = 1
        """

        self.c0 = c0
        self.c1 = c1
        if min_max == 0:
            self.loss_fuel = loss_fuel_min
            self.loss_time = loss_time_min
        elif min_max == 1:
            self.loss_fuel = loss_fuel_max
            self.loss_time = loss_time_max
        print("Parameters : c0 : ", c0)
        print("c1 : ", c1)
        print("Min" if min_max == 0 else "Max")
    # Methods to calculate and optimize J with single values

    # Loss dependent on fuel and time

    def J_time(self, x0: list) -> float:
        """Compute maneuver Wheel with parameters and see the loss
        (depend on time too)

        Parameters
        ----------
        x0 : list
            List of parameters used for the wheel (speed, altitude, distance)

        Returns
        -------
        float
            loss of the fuel (min or max choosed by init) / time.
            We want to minimize this function so time need to be high.
        """
        speed = x0[0]
        altitude = x0[1]
        distance = x0[2]
        # iter = math.ceil(x0[3])
        fuel_c, time = compute_maneuver(speed, altitude, distance)
        return self.loss_fuel(fuel_c, self.c0) / time

    # Loss only dependent on fuel

    def J_no_time(self, x0: list) -> float:
        """Compute maneuver Wheel with parameters and see the loss
        (Only with fuel)

        Parameters
        ----------
        x0 : list
            List of parameters used for the wheel (speed, altitude, distance)

        Returns
        -------
        float
            loss of the fuel (min or max choosed by init).
            We want to minimize this function so they have to be close.
        """
        speed = x0[0]
        altitude = x0[1]
        distance = x0[2]
        # iter = math.ceil(x0[3])
        fuel_c, time = compute_maneuver(speed, altitude, distance)
        return self.loss_fuel(fuel_c, self.c0)

    # Loss only dependent on time

    def J_only_time(self, x0: list) -> float:
        """Compute maneuver Wheel with parameters and see the loss
        (Only with time)

        Parameters
        ----------
        x0 : list
            List of parameters used for the wheel (speed, altitude, distance)

        Returns
        -------
        float
            loss of the time (min or max choosed by init).
            We want to minimize this function so they have to be close.
        """
        speed = x0[0]
        altitude = x0[1]
        distance = x0[2]
        # iter = math.ceil(x0[3])
        fuel_c, time = compute_maneuver(speed, altitude, distance)
        return self.loss_time(time, self.c1)

    def choose_J(self, time: int):
        """Choose associated loss with time as 1, 2 or 3

        Parameters
        ----------
        time : int
            1, 2 or 3 for the type of function

        Returns
        -------
        function
            Corresponding function according to the choice

        Raises
        ------
        Exception
            time parameter is not supported
        """

        if time == 1:
            return self.J_time
        elif time == 2:
            return self.J_no_time
        elif time == 3:
            return self.J_only_time
        else:
            raise Exception("Time is not valid")

    # Dependent on time and fuel

    def J_to_compute(self, x0: list) -> float:
        """Same as J functions but usable with np.array. Used for plot.

        Parameters
        ----------
        x0 : list
            Parameters to use for wheel

        Returns
        -------
        float
            Loss to minimize, according to time
        """
        values = get_values_from_list(x0)
        return self.loss_fuel(values[:, 0], self.c0) / values[:, 1]

    # Dependent only on fuel

    def J_to_compute_no_time(self, x0: list) -> float:
        """Same as J functions but usable with np.array. Used for plot.
        (Only with fuel)

        Parameters
        ----------
        x0 : list
            Parameters to use for wheel

        Returns
        -------
        float
            Loss to minimize, only with fuel
        """
        values = get_values_from_list(x0)
        return self.loss_fuel(values[:, 0], self.c0)

    # Dependant only on time

    def J_to_compute_only_time(self, x0: list):
        """Same as J functions but usable with np.array. Used for plot.
        (Only with time)

        Parameters
        ----------
        x0 : list
            Parameters to use for wheel

        Returns
        -------
        float
            Loss to minimize, only with time
        """
        values = get_values_from_list(x0)
        return self.loss_time(values[:, 1], self.c1)

    def choose_J_to_compute(self, time: int):
        """Choose associated function to compute with time as 1, 2 or 3

        Parameters
        ----------
        time : int
            1, 2 or 3 for the type of function

        Returns
        -------
        function
            Corresponding function according to the choice

        Raises
        ------
        Exception
            time is not supported
        """
        if time == 1:
            return self.J_to_compute
        elif time == 2:
            return self.J_to_compute_no_time
        elif time == 3:
            return self.J_to_compute_only_time
        else:
            raise Exception("Time not valid")

    # Return the result of J if we exclude X, Y or Z
    # depending of time and label

    def J_to_compute_except(self, X, Y, Z, label: int, time: int = 2):
        """Compute J, but excluding one of the three dimension (X, Y, Z).

        Parameters
        ----------
        X : array
            First dimension, speed
        Y : array
            Second dimension, altitude
        Z : array
            Third dimension, distance
        label : int
            1, 2 or 3, for the choice of dimension to exclude
        time : int, optional
            Choose of loss 1, 2 or 3, by default 2

        Returns
        -------
        array
            Return the result of the J_to_compute but with a dimension less

        Raises
        ------
        Exception
            Dimension not found, label is not supported
        """
        if label == 1:
            method = self.J_to_compute_noX
        elif label == 2:
            method = self.J_to_compute_noY
        elif label == 3:
            method = self.J_to_compute_noZ
        else:
            raise Exception("Label not found, enter 1 for X, 2 for Y, 3 for Z")
        return method(X, Y, Z, time)

    def J_to_compute_except2(self, X, Y, Z, label1: int,
                             label2: int, time: int = 2):
        """Return the result of J if we exclude 2 dimensions of X, Y or Z
        depending of time and label

        Parameters
        ----------
        X : array
            First dimension, speed
        Y : array
            Second dimension, altitude
        Z : array
            Third dimension, distance
        label1 : int
            1, 2 or 3, for the choice of dimension to exclude
        label2 : int
            1, 2 or 3, for the choice of dimension to exclude
        time : int, optional
            Choose of loss 1, 2 or 3, by default 2

        Returns
        -------
        Array
            Result of the J function but with 2 dimensions excluded

        Raises
        ------
        Exception
            Labels not supported (1 and 1, 4...)
        """
        if (label1 == 1 and label2 == 2) or (label1 == 2 and label2 == 1):
            method = self.J_to_compute_noXY
        elif (label1 == 1 and label2 == 3) or (label1 == 3 and label2 == 1):
            method = self.J_to_compute_noXZ
        elif (label1 == 2 and label2 == 3) or (label1 == 3 and label2 == 2):
            method = self.J_to_compute_noYZ
        else:
            raise Exception("Label not found, enter 1 for X, 2 for Y, 3 for Z")
        return method(X, Y, Z, time)

    def J_to_compute_noZ(self, X, Y, Z, time: int):
        """Return J with a 1D Z and 2D X and Y

        Parameters
        ----------
        X : array
            First dimension, speed
        Y : array
            Second dimension, altitude
        Z : array
            Third dimension, distance
        time : int
            Choose of loss 1, 2 or 3

        Returns
        -------
        _type_
            _description_
        """
        method = self.choose_J(time)
        res = []
        for i, row in enumerate(list(zip(X, Y))):
            x, y = row
            res.append([])
            for xi, yi, zi in zip(x, y, Z):
                res[i].append(method([xi, yi, zi]))
        return res

    # Return J with a 1D Y and 2D X and Z
    def J_to_compute_noY(self, X, Y, Z, time: int):
        """J without Y

        Parameters
        ----------
        X : array
            First dimension, speed
        Y : array
            Second dimension, altitude
        Z : array
            Third dimension, distance
        time : int
            Choose of loss 1, 2 or 3

        Returns
        -------
        _type_
            _description_
        """
        method = self.choose_J(time)
        res = []
        for i, row in enumerate(list(zip(X, Z))):
            x, z = row
            res.append([])
            for xi, yi, zi in zip(x, Y, z):
                res[i].append(method([xi, yi, zi]))
        return res

    # Return J with a 1D X and 2D Y and Z
    def J_to_compute_noX(self, X, Y, Z, time: int):
        """J without X

        Parameters
        ----------
        X : array
            First dimension, speed
        Y : array
            Second dimension, altitude
        Z : array
            Third dimension, distance
        time : int
            Choose of loss 1, 2 or 3

        Returns
        -------
        _type_
            _description_
        """
        method = self.choose_J(time)
        res = []
        for i, row in enumerate(list(zip(Y, Z))):
            y, z = row
            res.append([])
            for xi, yi, zi in zip(X, y, z):
                res[i].append(method([xi, yi, zi]))
        return res

    # Return J with a 2D Z and 1D X and Y
    def J_to_compute_noXY(self, X, Y, Z, time: int):
        """J without X and Y

        Parameters
        ----------
        X : array
            First dimension, speed
        Y : array
            Second dimension, altitude
        Z : array
            Third dimension, distance
        time : int
            Choose of loss 1, 2 or 3

        Returns
        -------
        _type_
            _description_
        """
        method = self.choose_J(time)
        res = []
        for i, z in enumerate(Z):
            res.append([])
            for xi, yi, zi in zip(X, Y, z):
                res[i].append(method([xi, yi, zi]))
        return res

    # Return J with a 2D X and 1D Y and Z
    def J_to_compute_noYZ(self, X, Y, Z, time: int):
        """ J without Y and Z

        Parameters
        ----------
        X : array
            First dimension, speed
        Y : array
            Second dimension, altitude
        Z : array
            Third dimension, distance
        time : int
            Choose of loss 1, 2 or 3

        Returns
        -------
        _type_
            _description_
        """
        method = self.choose_J(time)
        res = []
        for i, x in enumerate(X):
            res.append([])
            for xi, yi, zi in zip(x, Y, Z):
                res[i].append(method([xi, yi, zi]))
        return res

    # Return J with a 2D Y and 1D X and Z
    def J_to_compute_noXZ(self, X, Y, Z, time: int):
        """J without X and Z

        Parameters
        ----------
        X : array
            First dimension, speed
        Y : array
            Second dimension, altitude
        Z : array
            Third dimension, distance
        time : int
            Choose of loss 1, 2 or 3

        Returns
        -------
        _type_
            _description_
        """
        method = self.choose_J(time)
        res = []
        for i, y in enumerate(Y):
            res.append([])
            for xi, yi, zi in zip(X, y, Z):
                res[i].append(method([xi, yi, zi]))
        return res


def get_values_from_list(x0: list):
    """Methods to compute J into a graph


    Parameters
    ----------
    x0 : list
        _description_

    Returns
    -------
    _type_
        _description_
    """
    x = np.asarray(x0)
    values = []
    for spd, alt, dis in zip(x[0], x[1], x[2]):
        fuel_c, time = compute_maneuver(spd, alt, dis)
        values.append((fuel_c, time))
    return np.array(values)
