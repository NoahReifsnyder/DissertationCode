# Grid World Problem File
from Problems.SND.MWO_SND import *
from random import *
from Planner.ExpectationsGenerator import *
from Planner.pyhop import print_state
state = None
policy = None

def run():
    global state, policy
    n = 4
    state = treehop.State('state')
    state.north = {}
    state.west = {}
    state.south = {}
    state.east = {}
    state.aty = {'Agent1': 1, 'B1': 1, 'B2': 0, 'B3': 0}
    state.atx = {'Agent1': 1, 'B1': 1, 'B2': 0, 'B3': 1}
    state.lit = {"B1": 0, "B2": 0, "B3": 0}
    state.fuel = {'Agent1': 6*(n-1)}
    state.repair = {'Agent1': False}
    state.less = {}

    for i in range(state.fuel['Agent1']):
        state.less[i+1] = i
    #position = randint(0, n*n - 1)
    #state.aty['Agent1'] = position // n
    #state.atx['Agent1'] = position % n

    #placed = []
    #for b in state.lit:
    #    x = randint(0, n*n - 1)
    #    while x in placed:
    #        x = randint(0, n*n - 1)
    #    placed.append(x)
    #    state.aty[b] = x//n
    #    state.atx[b] = x%n
    print(state.aty)
    print(state.atx)
    for i in range(n-1):
        state.south[i+1] = i
        state.west[i+1] = i
        state.north[i] = i+1
        state.east[i] = i+1
    treehop.reset()
    goals = [('light_all', 'Agent1', n)]
    treehop.declare_goals(goals)
    policy = treehop.pyhop_t(state, original_call=True)
    print(len(policy.verticies), len(policy.edges), len(policy.verticies) * len(policy.edges))
    gen_expectations(policy, state, {})
    print(state.expectations.regression)
    for action in policy.edges[state]:
        print(action.expectations.regression)
    #print(policy.policy[state].expectations.regression)
    #treehop.print_policy(policy, state)
