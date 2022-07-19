from typing_extensions import Self
import gym
import numpy as np
from gym import spaces
from function.tools import get_key_from_value
from objects.AllManeuvers import *
from function.j_methods import compute_maneuver
from function.j_methods import *
from scipy.optimize import minimize

# Parameters
# Deprecated
time_nb = 1
bounds = ((100, 200), (300, 20000), (15, 40))
min_max: int = 0  # Minimize with 0, maximize with 1


class PlaytimeEnv(gym.Env):
    """Custom Environment that follows gym interface"""
    metadata = {'render.modes': ['human']}

    def __init__(self, gameplan_list: list):
        super(PlaytimeEnv, self).__init__()
        # Do we have to add gameplan parameters to observation ?
        # Seems legit : the agent has to see those parameters to determine
        # Or, we give our agent the gameplan parameters in order to predict

        self.gameplan_list = gameplan_list
        # Set maneuver list or maneuvers done to an empty list.
        self.maneuver_list = []
        # TODO : add other parameters for gameplan like objectives,
        # time constraint, changing wind

        # We create dictionnaries for an enconding similar to onehot
        # in order to create our observation space
        planes = list(set(gp['Plane'] for gp in self.gameplan_list))
        self.plane_index = dict()
        for i, p in enumerate(planes):
            self.plane_index[i] = p

        # We fetch the max fuel quantity in order to create the
        # first observation space.
        maxfuel = 0
        for plane in self.plane_index.values():
            if plane.fuel_max > maxfuel:
                maxfuel = plane.fuel_max

        strength = list(set(gp['Strength'] for gp in self.gameplan_list))
        self.strength_index = dict()
        for i, s in enumerate(strength):
            self.strength_index[i] = s

        meteo = list(set(gp['Meteo'] for gp in self.gameplan_list))
        self.meteo_index = dict()
        for i, m in enumerate(meteo):
            self.meteo_index[i] = m

        missionType = list(set(gp['MissionType'] for gp in self.gameplan_list))
        self.missionType_index = dict()
        for i, mt in enumerate(missionType):
            self.missionType_index[i] = mt

        maneuvers = list(set(
                        filter(lambda x:
                               (x.name in gp['MissionType'].getManeuvers()
                                for gp in self.gameplan_list), LIST_MAN)))
        self.maneuvers_index = dict()
        for i, ma in enumerate(maneuvers):
            self.maneuvers_index[i] = ma

        # End onehot index

        # Let's set the action space with the maneuvers' parameters
        # Change parameters according to plane parameters or others
        # Dicrete 4 for 4 maneuvers available
        # TODO : We have to consider maneuvers parameters to optimize

        self.observation_space = spaces.Dict({
            "time": spaces.Discrete(35000),
            "fuel": spaces.Discrete(200),
            "Plane": spaces.Discrete(len(self.plane_index)),
            "GoalDistance": spaces.Discrete(50),
            "RtBDistance": spaces.Discrete(50),
            "FuelAvailable": spaces.Discrete(maxfuel),
            "Meteo": spaces.Discrete(len(self.meteo_index)),
            "MissionType": spaces.Discrete(len(self.missionType_index)),
            "Strength": spaces.Discrete(len(self.strength_index)),
            "TimeMin": spaces.Discrete(3000),
            "SynchroTime": spaces.Discrete(6000)
        })

        # Name of all parameters in the action space.
        self.action_index = [
            'maneuver',
            'speed',
            'altitude',
            'distance',
            'gap',
            'length',
            'width',
            'radius'
        ]
        self.action_space = spaces.MultiDiscrete(
            [
                len(self.maneuvers_index),
                max(p.MAXSPEED - p.MINSPEED for p in
                    self.plane_index.values()) / 5,
                max(p.MAXALTITUDE - p.MINALTITUDE for p in
                    self.plane_index.values()) / 100,
                max(max(gp['GoalDistance'] for gp in self.gameplan_list),
                    max(gp['RtBDistance'] for gp in self.gameplan_list)),
                4,
                15,
                15,
                4
            ]
        )

        # self.get_new_gameplan()
        # self.reset_action_space()

    # Step for the current episode
    # Can change some parameters, for example changing power balance,
    # wind strength / direction, among others
    # TODO : Change for each maneuver
    def step(self, action):
        # Execute one time step within the environment
        # Action is the new maneuver to add.
        info = {}
        action = dict(zip(self.action_index, action))
        action = self.action_to_real_space(action)
        # print("Action in step :", action)
        maneuver = self.maneuvers_index[action['maneuver']]
        if maneuver == Wheel:
            maneuver = maneuver(action['speed'], action['altitude'],
                                action['radius'], self.plane)
        elif maneuver == ShowOfForce:
            maneuver = maneuver(action['speed'], self.plane)
        elif maneuver == Spiral:
            maneuver = maneuver(action['speed'], action['altitude'],
                                action['gap'], action['length'],
                                self.plane)
        elif maneuver == ZigZag:
            maneuver = maneuver(action['speed'], action['altitude'],
                                action['gap'], action['length'],
                                action['width'], self.plane)

        fuel = maneuver.total_fuel_consumption()
        time = maneuver.travelled_time()
        self.state_to_add = {'fuel': fuel,
                             'time': time}
        # Check if state is correctly initialized
        assert (k in self.state.keys() for k in self.state_to_add.keys())

        for key in self.state_to_add.keys():
            self.state[key] += self.state_to_add[key]
            self.state[key] = round(self.state[key], 2)

        self.maneuver_list.append(maneuver)
        done = self.is_done()
        reward = self.reward(maneuver)
        # print("Current state : ", self.state)
        return (self.state, reward, done, info)

    # Raise the action_space to the real interval
    def action_to_real_space(self, action):
        action['speed'] *= 5
        action['speed'] += self.plane.MINSPEED
        if self.strength != "Strong":
            action['speed'] += self.action_change['speed']
            # if self.strength == "Weak":
            #     print(action['speed'])
        action['altitude'] *= 100
        action['altitude'] += self.plane.MINALTITUDE
        # If meteo is not sunny then we do not raise the threshold
        # if self.meteo != "Sunny":
        #     action['altitude'] += self.action_change['altitude']
        action['distance'] += 15

        action['gap'] += 2
        # If meteo is not sunny, then we do not raise the threshold
        # and keep it low.
        action['length'] += 15
        action['width'] += 15

        action['radius'] += 2
        if self.strength == "Weak":
            action['radius'] += self.action_change['radius']
        # We raise the threshold only if we are weaker.

        return action

    # Set new episode : select new gameplan so new observation
    def reset(self, verbose=1):
        # print("RESET ENV")
        self.get_new_gameplan()
        self.reset_action_space()
        self.maneuver_list = []

        self.state = {'fuel': 0,
                      'time': 0}
        self.state.update(self.gameplan)

        self.state['Plane'] = get_key_from_value(self.plane_index,
                                                 self.state['Plane'])
        self.state['Meteo'] = get_key_from_value(self.meteo_index,
                                                 self.state['Meteo'])
        self.state['MissionType'] = get_key_from_value(
                                    self.missionType_index,
                                    self.state['MissionType'])
        self.state['Strength'] = get_key_from_value(self.strength_index,
                                                    self.state['Strength'])

        # TODO : Consider bingo distance and objective distance in the fuel
        # Add a maneuver ?
        # Need to consider the choice of speed in policy.

        # print("Reset, new obs : ", self.state)
        if verbose:
            print("Fuel, Tmin, Tsync : ", self.fuel,
                  self.timeMin, self.synchroTime)

        return self.state

    # TODO ? :
    # Visualize the environment, we can consider a 2D env in which
    # the situation can evolve.
    def render(self, mode='human', close=False):
        # Render the environment to the screen
        pass

    # Reward function for the environment, we want to consider
    # all parameters from the episode's gameplan
    # TODO
    # Give more reward if the parameters used for the maneuvers
    # correspond to the interval set by the gameplan parameters.
    # For example speed, altitude, radius according to meteo, strength...
    # Give a super negative reward if fuel consumed >= fuel available
    # Give a reward if total time > time min (time on zone set by C2)
    # Give a reward if total time is close to synchro timing
    # Give a reward if the required maneuvers are done for a type of mission
    # IE : SCAR : at least 1 SoF, CAS : at least 2 Wheel
    def reward(self, action):
        # If we want a high reward, it means we want to maximize loss
        # We'll try first with loss_time * loss_fuel
        # with target and observation as parameters.
        reward = 0

        # TODO Change to make this impossible to get
        # If we consume too much fuel, super negative reward
        if self.fuel - self.state['fuel'] <= 0:
            print("Too much fuel consumed")
            reward -= 99999
        else:
            reward += 1

        # If we are not in the min time, negative reward, else good reward
        if self.timeMin > self.state['time']:
            reward -= 200
        else:
            reward += 200

        # TODO Change to make this impossible to get
        # If we have value that are not allowed within the range, neg reward
        if (action.meanspeed < action.minspeed) | (
            action.meanspeed > action.maxspeed) | (
             action.altitude < action.minaltitude) | (
             action.altitude > action.maxaltitude):
            print("Bad altitude or bad speed")
            print(self.gameplan)
            reward -= 99999

        # If we have a synchro time needed and we are close to this time
        # (More or less 30 seconds), reward
        if self.synchroTime != 0:
            diff_time_synchro = abs(self.state['time'] - self.synchroTime)
            if diff_time_synchro < 30:
                reward += 600
            else:
                reward -= 300

        mission_needed = self.missionType.getMinManeuver()
        man_done = self.count_maneuvers()
        for mission in mission_needed.keys():
            if mission in man_done:
                if man_done[mission] < mission_needed[mission]:
                    reward -= 10
                elif man_done[mission] > mission_needed[mission]:
                    reward += 5 - (man_done[mission] -
                                   mission_needed[mission] + 1) * 5
                else:
                    reward += 10

        if self.timeMin != 0:
            reward += self.state['time'] - self.synchroTime

        # TODO : Ponderer avec un ratio
        return round(reward)

    # Set a new gameplan for the current episode.
    # Change with reset
    def get_new_gameplan(self):
        r = np.random.randint(0, len(self.gameplan_list))

        self.gameplan = self.gameplan_list[r]
        self.plane = self.gameplan['Plane']
        self.goalDistance = self.gameplan['GoalDistance']
        self.rtbDistance = self.gameplan['RtBDistance']
        self.fuel = self.gameplan['FuelAvailable']
        self.meteo = self.gameplan['Meteo']
        self.missionType = self.gameplan['MissionType']
        self.strength = self.gameplan['Strength']
        self.timeMin = self.gameplan['TimeMin']  # seconds
        self.synchroTime = self.gameplan['SynchroTime']  # seconds

    # Count occurences of maneuvers done
    def count_maneuvers(self):
        count = dict()
        for man in self.maneuver_list:
            if man.name in count:
                count[man.name] += 1
            else:
                count[man.name] = 1
        return count

    # Set new action space for our environment.
    # TODO According to gameplan parameters
    def reset_action_space(self):
        # Change function in order to consider parameters
        # For example, strength, meteo etc.
        self.action_change = dict().fromkeys(self.action_index, 0)
        # Number of maneuvers that can be done
        maneuvers_nb = len(self.missionType.getManeuvers())

        # Speed interval (/5 to narrow done the interval)
        # TODO : WIP
        # Decrease MAXSPEED if strong
        # Increase MINSPEED if weak or equal
        spd_interval = (self.plane.MAXSPEED - self.plane.MINSPEED)
        if self.strength != "Weak":
            self.action_change['speed'] = 10
        else:
            self.action_change['speed'] = 30

        spd_interval -= self.action_change['speed']
        spd_interval /= 5

        # Altitude interval (/100 to narrow done the interval)
        # TODO
        # Decrease a lot MAXALT if bad weather
        alt_interval = (self.plane.MAXALTITUDE - self.plane.MINALTITUDE)
        if self.meteo != "Sunny":
            self.action_change['altitude'] = 10000
        alt_interval -= self.action_change['altitude']
        alt_interval /= 100

        # Distance interval (Only usable for SimpleMove)
        # TODO
        dist_interval = 15

        # Gap interval (Used in Spiral and Zigzag)
        # TODO
        # Decrease if bad weather
        gap_interval = 4
        if self.meteo != "Sunny":
            self.action_change['gap'] = 2
        gap_interval -= self.action_change['gap']

        # Width and Length interval (Used for the zone in Spiral and Zigzag)
        # TODO
        # Maybe not affected in the prediction
        wid_len_interval = 15

        # Radius interval (Used for Wheel)
        # TODO
        # Decrease if bad weather
        # Increase if weaker
        rad_interval = 3
        if self.meteo != "Sunny" or self.strength == "Weak":
            self.action_change['radius'] = 1.5
        rad_interval += self.action_change['radius']

        self.action_space = spaces.MultiDiscrete(
            [
                maneuvers_nb,
                spd_interval,
                alt_interval,
                dist_interval,
                gap_interval,
                wid_len_interval,
                wid_len_interval,
                rad_interval
             ])

    # Check if current episode is done
    # TODO, for now considering only fuel remaining and time
    # Check when is the episode considered done
    # Amount of fuel consumed, time of presence etc
    # Do we consider at least one constraint ?
    # Fuel constraint, time min constraint or sync constraint ?
    def is_done(self):
        done = self.done_fuel() or (
               self.done_min_time() and self.done_sync_time())
        return done

    # Check for current episode time if synchro time is near or done
    def done_sync_time(self):
        # Define what to do when there is no up-limit for time
        # Define what to do when there is no down-limit for time
        if self.synchroTime == 0:
            return False
        else:
            return (abs(self.state['time'] - self.synchroTime) <= 30) or (
                    self.state['time'] > self.synchroTime)

    # Check for current episode time if minimum time is done
    def done_min_time(self):
        if self.timeMin == 0:
            return True
        else:
            return self.state['time'] >= self.timeMin

    # Check for current episode if fuel consumed is above the limit
    # TODO : Change and set it done before everything is consumed
    def done_fuel(self):
        return ((self.state['fuel'] - self.fuel) < 1 and
                self.state['fuel'] - self.fuel >= 0) or (
                self.state['fuel'] >= self.fuel)
