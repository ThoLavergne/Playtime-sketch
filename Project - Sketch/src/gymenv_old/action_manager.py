from objects.Maneuver import Maneuver_Mission, Mission_Maneuver
from objects.AllManeuvers import *
from torch import nn
from torch import round


class ActionModel(nn.Module):

    def __init__(self, input_shape, n_actions, nb_maneuvers=4):
        super(ActionModel, self).__init__()
        # For the out number, we get the max number of parameters
        # for a maneuver + 1. The first one will be a discrete number that
        # corresponds to a certain maneuver and then, depending on this
        # number, we pick enough parameters to build our maneuver object.

        self.linearInput = nn.Linear(input_shape, 28)
        self.activation = nn.ReLU()
        self.linearOutput = nn.Linear(28, n_actions)

    def forward(self, inputs):
        x = self.linearInput(inputs)
        x = self.activation(x)

        x[0] = round(x[0])
        # print("Before view :", x, x.size())
        # x = x.view(x.size(0), -1)
        # print(x)
        return self.linearOutput(x)
