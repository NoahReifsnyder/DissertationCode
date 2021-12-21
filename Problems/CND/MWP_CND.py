# Grid World Problem File
from Problems.NND.MWO_NND import *
from random import *
from Planner.ExpectationsGenerator import *
state = None
policy = None

def run():
    global state, policy
    n = 10
    state = treehop.State('state')
    state.aty_d = {'Agent1': None, 'B1': None, 'B2': None, 'B3': None}
    state.aty_u = {'Agent1': None, 'B1': None, 'B2': None, 'B3': None}
    state.atx_d = {'Agent1': None, 'B1': None, 'B2': None, 'B3': None}
    state.atx_u = {'Agent1': None, 'B1': None, 'B2': None, 'B3': None}
    state.lit = {"B1": 0, "B2": 0, "B3": 0}
    state.fuel_d = {'Agent1': 6 * (n - 1)}
    state.fuel_u = {'Agent1': 6 * (n - 1)}
    state.repair = {'Agent1': False}
    for i in state.aty_d:
        y_pos = uniform(0, n)
        x_pos = uniform(0, n)
        state.aty_d[i] = uniform(y_pos - .1, y_pos)
        state.aty_u[i] = uniform(y_pos, y_pos + .1)
        state.atx_d[i] = uniform(x_pos - .1, x_pos)
        state.atx_u[i] = uniform(x_pos, x_pos + .1)

    print('here')
    print(state)
    treehop.reset()
    goals = [('light_all', 'Agent1', n)]
    treehop.declare_goals(goals)
    #policy = treehop.pyhop_t(state, original_call=True)
    #treehop.print_policy(policy, state)
    #gen_expectations(policy)
    #print(policy[state].expectations.regression)
