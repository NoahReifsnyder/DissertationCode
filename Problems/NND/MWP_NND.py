# Grid World Problem File
from TreeHop.Problems.NND.MWO_NND import *
from random import *
from TreeHop.Planner.ExpectationsGenerator import *
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
    state.size = {'size': n}
    placed = []
    for i in state.aty_d:
        y_pos = randint(0, n)
        x_pos = randint(0, n)
        while (x_pos, y_pos) in placed:
            y_pos = randint(0, n)
            x_pos = randint(0, n)
        placed.append((x_pos, y_pos))
        state.aty_d[i] = y_pos
        state.aty_u[i] = y_pos
        state.atx_d[i] = x_pos
        state.atx_u[i] = x_pos

    print('here')
    print(state)
    treehop.reset()
    goals = [('light_all', 'Agent1')]
    treehop.declare_goals(goals)
    policy = treehop.pyhop_t(state, original_call=True)
    #treehop.print_policy(policy, state)
    gen_expectations(policy)
    print(state.expectations.goldilocks)
