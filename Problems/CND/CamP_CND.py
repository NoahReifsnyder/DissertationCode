from Problems.CND.CamO_CND import *
from random import *
from Planner.ExpectationsGenerator import *
from Planner import pyhop as treehop
import numpy as np

def run():
    state = treehop.State('state')
    state.boundaries = {}
    state.fov = {'cam1': lambda t: (np.pi/15)}  # at 0,0 in the coordinate system
    state.angle = {'cam1': lambda t: 0}
    state.left = {}
    state.right = {}
    state.actors_x = {}
    state.actors_y = {}
    num_actors = 5
    state.t = {'t': 0}
    for i in range(0, num_actors):
        slope_1 = uniform(-1, 1)
        start = uniform(-10, 10)
        state.left[i] = False
        state.right[i] = False
        state.actors_x[i] = lambda t: slope_1 / 10 * t + start + 1
        slope_2 = uniform(0, 1)
        state.actors_y[i] = lambda t: slope_2 / 10 * t + i + 1
    goals = [('achieve_goal', 'cam1')]
    treehop.declare_goals(goals)
    policy = treehop.pyhop_t(state, original_call=True)
    gen_expectations(policy, verbose=True)
