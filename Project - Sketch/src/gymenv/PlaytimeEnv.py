from audioop import getsample
from decimal import DefaultContext
import gym
import numpy as np
from gym import spaces
from scipy import rand
from objects.AllManeuvers import Wheel
from function.j_methods import compute_maneuver
from .observation import Observation
from function.j_methods import *
from scipy.optimize import minimize
from deprecated import deprecated

# Parameters
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

        # TODO : add other parameters for gameplan like objectives,
        # time constraint etc
        self._target = self._get_target()
        print('Target ', self._target)
        # self.reset_action_state()
        # w = Wheel(self.action_state['speed'],
        #           self.action_state['altitude'],
        #           self.action_state['distance'])
        # self.state = np.array([w.total_fuel_consumption(ULM),
        #                        w.travelled_time()])
        # print("Beginning : ", self.action_state, self.state)

        # Let's set the action space with the maneuvers' parameters
        # Change parameters according to plane parameters or others

        self.action_space = spaces.Discrete(4)
        spaces.Dict({
            "speed": spaces.Discrete(10),
            "altitude": spaces.Discrete(50),
            "distance": spaces.Discrete(6),
        })
        # Example for using image as input:
        # self.target_space = spaces.Dict({
        self.observation_space = spaces.Dict({
            "time": spaces.Box(self.timeMin, self.plane.max_flight_time,
                               shape=(1,)),
            "fuel": spaces.Box(0, self.fuel, shape=(1,)),
        })
        # self.observation_space = spaces.Dict({
        #     "speed": spaces.Box(bounds[0, 0], bounds[0, 1]),
        #     "altitude":  spaces.Box(bounds[1, 0], bounds[1, 1]),
        #     "distance":  spaces.Box(bounds[2, 0], bounds[2, 1]),
        # })

    # Step for the current episode
    def step(self, actions):
        # Execute one time step within the environment
        info = {}
        for key, value in self.action_space.spaces.items():
            # With value.n / 2, we can get an interval of value around 0.
            # Ie : from -10 to 10

            self.action_state[key] += actions[key] - (value.n / 2)
        w = Wheel(self.action_state['speed'],
                  self.action_state['altitude'],
                  self.action_state['distance'])
        fuel = w.total_fuel_consumption(self.plane)
        time = w.travelled_time()
        self.state = [fuel, time]
        done = self.is_done()
        reward = self.reward(self.state)

        return (self.state, reward, done, info)

    # Set new episode : select new gameplan so new observation
    def reset(self):
        self.get_new_gameplan()
        self.reset_action_state()

        w = Wheel(self.action_state['speed'],
                  self.action_state['altitude'],
                  self.action_state['distance'])

        self.state = np.array([w.total_fuel_consumption(ULM),
                               w.travelled_time()])
        print("Reset, new obs : ", self.state)
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
    def reward(self, observation):
        # If we want a high reward, it means we want to maximize loss
        # We'll try first with loss_time * loss_fuel
        # with target and observation as parameters.
        fuel_found, time_found = observation
        fuel_wanted, time_wanted = self._target
        loss_f = loss_fuel_max(fuel_found, fuel_wanted)
        loss_t = loss_time_max(time_found, time_wanted)
        # Ponderer avec un ratio TODO
        return loss_f + loss_t

    # Deprecated, check for optimal condition for a single wheel
    @deprecated(version='1.0',
                reason="Target is not corresponding : only 1 wheel")
    def _get_target(self):
        j_fac = LossFunction(self.fuel, self.timeMin, min_max)
        J = j_fac.choose_J(time=time_nb)
        result = minimize(J, (180, 2000, 20), method='Powell', bounds=bounds,)
        w = Wheel(result.x[0], result.x[1], result.x[2])

        return [w.total_fuel_consumption(ULM), w.travelled_time()]

    # Deprecated
    @deprecated(version='1.0',
                reason="Action state is not corresponding")
    def reset_action_state(self):
        # Change function in order to consider parameters
        # For example, strength, meteo etc.
        self.action_state = dict()
        self.action_state['speed'] = 150 + np.random.randint(-15, 15)
        self.action_state['altitude'] = 2000 + np.random.randint(-1000, 1000)
        self.action_state['distance'] = 30 + np.random.randint(-15, 15)

    # Check if current episode is done
    # For now deprecated, as self._target is also deprecated
    # TODO, for now considering only fuel remaining and time
    def is_done(self):
        difference = [s - t for s, t in zip(self.state, self._target)]
        # difference[:, 1] = [round(d) for d in difference[:, 1]]

        done_fuel = difference[0] <= 0.5 and difference[0] >= 0
        done_time = difference[1] >= 0
        if done_fuel and done_time:
            print(difference)
        return done_fuel and done_time

    # Policy function for random choose : deprecated
    # Or can be used to do a classic env step
    def action_choose(self, observation):
        difference = [s - t for s, t in zip(observation, self._target)]
        actions = dict()
        r = dict()
        actions_n = dict()
        for key, value in self.action_space.spaces.items():
            actions_n[key] = value.n
            r[key] = np.random.randint(0, int(value.n / 2))

        if difference[0] < 0:  # Fuel consumed under the limit
            spd = actions_n['speed'] / 2 + r['speed']
            alt = actions_n['altitude'] / 2 - r['altitude']
            dis = (actions_n['distance'] + r['distance']) / 2
        elif difference[0] > 0:  # More fuel consumed
            spd = actions_n['speed'] / 2 - r['speed']
            alt = actions_n['altitude'] / 2 + r['altitude']
            dis = (actions_n['distance'] - r['distance']) / 2
        else:
            spd = actions_n['speed'] / 2
            alt = actions_n['altitude'] / 2
            dis = actions_n['distance'] / 2

        actions['speed'] = spd
        actions['altitude'] = alt
        actions['distance'] = dis
        return actions

    # Set a new gameplan for the current episode.
    # Change with reset
    def get_new_gameplan(self):
        r = np.random.randint(0, len(self.gameplan_list))
        gameplan = self.gameplan_list[r]
        self.plane = gameplan['Plane']
        self.goalDistance = gameplan['GoalDistance']
        self.rtbDistance = gameplan['RtBDistance']
        self.fuel = gameplan['Fuel']
        self.meteo = gameplan['Meteo']
        self.missionType = gameplan['MissionType']
        self.strength = gameplan['Strength']
        self.timeMin = gameplan['TimeMin']  # seconds
