# Grid World Domain File With Preconditions Sent To Planner
# Conformant Planning for refuelling
from Planner import pyhop as treehop
import copy

G_eff = 1
err = .1
p_G_eff = G_eff + err
s_G_eff = G_eff - err
repair_cost = 5


def energy(state, none):
    prev = state.fuel['Beacon']
    state.fuel['Beacon'] = (prev[0] + 1, prev[1] + 1)
    return [state], {}


def refuel(state, agent):
    t_p_g_eff = p_G_eff
    t_s_g_eff = s_G_eff
    if state.repair[agent]:
        t_p_g_eff += repair_cost
        t_s_g_eff += repair_cost
    if state.fuel[agent][0] < p_G_eff:
        preconditions = {'fuel': {agent: ('-inf', t_p_g_eff)}}
        state.fuel[agent] = state.max_fuel[agent]
        return [state], preconditions
    else:
        return False


def light(state, agent, beacon):
    if not state.lit[beacon] and state.agent[agent] == state.beacons[beacon] and state.fuel['Beacon'][0] >= 1:
        preconditions = {'lit': {beacon: 0}, 'agent': {agent: state.beacons[beacon]}, 'fuel': {'Beacon': (1, 'inf')}}
        state.lit[beacon] = 1
        prev = state.fuel['Beacon']
        state.fuel['Beacon'] = (prev[0] - 1, prev[1] - 1)
        return[state], preconditions
    else:
        return False


def repair(state, agent):
    if state.repair[agent]:
        preconditions = {'repair': {agent: True}}
        state.repair[agent] = False
        return [state], preconditions
    else:
        return False


def move_north(state, agent, t):
    if state.fuel[agent.down] >= 1.1*t and state.aty[agent.up] <= 10 - (1.1*t):
        effects = {'fuel': {}, 'aty': {}}
        preconditions = {'fuel': {agent.down: (1.1*t)}, 'at-y' : {agent.up: (10 - (1.1*t))}}
        effects['fuel'][agent.up] = lambda x: -.9 * x
        effects['fuel'][agent.down] = lambda x: -1.1 * x
        effects['aty'][agent.up] = lambda x: 1.1 * x
        effects['aty'][agent.down] = lambda x: .9 * x
        return [effects], preconditions, effects
    else:
        return False


def move_back(state, agent):
    t_p_g_eff = p_G_eff
    t_s_g_eff = s_G_eff
    if state.repair[agent]:
        t_p_g_eff += repair_cost
        t_s_g_eff += repair_cost
    loc = state.agent[agent]
    if loc in state.in_front:
        preconditions = {'agent': {agent: loc}, 'in_front': {loc: state.in_front[loc]}, 'fuel': {agent: (t_p_g_eff, 'inf')}}
        state.fuel[agent] = (state.fuel[agent][0] - t_p_g_eff, state.fuel[agent][1] - t_s_g_eff)
        state.agent[agent] = state.in_front[loc]
        return [state], preconditions
    else:
        return False


def move_up(state, agent):
    t_p_g_eff = p_G_eff
    t_s_g_eff = s_G_eff
    if state.repair[agent]:
        t_p_g_eff += repair_cost
        t_s_g_eff += repair_cost
    loc = state.agent[agent]
    if loc in state.below:
        preconditions = {'agent': {agent: loc}, 'below': {loc: state.below[loc]}, 'fuel': {agent: (t_p_g_eff, 'inf')}}
        state.fuel[agent] = (state.fuel[agent][0] - t_p_g_eff, state.fuel[agent][1] - t_s_g_eff)
        state.agent[agent] = state.below[loc]
        return [state], preconditions
    else:
        return False


def move_down(state, agent):
    t_p_g_eff = p_G_eff
    t_s_g_eff = s_G_eff
    if state.repair[agent]:
        t_p_g_eff += repair_cost
        t_s_g_eff += repair_cost
    loc = state.agent[agent]
    if loc in state.above:
        preconditions = {'agent': {agent: loc}, 'above': {loc: state.above[loc]}, 'fuel': {agent: (t_p_g_eff, 'inf')}}
        state.fuel[agent] = (state.fuel[agent][0] - t_p_g_eff, state.fuel[agent][1] - t_s_g_eff)
        state.agent[agent] = state.above[loc]
        return [state], preconditions
    else:
        return False


treehop.declare_operators(move_forward, move_back, move_up, move_down, light, refuel, repair, energy)


def find_cost(start, end, n):
    s_col = (start-1) % n
    s_row = (start-1) // n
    e_col = (end-1) % n
    e_row = (end-1) // n
    dist = abs(e_col-s_col) + abs(e_row-s_row)
    return dist


def achieve_goal(state, agent, end, n):
    if state.repair[agent]:
        return [(repair, agent), ('achieve_goal', agent, end, n)]
    if state.fuel[agent][0] < p_G_eff:
        return[('refuel', agent), ('achieve_goal', agent, end, n)]
    start = state.agent[agent]
    if start == end:
        return []
    state1 = copy.copy(state)
    up = move_up(state1, agent)
    if up:
        up = up[0][0].agent[agent]
        up = find_cost(up, end, n)
    else:
        up = n**2
    state1 = copy.copy(state)
    down = move_down(state1, agent)
    if down:
        down = down[0][0].agent[agent]
        down = find_cost(down, end, n)
    else:
        down = n**2
    state1 = copy.copy(state)
    backward = move_back(state1, agent)
    if backward:
        backward = backward[0][0].agent[agent]
        backward = find_cost(backward, end, n)
    else:
        backward = n**2
    state1 = copy.copy(state)
    forward = move_forward(state1, agent)
    if forward:
        forward = forward[0][0].agent[agent]
        forward = find_cost(forward, end, n)
    else:
        forward = n**2
    m = min(up, down, forward, backward)
    move = 0
    if m == up:
        move = 'move_up'
    if m == down:
        move = 'move_down'
    if m == forward:
        move = 'move_forward'
    if m == backward:
        move = 'move_back'
    return[(move, agent), ('achieve_goal', agent, end, n)]


treehop.declare_methods('achieve_goal', achieve_goal)


def light_all(state, agent, n):
    build = []
    t_energy = state.fuel['Beacon'][0]
    for b in state.lit:
        if state.lit[b] == 0:
            build.append(('achieve_goal', agent, state.beacons[b], n))
            if t_energy < 1:
                build.append(('energy', None))
                t_energy += 1
            build.append(('light', agent, b))
            t_energy -= 1
    return build


treehop.declare_methods('light_all', light_all)
