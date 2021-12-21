from Planner import pyhop as treehop
import copy
import random


def prec(state, pre):
    for d in pre:
        for key in pre[d]:
            if not getattr(state, d)[key] == pre[d][key]:
                return False
    return True


def stack(state, a, b):
    preconditions = {'on': {a: None, b: None}, 'floor': {a: False, b: False}}
    if prec(state, preconditions):
        effect1 = {'on': {}, 'under': {}}
        if state.on[a]:
            effect1['on'][state.on[a]] = None
        effect1['on'][b] = a
        effect1['under'][a] = b
        effect2 = {'under': {}, 'on': {}}
        temp = b
        while state.under[temp]:
            effect2['under'][temp] = None
            temp = state.under[temp]
            effect2['on'][temp] = None
        effect3 = {'on': {}, 'under': {}, 'floor': {}}
        if state.on[a]:
            effect3['on'][state.on[a]] = None
            effect3['under'][a] = None
        effect3['floor'][a] = True
        return [effect1, effect2, effect3], preconditions, [.9, .08, .02]
        pass
    else:
        return False


def unstack(state, a, b):
    preconditions = {'on': {b: a, a: None}}
    if prec(state, preconditions):
        effect1 = {'on': {b: None}, 'under': {a: None}}
        return [effect1], preconditions, [1]
    else:
        return False
    pass

treehop.declare_operators(stack, unstack)


def tallest(state):
    block = None
    height = 0
    cbs = []
    blocks = [b for b in state.on if not state.on[b] and not state.floor[b]]
    for b in blocks:
        temp = b
        t_height = 1
        while state.under[temp]:
            temp = state.under[temp]
            t_height += 1
        if t_height > height:
            height = t_height
            block = b
    return block, height


def achieve_goal(state, n):  # goal is tower of n blocks
    plan = []
    block, height = tallest(state)
    if height >= n:
        return []
    useable = [b for b in state.on if not state.on[b] and not state.floor[b]]
    useable.remove(block)
    if len(useable) >= (n - height):
        new = random.choice(useable)
        plan = [('stack', new, block), ('achieve_goal', n)]
        return plan
    else:
        return False


treehop.declare_methods('achieve_goal', achieve_goal)

