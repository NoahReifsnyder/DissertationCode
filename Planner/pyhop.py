"""
Pyhop, version 1.2.2 -- a simple SHOP-like planner written in Python.
Author: Dana S. Nau, 2013.05.31

Copyright 2013 Dana S. Nau - http://www.cs.umd.edu/~nau

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
   
Pyhop should work correctly in both Python 2.7 and Python 3.2.p
For examples of how to use it, see the example files that come with Pyhop.

Pyhop provides the following classes and functions:

- foo = State('foo') tells Pyhop to create an empty state object named 'foo'.
  To put variables and values into it, you should do assignments such as
  foo.var1 = val1

- bar = Goal('bar') tells Pyhop to create an empty goal object named 'bar'.
  To put variables and values into it, you should do assignments such as
  bar.var1 = val1

- print_state(foo) will print the variables and values in the state foo.

- print_goal(foo) will print the variables and values in the goal foo.

- declare_operators(o1, o2, ..., ok) tells Pyhop that o1, o2, ..., ok
  are all of the planning operators; this supersedes any previous call
  to declare_operators.

- print_operators() will print out the list of available operators.

- declare_methods('foo', m1, m2, ..., mk) tells Pyhop that m1, m2, ..., mk
  are all of the methods for tasks having 'foo' as their taskname; this
  supersedes any previous call to declare_methods('foo', ...).

- print_methods() will print out a list of all declared methods.

- pyhop(state1,tasklist) tells Pyhop to find a plan for accomplishing tasklist
  (a list of tasks), starting from an initial state state1, using whatever
  methods and operators you declared previously.

- In the above call to pyhop, you can add an optional 3rd argument called
  'verbose' that tells pyhop how much debugging printout it should provide:
- if verbose = 0 (the default), pyhop returns the solution but prints nothing;
- if verbose = 1, it prints the initial parameters and the answer;
- if verbose = 2, it also prints a message on each recursive call;
- if verbose = 3, it also prints info about what it's computing.
"""
# Pyhop's planning algorithm is very similar to the one in SHOP and JSHOP
# (see http://www.cs.umd.edu/projects/shop). Like SHOP and JSHOP, Pyhop uses
# HTN methods to decompose tasks into smaller and smaller subtasks, until it
# finds tasks that correspond directly to actions. But Pyhop differs from 
# SHOP and JSHOP in several ways that should make it easier to use Pyhop
# as part of other programs:
# 
# (1) In Pyhop, one writes methods and operators as ordinary Python functions
#     (rather than using a special-purpose language, as in SHOP and JSHOP).
# 
# (2) Instead of representing states as collections of logical assertions,
#     Pyhop uses state-variable representation: a state is a Python object
#     that contains variable bindings. For example, to define a state in
#     which box b is located in room r1, you might write something like this:
#     s = State()
#     s.loc['b'] = 'r1'
# 
# (3) You also can define goals as Python objects. For example, to specify
#     that a goal of having box b in room r2, you might write this:
#     g = Goal()
#     g.loc['b'] = 'r2'
#     Like most HTN planners, Pyhop will ignore g unless you explicitly
#     tell it what to do with g. You can do that by referring to g in
#     your methods and operators, and passing g to them as an argument.
#     In the same fashion, you could tell Pyhop to achieve any one of
#     several different goals, or to achieve them in some desired sequence.
# 
# (4) Unlike SHOP and JSHOP, Pyhop doesn't include a Horn-clause inference
#     engine for evaluating preconditions of operators and methods. So far,
#     I've seen no need for it; I've found it easier to write precondition
#     evaluations directly in Python. But I could consider adding such a
#     feature if someone convinces me that it's really necessary.
# 
# Accompanying this file are several files that give examples of how to use
# Pyhop. To run them, launch python and type "import blocks_world_examples"
# or "import simple_travel_example".


import copy
import sys


############################################################
# States and goals
import types


class Policy:
    def __init__(self):
        self.starting_state = None
        self.edges = {}
        self.verticies = []
        self.policy = {}

    def add_edge(self, alpha, beta):
        if alpha not in self.edges:
            self.edges[alpha] = set()
        self.edges[alpha].add(beta)
        return


class Action:
    counter = -1
    def __init__(self, args=None, name="Default", state=None):
        self.name = name
        self.args = args
        self.children = []
        self.effects = {}
        self.eff_prob = {}
        self.preconditions = {}
        self.n_preconditions = {}
        self.state = state
        self.t = {'t': None}
        self._num = Action.counter
        Action.counter -= 1

    def __str__(self):
        return str(self.name) + " " + str(self.state.get_num())

    def get_num(self):
        return self._num

    def __hash__(self):
        return hash(self._num)


counter = 0


class State:
    """A state is just a collection of variable bindings."""
    """NEED TO BE ALL DICTIONARIES"""
    def __init__(self, name):
        global counter
        self.__name__ = name
        self._num = counter
        self._valid = True
        self._effects = {}
        self._test = None
        counter += 1

    def get_num(self):
        return self._num

    def is_valid(self):
        return self._valid

    def get_diff(self, other_state):
        diff = {}

        def add_diff(t_attr, t_var, t_val):
            if t_attr not in diff:
                diff[t_attr] = {}
            diff[t_attr][t_var] = t_val
        for attr in vars(self):
            if attr[0] == "_":
                continue
            for var in getattr(self, attr):
                val = getattr(self, attr)[var]
                if var not in getattr(other_state, attr) or getattr(other_state, attr)[var] != val:
                    add_diff(attr, var, val)
        return diff

    def __eq__(self, other_state):
        if not type(self) == type(other_state):
            return False
        for attr in vars(self):
            try:
                iter(getattr(self, attr))  # for when expectation object is added to states later
            except TypeError:
                continue
            if attr[0] == "_":
                continue
            for var in getattr(self, attr):
                val = getattr(self, attr)[var]
                if var not in getattr(other_state, attr) or getattr(other_state, attr)[var] != val:
                    return False
        return True

    def __hash__(self):
        return self._num

    def __copy__(self):
        global counter
        #print("state copy")
        newstate = copy.deepcopy(self)
        newstate._num = counter
        counter += 1
        return newstate

    def __str__(self):
        return print_state(self)

    def apply_effects(self, effects):
        for key in effects:
            for eff in effects[key]:
                x = copy.deepcopy(effects[key][eff])
                s = copy.deepcopy(getattr(self, key)[eff])
                #snd = effects[key][eff]
                #nnd = effects[key][eff](getattr(self, key)[eff])
                #cnd = lambda t: (getattr(self, key)[eff](t) + effects[key][eff](t - getattr(self, 't')['t']))
                snd = lambda z: z
                nnd = lambda z: z(s)
                cnd = lambda z: (lambda t: (s(t) + z(t - getattr(self, 't')['t'])))
                #snd = (lambda z: z, effects[key][eff])
                #nnd = (lambda z: z(getattr(self, key)[eff]), effects[key][eff])
                getattr(self, key)[eff] = case(getattr(self, key)[eff], effects[key][eff], snd, nnd, cnd)(x)



class Goal:  # TODO this is not used
    """A goal is just a collection of variable bindings."""
    def __init__(self, name):
        self.__name__ = name


# print_state and print_goal are identical except for the name
def print_state(state, indent=4):
    """Print each variable in state, indented by indent spaces."""
    retval = ""
    if state is not False:
        for (name, val) in vars(state).items():
            if name != '__name__':
                for x in range(indent):
                    retval += ' '
                retval += (state.__name__ + '.' + name + ' = ' + str(val) + '\n')
        return retval
    else:
        return "False\n"


def print_goal(goal, indent=4):
    """Print each variable in goal, indented by indent spaces."""
    if goal is not False:
        for (name, val) in vars(goal).items():
            if name != '__name__':
                for x in range(indent):
                    sys.stdout.write(' ')
                sys.stdout.write(goal.__name__ + '.' + name)
                print(' =', val)
    else:
        print('False')


def print_policy(policy, state, depth=list(), tracker=list()):  # Needs work,incorrect
    for x in depth:
        print(str(x) + " ", end="")
    if state not in policy:
        if not state:
            print("T", end="\n")
        else:
            print("Goal", end="\n")
        return
    #if state in tracker:
    #    return
    tracker.append(state)
    action = policy[state]
    depth.append(tracker.index(state))
    print(action.name)
    for child in action.children:
        print_policy(policy, child, depth=depth, tracker=tracker)

    depth.remove(tracker.index(state))

def print_policy2(policy, state, depth=list(), tracker=list()):
    if state in policy:
        print(state._num, policy[state])
        for child in Policy[state].children:
            print_policy2(policy, child)
    else:
        print(state._num)

############################################################
# Helper functions that may be useful in domain models
# TODO not used
def forall(seq, cond):
    """True if cond(x) holds for all x in seq, otherwise False."""
    for x in seq:
        if not cond(x):
            return False
    return True


def find_if(cond, seq):
    """
    Return the first x in seq such that cond(x) holds, if there is one.
    Otherwise return None.
    """
    for x in seq:
        if cond(x):
            return x
    return None


def reduct_dict(d):
    if isinstance(d, type(State('type'))):     # TODO: there is a better way for this
        for key in dir(d):
            if reduct_dict(getattr(d, key)):
                return True
    elif isinstance(d, dict):
        for key in d:
            if isinstance(key, types.FunctionType):
                return True
            if reduct_dict(d[key]):
                return True
    elif isinstance(d, types.FunctionType):
        return True
    return False



def case(a, b, snd, nnd, cnd):
    a = copy.deepcopy(a)
    a = reduct_dict(a)
    b = copy.deepcopy(b)
    b = reduct_dict(b)
    if b:
        if a:  # Continuous Effects
            return cnd
            #return cnd[0](cnd[1])
            pass
        else:  # Numeric Effects
            return nnd
            #return nnd[0](nnd[1])
    else:
        if a:  # Continuous Effects, but b is empty
            return cnd
        else:  # Symbolic Effects
            return snd
            #return snd[0](snd[1])


def contained(state, pre):  # TODO lambda function applicable
    for d in pre:
        numerics = d.split('_')
        if len(numerics) == 1:
            for key in pre[d]:
                if not getattr(state, d)[key] == pre[d][key]:
                    return False
        else:
            num_denom = False  # False if this is lower bound, True if upper bound
            if numerics[1] == 'u':
                num_denom = True
            for key in pre[d]:
                s = getattr(state, d)[key]
                if isinstance(s, types.FunctionType):
                    s = s(state.t['t'])
                if num_denom:
                    if not s <= pre[d][key]:
                        return False
                else:
                    if not s >= pre[d][key]:
                        return False
    return True
############################################################
# Commands to tell Pyhop what the operators and methods are
operators = {}
methods = {}
goals = []
numeric_values = set()


def declare_numeric(numeric_val):
    numeric_values.add(numeric_val)
    pass


def declare_goals(goal_list):
    for goal in goal_list:
        goals.append(goal)
    return


def declare_operators(*op_list):
    """
    Call this after defining the operators, to tell Pyhop what they are. 
    op_list must be a list of functions, not strings.
    """
    operators.update({op.__name__: op for op in op_list})
    return operators


def declare_methods(task_name, *method_list):
    """
    Call this once for each task, to tell Pyhop what the methods are.
    task_name must be a string.
    method_list must be a list of functions, not strings.
    """
    methods.update({task_name: list(method_list)})
    return methods[task_name]


############################################################
# Commands to find out what the operators and methods are
def print_operators(op_list=operators):
    """Print out the names of the operators"""
    print('OPERATORS:', ', '.join(op_list))


def print_methods(m_list=methods):
    """Print out a table of what the methods are for each task"""
    print('{:<14}{}'.format('TASK:', 'METHODS:'))
    for task in m_list:
        print('{:<14}'.format(task) + ', '.join([f.__name__ for f in m_list[task]]))


############################################################
# The actual planner
verticies = []
policy = Policy()


def reset():
    global verticies, Policy
    verticies = []
    policy = Policy()


def pyhop_t(state, tasks=goals, original_call=False):
    """
    Try to find a plan that accomplishes tasks in state. 
    If successful, return the plan. Otherwise return False.
    """

    if original_call:
        policy.verticies.append(state)
        policy.starting_state = state
    result = seek_plan(state, tasks)  # result holds True or False if planner succeeds or fails
    if original_call:
        return policy
    return result


def seek_plan(state, tasks):
    if tasks == list():
        return True
    task1 = tasks[0]
    if task1[0] in operators:
        operator = operators[task1[0]]
        op_return = operator(state, *task1[1:])
        if not op_return:
            return False
        effects, preconditions, probabilities = op_return
        first_effect = effects[0]
        action = Action(name=task1, state=state)
        policy.verticies.append(action)
        policy.add_edge(state, action)
        action.preconditions = preconditions
        if 't' in dir(state):
            action.t['t'] = state.t['t']
        g_preconditions = {}
        for key in preconditions:
            g_preconditions[key] = {}
            for val in preconditions[key]:
                g_preconditions[key][val] = {}
                g_preconditions[key][val][preconditions[key][val]] = 1
        action.g_preconditions = g_preconditions
        children = []
        for i in range(len(effects)):
            effect = effects[i]
            probability = probabilities[i]
            new_state = copy.copy(state)
            new_state.apply_effects(effect)
            found = False
            for old_state in policy.verticies:
                if old_state == new_state:
                    policy.add_edge(action, old_state)
                    children.append(old_state)
                    action.effects[old_state] = effect
                    action.eff_prob[old_state] = probability
                    found = True
                    break
            if not found:
                policy.verticies.append(new_state)
                if effect == first_effect:
                    solution = seek_plan(new_state, tasks[1:])
                    if solution is not False:
                        policy.add_edge(action, new_state)
                        children.append(new_state)
                        action.effects[new_state] = effect
                        action.eff_prob[new_state] = probability
                    else:
                        new_state._valid = False
                        policy.add_edge(action, new_state)
                        action.effects[new_state] = effect
                        action.eff_prob[new_state] = probability
                        children.append(new_state)
                else:
                    result = pyhop_t(new_state, goals)
                    if result:
                        policy.add_edge(action, new_state)
                        children.append(new_state)
                        action.effects[new_state] = effect
                        action.eff_prob[new_state] = probability
                    else:
                        new_state._valid = False
                        policy.add_edge(action, new_state)
                        action.effects[new_state] = effect
                        action.eff_prob[new_state] = probability
                        children.append(new_state)
        action.children = children
        return True

    if task1[0] in methods:
        relevant = methods[task1[0]]
        for method in relevant:
            sub_tasks = method(state, *task1[1:])
            if sub_tasks is not False:
                solution = seek_plan(state, sub_tasks+tasks[1:])
                if solution is not False:
                    return True
    return False
