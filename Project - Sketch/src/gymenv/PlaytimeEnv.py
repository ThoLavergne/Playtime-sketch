import gym
import numpy as np
from gym import spaces
from function.tools import get_key_from_value
from objects.AllManeuvers import *


class PlaytimeEnv(gym.Env):
    """Custom Environment that follows gym interface,
    used for Playtime function, Pronostic"""
    metadata = {'render.modes': ['human']}

    def __init__(self, gameplan_list: list, verbose: int = 0):
        """Create environment

        Parameters
        ----------
        gameplan_list : list
            List of all gameplans, will set the observation state
            at each reset.
        verbose : int, optional
            Print more information if != 0, by default 0
        """
        super(PlaytimeEnv, self).__init__()

        # Verbose if we want to print some parameters in functions.
        self.verbose = verbose
        # Gameplan list are all the possible mission we want the environment
        # to learn.
        self.gameplan_list = gameplan_list
        # Set maneuver list or maneuvers done to an empty list.
        self.maneuver_list = []

        # We create dictionnaries for an enconding similar to onehot
        # in order to create our observation space for string values in
        # the gameplans of gameplan_list
        # Begin onehot index
        planes = list(set(gp['Plane'] for gp in self.gameplan_list))
        # Ie : Dictionnary for every plane
        self.plane_index = dict()
        for i, p in enumerate(planes):
            self.plane_index[i] = p

        strength = list(set(gp['Strength'] for gp in self.gameplan_list))
        # Dictionnary for every power relations
        self.strength_index = dict()
        for i, s in enumerate(strength):
            self.strength_index[i] = s

        meteo = list(set(gp['Meteo'] for gp in self.gameplan_list))
        # Dictionnary for every meteo
        self.meteo_index = dict()
        for i, m in enumerate(meteo):
            self.meteo_index[i] = m

        missionType = list(set(gp['MissionType'] for gp in self.gameplan_list))
        # Dictionnary for every mission type
        self.missionType_index = dict()
        for i, mt in enumerate(missionType):
            self.missionType_index[i] = mt

        maneuvers = list(set(filter(lambda x:
                             (x.name in gp['MissionType'].getManeuvers()
                              for gp in self.gameplan_list), LIST_MAN)))
        # Dictionnary for every usable maneuvers according to mission type
        self.maneuvers_index = dict()
        for i, ma in enumerate(maneuvers):
            self.maneuvers_index[i] = ma

        # End onehot index

        # Numerical values for non-string values of gameplan.

        # We fetch the max fuel quantity in order to create the
        # first observation space. (To change if dynamic space is possible)
        # We add +1 in every numerical values : Discrete(n) goes from 0 to n-1
        maxfuel = 0
        for plane in self.plane_index.values():
            if plane.fuel_max > maxfuel:
                maxfuel = plane.fuel_max + 1

        max_goal_dist = max(gp['GoalDistance'] for
                            gp in self.gameplan_list) + 1
        max_rtb_dist = max(gp['RtBDistance'] for
                           gp in self.gameplan_list) + 1
        max_min_time = max(gp['TimeMin'] for
                           gp in self.gameplan_list) + 1
        max_sync_time = max(gp['SynchroTime'] for
                            gp in self.gameplan_list) + 1

        max_time_available = max(p.max_flight_time for
                                 p in self.plane_index.values()) + 1

        # TODO : We have to consider maneuvers parameters to optimize
        # TODO : Try to see if dynamic observation space are possible
        # (Change the space depending on parameters,
        # for example maxfuel, maxtime)
        self.observation_space = spaces.Dict({
            "time": spaces.Discrete(max_time_available),
            "fuel": spaces.Discrete(maxfuel),
            # TODO : change, if there is another plane, there will be problem
            "Plane": spaces.Discrete(len(self.plane_index)),
            "GoalDistance": spaces.Discrete(max_goal_dist),
            "RtBDistance": spaces.Discrete(max_rtb_dist),
            "FuelAvailable": spaces.Discrete(maxfuel),
            "Meteo": spaces.Discrete(len(self.meteo_index)),
            "MissionType": spaces.Discrete(len(self.missionType_index)),
            "Strength": spaces.Discrete(len(self.strength_index)),
            "TimeMin": spaces.Discrete(max_min_time),
            "SynchroTime": spaces.Discrete(max_sync_time),
        })

        # Name of all parameters in the action space.
        # In the same order as action_space
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

        # This action space is a MultiDiscrete because most agents can't handle
        # Dict action space (like observation_space).
        # To counter this part, we create an index to zip with the action.
        # TODO : Try to see if dynamic action spaces are possible :
        # Change the size of the spaces depending on gameplan parameters.
        # For example, for the speed we will not check in the entire gameplan
        # list, but only the one we picked at the reset.
        self.action_space = spaces.MultiDiscrete(
            [
                # Max number of maneuvers
                len(self.maneuvers_index),
                # Max speed interval, /5 for scale
                max(p.MAXSPEED - p.MINSPEED for p in
                    self.plane_index.values()) / 5,
                # Max altitude interval, /100 for scale
                max(p.MAXALTITUDE - p.MINALTITUDE for p in
                    self.plane_index.values()) / 100,
                # Max goal_dist or rtb_dist for simple move.
                max(max_goal_dist, max_rtb_dist),
                # Max gap distance
                2,
                # Max length
                15,
                # Max width
                15,
                # Max radius
                4
            ]
        )

        print(self.observation_space)
        print(self.action_space)

        # This dictionnary is used to add intervals
        self.action_space_interval = dict().fromkeys(self.action_index, 0)

    # Step for the current episode
    # Can change some parameters, for example changing power balance,
    # wind strength / direction, among others
    # TODO : Change for each maneuver
    def step(self, action):
        """Step for the current episode.
        TODO : Change some parameters (power balance,
        wind strength / direction...)

        Parameters
        ----------
        action : List [int]
            Contains all values corresponding to the action space.
            [ maneuver, speed, altitude, distance, gap, length, width, radius]
        Returns
        -------
         (New state after the action, reward, done, info)
            Will give the result of the action on the environment,
            with the new state, the reward linked to this action and
            if the episode is over.
        """
        # Execute one time step within the environment
        # Action is the new maneuver to add.

        action = dict(zip(self.action_index, action))
        action = self.action_to_real_space(action)
        # Action becomes a dict
        # Get type of maneuver predicted by the agent
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
        info = {}
        # print("Current state : ", self.state)
        return (self.state, reward, done, info)

    # Raise the action_space to the real interval
    def action_to_real_space(self, action):
        """Raise the actions to the real value we need.

        Parameters
        ----------
        action : Dict [String, int]
            Contains all values corresponding to the action space
            with the corresponding key.
            [ maneuver, speed, altitude, distance, gap, length, width, radius]

        Returns
        -------
        Dict
            Return action but with a few tweaks in the value.
        """
        action['speed'] *= 5
        action['speed'] += self.plane.MINSPEED

        action['altitude'] *= 100
        action['altitude'] += self.plane.MINALTITUDE

        action['distance'] += 15

        action['gap'] += 1

        action['length'] += 15
        action['width'] += 15

        action['radius'] += 2
        action['radius'] *= 0.5

        return action

    def reset(self, verbose=1):
        """Set new episode : select new gameplan so new observation

        Parameters
        ----------
        verbose : int, optional
            Print additionnal information if 1, by default 1

        Returns
        -------
        state
            Return new state after reset, new gameplan information,
            set fuel and time to 0.
        """
        # print("RESET ENV")
        self.get_new_gameplan()
        # self.reset_action_space()
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
            print("Fuel=", self.fuel,
                  "Tmin=", self.timeMin,
                  "Tsync=", self.synchroTime)

        return self.state

    def render(self, mode='human', close=False):
        """ TODO
        Visualize the environment, we can consider a 2D env in which
        the situation can evolve.
        Parameters
        ----------
        mode : str, optional
            _description_, by default 'human'
        close : bool, optional
            _description_, by default False
        """
        # Render the environment to the screen
        pass

    def reward(self, action) -> float:
        """WIP TODO :
        Reward function for the environment, we want to consider all parameters
        for the episode's gameplan.
        TODO : Try to tweak the function in order to give correct rewards.

        Give more reward if the parameters used for the maneuvers
        correspond to the interval set by the gameplan parameters.
        For example speed, altitude, radius according to meteo, strength...
        Give a super negative reward if fuel consumed >= fuel available
        Give a reward if total time > time min (time on zone set by C2)
        Give a reward if total time is close to synchro timing
        Give a reward if the required maneuvers are done for a type of mission
        IE : SCAR : at least 1 SoF, CAS : at least 2 Wheel

        Parameters
        ----------
        action : Dict [String, int]
            Contains all values corresponding to the action space
            with the corresponding key.
            [ maneuver, speed, altitude, distance, gap, length, width, radius]

        Returns
        -------
        Number
            Reward given to the agent after the action
        """
        # If we want a high reward, it means we want to maximize loss
        # We'll try first with loss_time * loss_fuel
        # with target and observation as parameters.
        reward = 0

        # TODO Change to make this impossible to get
        # If we consume too much fuel, super negative reward
        if self.state['fuel'] > self.fuel:
            if self.verbose:
                print("Too much fuel consumed")
            reward -= 9999
        else:
            reward += 100

        # If we are not in the min time, negative reward, else good reward
        # if self.timeMin > self.state['time']:
        #     reward -= 200
        # else:
        #     reward += 200

        # TODO Change to make this impossible to get
        # If we have value that are not allowed within the range, neg reward
        minspeed = action.minspeed
        maxspeed = action.maxspeed
        minaltitude = action.minaltitude
        maxaltitude = action.maxaltitude
        if self.strength == "Weak":
            minspeed += 30
        elif self.strength == "Equal":
            minspeed += 15
        else:
            maxspeed -= 10

        if self.meteo != "Sunny":
            maxaltitude -= 10000

        if (action.meanspeed < minspeed) | (
            action.meanspeed > maxspeed) | (
             action.altitude < minaltitude) | (
             action.altitude > maxaltitude):
            if self.verbose:
                print("Bad altitude or bad speed")
            # print(self.gameplan)
            reward -= 4999

        # If we have a wheel, check radius according to gameplan parameters
        if action.name == Maneuver_Mission.Wheel:  # and (
            # (self.strength == "Weak" and action.radius < 3.5)
            #     or
            if self.meteo != "Sunny" and action.radius != 1:
                if self.verbose:
                    print("Bad radius for this wheel")
                reward -= 4999

        elif (action.name == Maneuver_Mission.Spiral or
              action.name == Maneuver_Mission.Zigzag) and (
                self.meteo != "Sunny" and action.gap > 2):
            if self.verbose:
                print("Bad gap")
            reward -= 4999

        # If we have a synchro time needed and we are close to this time
        # (More or less 30 seconds), reward
        if self.synchroTime != 0:
            diff_time_synchro = abs(self.state['time'] - self.synchroTime)
            if diff_time_synchro < 30:
                reward += 6000
            else:
                reward -= 100

        mission_needed = self.missionType.getMinManeuver()
        man_done = self.count_maneuvers()
        for mission in mission_needed.keys():
            if mission in man_done:
                # If the mission is done at least once, we give a reward
                reward += 500
                if man_done[mission] < mission_needed[mission]:
                    reward -= 100
                elif man_done[mission] > mission_needed[mission]:
                    reward += 50 - (man_done[mission] -
                                    mission_needed[mission] + 1) * 50
                else:
                    reward += 100
            else:
                # If the mission is not yet done, negative reward
                reward -= 1000

        # Man_done is with Maneuver_Mission keys

        if len(man_done.keys()) == 1:
            key, value = list(man_done.items())[0]
            if value > 2 and (
                key == Maneuver_Mission.ShowOfForce
                    or key == Maneuver_Mission.Zigzag):
                reward -= 9999

        # if self.timeMin != 0:
        # reward += self.state['time'] - self.timeMin

        # TODO : ponderate with ratio
        return round(reward)

    # Set a new gameplan for the current episode.
    # Change with reset
    def get_new_gameplan(self):
        """ Draw a random gameplan in the gameplan list and set current state
        with new parameters
        """
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

    def count_maneuvers(self):
        """ Use the maneuver list to check and count the maneuvers done
        during this episode.

        Returns
        -------
        Dict [Maneuver_Mission, int]
            Number of occurences for each maneuver done
        """
        count = dict()
        for man in self.maneuver_list:
            if man.name in count:
                count[man.name] += 1
            else:
                count[man.name] = 1
        return count

    def done_sync_time(self) -> bool:
        """Check for current episode time if synchro time is near or done

        Returns
        -------
        bool
            Synchronization time is near or passed or 0
        """
        if self.synchroTime == 0:
            return False
        else:
            return (abs(self.state['time'] - self.synchroTime) <= 30) or (
                    self.state['time'] > self.synchroTime)

    def done_min_time(self) -> bool:
        """Check for current episode time if minimum time is done

        Returns
        -------
        bool
            Minimum time is 0 or passed
        """
        if self.timeMin == 0:
            return True
        else:
            return self.state['time'] >= self.timeMin

    def done_fuel(self) -> bool:
        """Check for current episode if fuel consumed is above the limit
        TODO : Change and set it done before everything is consumed

        Returns
        -------
        bool
            Near all the fuel is consumed or too much fuel consumed
        """
        return ((self.fuel - self.state['fuel']) < 2 and
                self.fuel - self.state['fuel'] >= 0) or (
                self.state['fuel'] >= self.fuel)

    def is_done(self) -> bool:
        """
        Check if current episode is done
        TODO, for now considering only fuel remaining and time
        Check when is the episode considered done
        Amount of fuel consumed, time of presence etc
        Do we consider at least one constraint ?
        Fuel constraint, time min constraint or sync constraint ?

        Returns
        -------
        bool
            Is the episode done according to the conditions
        """
        done = self.done_fuel() or (
               self.done_min_time() and self.done_sync_time())
        return done
