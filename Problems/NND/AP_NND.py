from Problems.SND.AO_SND import *
from random import *
from Planner.ExpectationsGenerator import *

def run():
    n = 10
    t = 3
    state = treehop.State('state')
    state.floor = {}
    state.on = {}
    state.under = {}
    state.collected = {}
    state.color = {'Agent1': None}
    state.mass_u = {'Agent1': 0}
    state.mass_d = {'Agent1': 0}
    state.mass = {}
    state.max_mass = {'Agent1': n*1.5}
    colors = ['red', 'blue', 'yellow']
    for i in range(0, (t*n - t)):
        state.collected[i] = False
        state.on[i] = i+t
        state.floor[i] = False
        state.under[i+t] = i
        state.color[i] = colors[i % t]
        state.mass_u[i] = uniform(1, 1.2)
        state.mass_d[i] = uniform(.8, 1)
        state.mass[i] = uniform(state.mass_d[i], state.mass_u[i])
    for i in range(t*n - t, t*n):
        state.collected[i] = False
        state.on[i] = None
        state.under[t*n - i] = None
        state.color[i] = colors[i % t]
        state.mass_u[i] = uniform(1, 1.2)
        state.mass_d[i] = uniform(.8, 1)
        state.mass[i] = uniform(state.mass_d[i], state.mass_u[i])
    print(state)
    goals = [('achieve_goal', 'Agent1')]
    treehop.declare_goals(goals)
    policy = treehop.pyhop_t(state, goals, True)
    print(policy.verticies)
    #print(use_state)
    #treehop.print_policy(policy, use_state)
    gen_expectations(policy, verbose=True)  # Verbose prints out all expectations for every state
    print(state.expectations.regression)
    print(state.expectations.goldilocks)
    #print(policy)