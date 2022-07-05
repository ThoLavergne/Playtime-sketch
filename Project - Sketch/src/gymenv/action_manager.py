from objects.Maneuver import Maneuver_Mission, Mission_Maneuver
from objects.AllManeuvers import *
from torch import nn
from torch import round


class ActionModel(nn.Module):

    def __init__(self, input_shape, n_actions, nb_maneuvers=4):
        super(ActionModel, self).__init__()
        print(input_shape)
        # For the out number, we get the max number of parameters
        # for a maneuver + 1. The first one will be a discrete number that
        # corresponds to a certain maneuver and then, depending on this
        # number, we pick enough parameters to build our maneuver object.

        self.linearInput = nn.Linear(input_shape, 24)
        self.activation = nn.ReLU()
        self.linearOutput = nn.Linear(24, n_actions)
        self.softmax = nn.Softmax()

    def forward(self, inputs):
        x = self.linearInput(inputs)
        x = self.activation(x)
        x = self.linearOutput(x)
        print(x)
        x[0] = round(x[0])
        print(x[1: len(x)])

        return x
