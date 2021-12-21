# Grid World Domain File With Preconditions Sent To Planner
# Conformant Planning for refuelling
import math
from TreeHop.Planner import pyhop as treehop
from TreeHop.Planner.InverseFunc import inversefunc
import copy

err = .1
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


def light(state, agent, b):
    preconditions = {'lit': {b: 0}, 'aty_u': {b: state.aty_u[agent]}, 'aty_d': {b: state.aty_d[agent]},
                     'atx_u': {b: state.atx_u[agent]}, 'atx_d': {b: state.atx_d[agent]}}
    if treehop.contained(state, preconditions):
        effect1 = {'lit': {b: 1}}
        return [effect1], preconditions, [1]
    else:
        return False


def repair(state, agent):
    if state.repair[agent]:
        preconditions = {'repair': {agent: True}}
        state.repair[agent] = False
        return [state], preconditions
    else:
        return False


def move_east(state, agent):
    if state.repair[agent]:
        t_p_g_eff += repair_cost
        t_s_g_eff += repair_cost
    n = state.size['size']
    preconditions = {'atx_u': {agent: n - 1}, 'fuel_d': {agent: 1 + err}}
    if treehop.contained(state, preconditions):
        effect1 = {}
        effect1['fuel_d'] = {agent: lambda x: x - 1 - err}
        effect1['fuel_u'] = {agent: lambda x: x - 1 + err}
        effect1['atx_d'] = {agent: lambda x: x + 1}
        effect1['atx_u'] = {agent: lambda x: x + 1}
        return [effect1], preconditions, [1]
    else:
        return False


def move_west(state, agent):
    if state.repair[agent]:
        t_p_g_eff += repair_cost
        t_s_g_eff += repair_cost
    n = state.size['size']
    preconditions = {'atx_d': {agent: 1}, 'fuel_d': {agent: 1 + err}}
    if treehop.contained(state, preconditions):
        effect1 = {}
        effect1['fuel_d'] = {agent: lambda x: x - 1 - err}
        effect1['fuel_u'] = {agent: lambda x: x - 1 + err}
        effect1['atx_d'] = {agent: lambda x: x - 1}
        effect1['atx_u'] = {agent: lambda x: x - 1}
        return [effect1], preconditions, [1]
    else:
        return False


def move_north(state, agent):
    if state.repair[agent]:
        t_p_g_eff += repair_cost
        t_s_g_eff += repair_cost
    n = state.size['size']
    preconditions = {'aty_u': {agent: n - 1}, 'fuel_d': {agent: 1 + err}}
    if treehop.contained(state, preconditions):
        effect1 = {}
        effect1['fuel_d'] = {agent: lambda x: x - 1 - err}
        effect1['fuel_u'] = {agent: lambda x: x - 1 + err}
        effect1['aty_d'] = {agent: lambda x: x + 1}
        effect1['aty_u'] = {agent: lambda x: x + 1}
        return [effect1], preconditions, [1]
    else:
        return False


def move_south(state, agent):
    if state.repair[agent]:
        t_p_g_eff += repair_cost
        t_s_g_eff += repair_cost
    n = state.size['size']
    preconditions = {'aty_d': {agent: 1}, 'fuel_d': {agent: 1 + err}}
    if treehop.contained(state, preconditions):
        effect1 = {}
        effect1['fuel_d'] = {agent: lambda x: x - 1 - err}
        effect1['fuel_u'] = {agent: lambda x: x - 1 + err}
        effect1['aty_d'] = {agent: lambda x: x - 1}
        effect1['aty_u'] = {agent: lambda x: x - 1}
        return [effect1], preconditions, [1]
    else:
        return False


treehop.declare_operators(move_east, move_west, move_north, move_south, light, refuel, repair, energy)


def find_cost(start, end, agent):
    startx = (start['atx_u'][agent] + start['atx_d'][agent]) / 2
    starty = (start['aty_u'][agent] + start['aty_d'][agent]) / 2
    endx = (end['atx_u'][agent] + end['atx_d'][agent]) / 2
    endy = (end['aty_u'][agent] + end['aty_d'][agent]) / 2
    dist = abs(startx - endx) + abs(starty - endy)
    print('awefawefaw', dist)
    return dist


def achieve_goal(state, agent, b):
    if state.repair[agent]:
        return [(repair, agent), ('achieve_goal', agent, b)]
    max_cost = state.size['size'] ** 2
    endx_u = state.atx_u[b]
    endx_d = state.atx_d[b]
    endy_u = state.aty_u[b]
    endy_d = state.aty_d[b]
    end = {'atx_d': {agent: endx_d}, 'atx_u': {agent: endx_u}, 'aty_d': {agent: endy_d}, 'aty_u': {agent: endy_u}}
    if treehop.contained(state, end):
        return []
    state1 = copy.deepcopy(state)
    north = move_north(state1, agent)
    if north:
        state1.apply_effects(north[0][0])
        startx_u = state1.atx_u[agent]
        startx_d = state1.atx_d[agent]
        starty_u = state1.aty_u[agent]
        starty_d = state1.aty_d[agent]
        start = {'atx_d': {agent: startx_d}, 'atx_u': {agent: startx_u}, 'aty_d': {agent: starty_d},
                 'aty_u': {agent: starty_u}}
        north = find_cost(start, end, agent)
    else:
        north = max_cost
    state1 = copy.deepcopy(state)
    south = move_south(state1, agent)
    if south:
        state1.apply_effects(south[0][0])
        startx_u = state1.atx_u[agent]
        startx_d = state1.atx_d[agent]
        starty_u = state1.aty_u[agent]
        starty_d = state1.aty_d[agent]
        start = {'atx_d': {agent: startx_d}, 'atx_u': {agent: startx_u}, 'aty_d': {agent: starty_d},
                 'aty_u': {agent: starty_u}}
        south = find_cost(start, end, agent)
    else:
        south = max_cost
    state1 = copy.deepcopy(state)
    west = move_west(state1, agent)
    if west:
        state1.apply_effects(west[0][0])
        startx_u = state1.atx_u[agent]
        startx_d = state1.atx_d[agent]
        starty_u = state1.aty_u[agent]
        starty_d = state1.aty_d[agent]
        start = {'atx_d': {agent: startx_d}, 'atx_u': {agent: startx_u}, 'aty_d': {agent: starty_d},
                 'aty_u': {agent: starty_u}}
        west = find_cost(start, end, agent)
    else:
        west = max_cost
    state1 = copy.deepcopy(state)
    east = move_east(state1, agent)
    if east:
        state1.apply_effects(east[0][0])
        startx_u = state1.atx_u[agent]
        startx_d = state1.atx_d[agent]
        starty_u = state1.aty_u[agent]
        starty_d = state1.aty_d[agent]
        start = {'atx_d': {agent: startx_d}, 'atx_u': {agent: startx_u}, 'aty_d': {agent: starty_d},
                 'aty_u': {agent: starty_u}}
        east = find_cost(start, end, agent)
    else:
        east = max_cost
    m = min(north, south, east, west)
    move = 0
    if m == north:
        move = 'move_north'
    if m == south:
        move = 'move_south'
    if m == east:
        move = 'move_east'
    if m == west:
        move = 'move_west'
    return[(move, agent), ('achieve_goal', agent, b)]


treehop.declare_methods('achieve_goal', achieve_goal)


def light_all(state, agent):
    build = []
    for b in state.lit:
        if state.lit[b] == 0:
            build.append(('achieve_goal', agent, b))
            build.append(('light', agent, b))
    return build


treehop.declare_methods('light_all', light_all)
