# Grid World Domain File With Preconditions Sent To Planner
# Conformant Planning for refuelling
from Planner import pyhop as treehop
import copy

cost = 0
repair_cost = 5


def not_zero(x):
    if x != 0:
        return True
    else:
        return False


def light(state, agent, beacon):
    if not state.lit[beacon] and (state.atx[agent], state.aty[agent]) == (state.atx[beacon], state.aty[beacon]):
        preconditions = {'lit': {beacon: 0}, 'atx': {agent: state.atx[beacon]}, 'aty': {agent: state.aty[beacon]}}
        effects = {'lit': {beacon: 1}}
        return[effects], preconditions, [1]
    else:
        return False


def repair(state, agent):
    if state.repair[agent]:
        preconditions = {'repair': {agent: True}}
        effects = {'repair': {agent: False}}
        return [effects], preconditions, [1]
    else:
        return False


def move_east(state, agent):
    if state.repair[agent]:
        cost += repair_cost
    if state.atx[agent] in state.east and not_zero(state.fuel[agent]):
        preconditions = {'fuel': {agent: not_zero(state.fuel[agent])}}
        effects1 = {'atx': {agent: state.east[state.atx[agent]]}, 'fuel': {agent: state.less[state.fuel[agent]]}}
        if state.aty[agent] in state.north:
            effects2 = {'aty': {agent: state.north[state.aty[agent]]}, 'fuel': {agent: state.less[state.fuel[agent]]}}
            return [effects1, effects2], preconditions, [.9, .1]
        else:
            return [effects1], preconditions, [1]
    else:
        return False


def move_west(state, agent):
    if state.repair[agent]:
        cost += repair_cost
    if state.atx[agent] in state.west and not_zero(state.fuel[agent]):
        preconditions = {'fuel': {agent: not_zero(state.fuel[agent])}}
        effects1 = {'atx': {agent: state.west[state.atx[agent]]}, 'fuel': {agent: state.less[state.fuel[agent]]}}
        if state.aty[agent] in state.south:
            effects2 = {'aty': {agent: state.south[state.aty[agent]]}, 'fuel': {agent: state.less[state.fuel[agent]]}}
            return [effects1, effects2], preconditions, [.9, .1]
        else:
            return [effects1], preconditions, [1]
    else:
        return False


def move_north(state, agent):
    if state.repair[agent]:
        cost += repair_cost
    if state.aty[agent] in state.north and not_zero(state.fuel[agent]):
        preconditions = {'fuel': {agent: not_zero(state.fuel[agent])}}
        effects1 = {'aty': {agent: state.north[state.aty[agent]]}, 'fuel': {agent: state.less[state.fuel[agent]]}}
        if state.atx[agent] in state.west:
            effects2 = {'atx': {agent: state.west[state.atx[agent]]}, 'fuel': {agent: state.less[state.fuel[agent]]}}
            return [effects1, effects2], preconditions, [.9, .1]
        else:
            return [effects1], preconditions, [1]
    else:
        return False


def move_south(state, agent):
    if state.repair[agent]:
        cost += repair_cost
    if state.aty[agent] in state.south and not_zero(state.fuel[agent]):
        preconditions = {'fuel': {agent: not_zero(state.fuel[agent])}}
        effects1 = {'aty': {agent: state.south[state.aty[agent]]}, 'fuel': {agent: state.less[state.fuel[agent]]}}
        if state.atx[agent] in state.east:
            effects2 = {'atx': {agent: state.east[state.atx[agent]]}, 'fuel': {agent: state.less[state.fuel[agent]]}}
            return [effects1, effects2], preconditions, [.9, .1]
        else:
            return [effects1], preconditions, [1]
    else:
        return False


treehop.declare_operators(move_east, move_west, move_north, move_south, light, repair)


def find_cost(start, end):
    dist = abs(start[0]-end[0]) + abs(start[1]-end[1])
    return dist


def achieve_goal(state, agent, end, n):
    if state.repair[agent]:
        return [(repair, agent), ('achieve_goal', agent, end, n)]
    if state.fuel[agent] == 0:
        return False
    startx = state.atx[agent]
    starty = state.aty[agent]
    if (startx, starty) == end:
        return []
    state1 = copy.deepcopy(state)
    north = move_north(state1, agent)
    if north:
        state1.apply_effects(north[0][0])
        north_x = state1.atx[agent]
        north_y = state1.aty[agent]
        north = find_cost((north_x, north_y), end)
    else:
        north = n**2
    state1 = copy.deepcopy(state)
    south = move_south(state1, agent)
    if south:
        state1.apply_effects(south[0][0])
        south_x = state1.atx[agent]
        south_y = state1.aty[agent]
        south = find_cost((south_x, south_y), end)
    else:
        south = n**2
    state1 = copy.deepcopy(state)
    west = move_west(state1, agent)
    if west:
        state1.apply_effects(west[0][0])
        west_x = state1.atx[agent]
        west_y = state1.aty[agent]
        west = find_cost((west_x, west_y), end)
    else:
        west = n**2
    state1 = copy.deepcopy(state)
    east = move_east(state1, agent)
    if east:
        state1.apply_effects(east[0][0])
        east_x = state1.atx[agent]
        east_y = state1.aty[agent]
        east = find_cost((east_x, east_y), end)
    else:
        east = n**2
    m = min(north, south, east, west)
    move = None
    if m == north:
        move = 'move_north'
    if m == south:
        move = 'move_south'
    if m == east:
        move = 'move_east'
    if m == west:
        move = 'move_west'
    return[(move, agent), ('achieve_goal', agent, end, n)]


treehop.declare_methods('achieve_goal', achieve_goal)


def light_all(state, agent, n):
    build = []
    for b in state.lit:
        if state.lit[b] == 0:
            build.append(('achieve_goal', agent, (state.atx[b], state.aty[b]), n))
            build.append(('light', agent, b))
    return build


treehop.declare_methods('light_all', light_all)
