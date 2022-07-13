import gym
import numpy as np
from gym import spaces
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
        self.maneuver_list = []
        # TODO : add other parameters for gameplan like objectives,
        # time constraint, changing wind
        self.reset_action_space()
        # Let's set the action space with the maneuvers' parameters
        # Change parameters according to plane parameters or others
        # Dicrete 4 for 4 maneuvers available
        # TODO : We have to consider maneuvers parameters to optimize

        self.observation_space = spaces.Dict({
            "time": spaces.Discrete(20000),
            "fuel": spaces.Discrete(200),
        })

        self.maneuvers_index = {
            0: Wheel,
            1: ShowOfForce,
            2: Spiral,
            3: ZigZag
        }

    # Step for the current episode
    # Can change some parameters, for example changing power balance,
    # wind strength / direction, among others
    # TODO : Change for each maneuver
    def step(self, action):
        # Execute one time step within the environment
        # Action is the new maneuver to add.
        info = {}
        print("Action in step :", action)

        maneuver = self.maneuvers_index[action['maneuver']]
        if maneuver == Wheel:
            maneuver = maneuver(action['speed'], action['altitude'],
                                action['radius'])
        elif maneuver == ShowOfForce:
            maneuver = maneuver()
        elif maneuver == Spiral:
            maneuver = maneuver(action['speed'], action['altitude'],
                                action['gap'], action['length'])
        elif maneuver == ZigZag:
            maneuver = maneuver(action['speed'], action['altitude'],
                                action['gap'], action['length'],
                                action['width'])

        self.maneuver_list.append(maneuver)
        fuel = maneuver.total_fuel_consumption(self.plane)
        time = maneuver.travelled_time()
        self.state_to_add = {'fuel': fuel,
                             'time': time}

        assert self.state.keys() == self.state_to_add.keys()
        for key in self.state.keys():
            self.state[key] += self.state_to_add[key]

        done = self.is_done()
        reward = self.reward(maneuver)

        return (self.state, reward, done, info)

    # Set new episode : select new gameplan so new observation
    def reset(self):
        print("RESET ENV")
        self.get_new_gameplan()
        self.reset_action_space()
        self.maneuver_list = []
        self.state = {'fuel': 0,
                      'time': 0}
        # print("Reset, new obs : ", self.state)
        return self.state

    # TODO
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
        # If we consume to much fuel, super negative reward
        if self.state['fuel'] < 0:
            reward -= 999999
        else:
            reward += 10

        # If we have value that are not allowed within the range, neg reward

        if (action.meanspeed < action.minspeed) | (
            action.meanspeed > action.maxspeed) | (
            action.altitude < action.minaltitude) | (
             action.altitude > action.maxaltitude):
            reward -= 999999

        # If we have a synchro time needed and we are close to this time
        # (More or less 30 seconds), reward
        if self.synchroTime != 0:
            diff_time_synchro = abs(self.state['time'] - self.synchroTime)
            if diff_time_synchro < 30:
                reward += 60
            else:
                reward -= 30

        mission_needed = self.missionType.getMinManeuver()
        man_done = self.count_maneuvers()
        if man_done is not None:
            for mission in mission_needed.keys():
                if man_done[mission] < mission_needed[mission]:
                    reward -= 10
                elif man_done[mission] > mission_needed[mission]:
                    reward += 5 - (man_done[mission] -
                                   mission_needed[mission] + 1) * 5
                else:
                    reward += 10

        if self.timeMin != 0:
            diff_time_min = self.state['time'] - self.synchroTime
            if diff_time_min < 0:
                reward -= 30
            else:
                reward += 30

        # fuel_found, time_found = observation
        # fuel_wanted, time_wanted = self._target
        # loss_f = loss_fuel_max(fuel_found, fuel_wanted)
        # loss_t = loss_time_max(time_found, time_wanted)
        # reward += loss_f + loss_t
        # Ponderer avec un ratio TODO
        return reward

    # Set a new gameplan for the current episode.
    # Change with reset
    def get_new_gameplan(self):
        r = np.random.randint(0, len(self.gameplan_list))
        self.gameplan = self.gameplan_list[r]
        self.plane = self.gameplan['Plane']
        self.goalDistance = self.gameplan['GoalDistance']
        self.rtbDistance = self.gameplan['RtBDistance']
        self.fuel = self.gameplan['Fuel']
        self.meteo = self.gameplan['Meteo']
        self.missionType = self.gameplan['MissionType']
        self.strength = self.gameplan['Strength']
        self.timeMin = self.gameplan['TimeMin']  # seconds
        self.synchroTime = self.gameplan['SynchroTime']  # seconds

    def count_maneuvers(self):
        count = dict()
        for man in self.maneuver_list:
            if man.name in count:
                count[man.name] += 1
            else:
                count[man.name] = 1

    def reset_action_space(self):
        # Change function in order to consider parameters
        # For example, strength, meteo etc.
        self.action_space = spaces.Dict({
            "maneuver": spaces.Discrete(4),
            "speed": spaces.Discrete(MAXSPEED - MINSPEED,
                                     start=MINSPEED),
            "altitude": spaces.Discrete(MAXALTITUDE - MINALTITUDE,
                                        start=MINALTITUDE),
            "distance": spaces.Discrete(30, start=15),
            "gap": spaces.Discrete(5, start=1),
            "length": spaces.Discrete(30, start=15),
            "width": spaces.Discrete(30, start=15),
            "radius": spaces.Discrete(3, start=2)
        })

    # Check if current episode is done
    # For now deprecated, as self._target is also deprecated
    # TODO, for now considering only fuel remaining and time
    def is_done(self):
        done_fuel = self.state['fuel'] >= self.fuel
        done_time = self.state['time'] >= self.timeMin and (
                    self.state['time'] <= self.synchroTime)
        return done_fuel and done_time

    # Deprecated, check for optimal condition for a single wheel
    def _get_target(self):
        j_fac = LossFunction(self.fuel, self.timeMin, min_max)
        J = j_fac.choose_J(time=time_nb)
        result = minimize(J, (180, 2000, 20), method='Powell', bounds=bounds,)
        w = Wheel(result.x[0], result.x[1], result.x[2])

        return [w.total_fuel_consumption(ULM), w.travelled_time()]
