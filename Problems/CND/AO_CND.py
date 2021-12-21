from Planner import pyhop as treehop
import copy
import random


def take(state, agent, b):
    preconditions = {'on': {b: None}, "mass_u": {b: state.max_mass[agent] - state.mass_u[agent]}}
    if treehop.contained(state, preconditions):
        effect1 = {'collected': {b: True}, "mass_u": {agent: state.mass_u[agent] + state.mass_u[b]}, "mass_d":
            {agent: state.mass_d[agent] + state.mass_d[b]}, 'under': {b: None}, 'on': {}}
        if state.under[b]:
            effect1['on'][state.under[b]] = None
        return [effect1], preconditions, [1]
    return


treehop.declare_operators(take)


def achieve_goal(state, agent):  # goal is tower of n blocks
    plan = []
    color = [state.color[x] for x in state.collected if state.collected[x]]
    if not color:
        color = random.choice(['red', 'yellow', 'blue'])
    else:
        color = color[0]
    collect = [x for x in state.on if not state.on[x] and state.color[x] == color and not state.collected[x]]
    if collect:
        plan = [('take', agent, collect[0]), ('achieve_goal', agent)]
    return plan


treehop.declare_methods('achieve_goal', achieve_goal)

