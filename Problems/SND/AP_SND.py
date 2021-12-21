from Problems.SND.AO_SND import *
from random import *
from Planner.ExpectationsGenerator import *

def run():
    n = 10
    state = treehop.State('state')
    state.floor = {}
    state.on = {}
    state.under = {}
    for i in range(0, n):
        state.on[i] = None
        state.floor[i] = False
        state.under[i] = None
    goals = [('achieve_goal', int(n/3))]
    treehop.declare_goals(goals)
    policy = treehop.pyhop_t(state, goals, True)
    #print(use_state)
    #treehop.print_policy(policy, use_state)
    gen_expectations(policy, state, {})
    print(state.expectations.regression)
    print(state.expectations.goldilocks)
    #print(policy)