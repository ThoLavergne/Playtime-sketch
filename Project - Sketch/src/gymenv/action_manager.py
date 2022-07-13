from objects.Maneuver import Maneuver_Mission, Mission_Maneuver
from objects.AllManeuvers import *
from torch import nn
from torch import round
import torch.nn.functional as F


class ActionModel(nn.Module):

    def __init__(self, input_shape, n_actions,
                 num_hidden=140, nb_maneuvers=4):
        super(ActionModel, self).__init__()
        # For the out number, we get the max number of parameters
        # for a maneuver + 1. The first one will be a discrete number that
        # corresponds to a certain maneuver and then, depending on this
        # number, we pick enough parameters to build our maneuver object.
        self.num_hidden = num_hidden
        self.second_num_hidden = int(self.num_hidden / n_actions)
        self.linearInput = nn.Linear(input_shape, self.num_hidden)
        self.activation = nn.ReLU()
        self.linearOutput = nn.Linear(self.second_num_hidden, n_actions)

        self.conv1 = nn.Conv1d(input_shape, 16, kernel_size=5, stride=2)
        self.bn1 = nn.BatchNorm1d(16)
        self.conv2 = nn.Conv1d(16, 32, kernel_size=5, stride=2)
        self.bn2 = nn.BatchNorm1d(32)
        self.conv3 = nn.Conv1d(32, 32, kernel_size=5, stride=2)
        self.bn3 = nn.BatchNorm1d(32)

        def conv2d_size_out(size, kernel_size=5, stride=2):
            return (size - (kernel_size - 1) - 1
                    ) // stride + 1
        convw = conv2d_size_out(conv2d_size_out(conv2d_size_out(n_actions)))
        convh = conv2d_size_out(conv2d_size_out(conv2d_size_out(n_actions)))
        linear_input_size = convw * convh * 32
        self.head = nn.Linear(linear_input_size, n_actions)
        print(n_actions)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv1(x))
        x = F.relu(self.conv1(x))
        # x[0] = round(x[0])
        # print("Before view :", x, x.size())
        print(x.size())
        x = x.view(int(x.size(0) / 7), 7)
        return self.linearOutput(x)
