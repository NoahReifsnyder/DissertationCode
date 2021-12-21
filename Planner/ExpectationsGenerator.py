# Takes in a graph from pyhop, performs necessary calculations to add expectations.
import copy
from queue import *
from Planner.pyhop import Action, case
from Planner.InverseFunc import inversefunc

class Expectations(object):
    def __init__(self):
        self.informed = {}
        self.immediate = {}
        self.regression = {}
        self.goldilocks = {}

    def __str__(self):
        retval = ''
        for exp in vars(self):
            retval += str(exp) + ': ' + str(getattr(self, exp)) + '\n'
        return retval

    def print(self):
        for exp in vars(self):
            print(exp, getattr(self, exp))


def o_plus(a={}, b={}, t_p=None, s={}):
    a = copy.deepcopy(a)
    b = copy.deepcopy(b)
    s = copy.deepcopy(s)
    t_p = copy.deepcopy(t_p)
    new_dict = {}
    keys_1 = [x for x in a if x in b]  # Case 1/2/3, break down in section
    keys_2 = [x for x in a if x not in b]  # Case 2
    keys_3 = [x for x in b if x not in a]  # Case 3
    for x in keys_1:
        new_dict[x] = {}
        keys_1_1 = [y for y in a[x] if y in b[x]]  # Case 1
        keys_1_2 = [y for y in a[x] if y not in b[x]]  # Case 2
        keys_1_3 = [y for y in b[x] if y not in a[x]]  # Case 3
        for y in keys_1_1:
            a_t = a[x][y]
            b_t = b[x][y]
            snd = lambda z: z
            nnd = lambda z: b_t(z)
            cnd = lambda z: lambda t: (z(t) + b_t(t - t_p))
            new_dict[x][y] = case(a_t, b_t, snd, nnd, cnd)(a_t)
        for y in keys_1_2:
            new_dict[x][y] = a[x][y]
        for y in keys_1_3:
            s_t = None
            if s:
                s_t = getattr(s, x)[y]
            b_t = b[x][y]
            snd = lambda z: b_t
            nnd = lambda z: b_t(z)
            cnd = lambda z: lambda t: (z(t) + b_t(t - t_p))
            if s:
                new_dict[x][y] = case(s_t, b[x][y], snd, nnd, cnd)(s_t)
            else:
                new_dict[x][y] = case(s, b[x][y], snd, nnd, cnd)(s)
    for x in keys_2:
        new_dict[x] = a[x]
    for x in keys_3:
        new_dict[x] = {}
        for y in b[x]:
            snd = lambda z: b[x][y]
            nnd = lambda z: b[x][y](z)
            cnd = lambda z: lambda t: (z(t) + b[x][y](t - t_p))
            if s:
                new_dict[x][y] = case(getattr(s, x)[y], b[x][y], snd, nnd, cnd)(getattr(s, x)[y])
            else:
                new_dict[x][y] = case(s, b[x][y], snd, nnd, cnd)(s)
    return new_dict


def o_minus(a={}, b={}, p={}, t_p=None):
    a = copy.deepcopy(a)
    b = copy.deepcopy(b)
    p = copy.deepcopy(p)
    t_p = copy.deepcopy(t_p)
    new_dict = {}
    keys_1 = [x for x in a if x in b and x not in p]  # Case 1/2/3, break down in section
    keys_2 = [x for x in a if x not in b and x not in p]  # Case 2
    keys_3 = [x for x in p]  # Case 3
    for x in keys_1:
        new_dict[x] = {}
        keys_1_1 = [y for y in a[x] if y in b[x] and y not in p]  # Case 1
        keys_1_2 = [y for y in a[x] if y not in b[x] and y not in p]  # Case 2
        keys_1_3 = []
        if x in p:
            keys_1_3 = [y for y in p[x]]  #Case 3
        for y in keys_1_1:
            if isinstance(a[x][y], dict):
                a_t = copy.deepcopy(a[x][y])
                snd = lambda z: {}
                nnd = lambda z: {inversefunc(z)(k).item(): a_t[k] for k in a_t}
                cnd = lambda z: {lambda t: k(t) - z(t - t_p): a_t[k] for k in a_t}
            else:
                snd = lambda z: {}
                nnd = lambda z: inversefunc(z)(a[x][y])
                cnd = lambda z: lambda t: (a[x][y](t) - z(t - t_p))
            new_dict[x][y] = case(a[x][y], b[x][y], snd, nnd, cnd)(b[x][y])
        for y in keys_1_2:
            new_dict[x][y] = a[x][y]
        for y in keys_1_3:
            snd = p[x][y]
            nnd = p[x][y]
            cnd = lambda t: p[x][y]
            new_dict[x][y] = case(p[x][y], {}, snd, nnd, cnd)
    for x in keys_2:
        new_dict[x] = a[x]
    for x in keys_3:
        new_dict[x] = {}
        for y in p[x]:
            snd = p[x][y]
            nnd = p[x][y]
            cnd = lambda t: p[x][y]
            new_dict[x][y] = case(p[x][y], {}, snd, nnd, cnd)
    return new_dict




def o_divide(dict_a, k):
    new_dict = {}
    for key in dict_a:
        new_dict[key] = {}
        for val in dict_a[key]:
            new_dict[key][val] = {}
            for c in dict_a[key][val]:
                new_dict[key][val][c] = dict_a[key][val][c] / k
    return new_dict


def o_times(dict_a, dict_b):
    new_dict = {}
    all_keys = [x for x in dict_b] + [x for x in dict_a]
    all_keys = set(all_keys)
    for x in all_keys:
        new_dict[x] = {}
        if x in dict_b and x in dict_a:
            b_keys = [y for y in dict_b[x] if y not in dict_a[x]]
            a_keys = [y for y in dict_a[x] if y not in dict_b[x]]
            comb_keys = [y for y in dict_a[x] if y in dict_b[x]]
            for key in b_keys:
                new_dict[x][key] = dict_b[x][key]
            for key in a_keys:
                new_dict[x][key] = dict_a[x][key]
            for key in comb_keys:
                new_dict[x][key] = {}
                a_val = [y for y in dict_a[x][key] if y not in dict_b[x][key]]
                b_val = [y for y in dict_b[x][key] if y not in dict_a[x][key]]
                comb_val = [y for y in dict_a[x][key] if y in dict_b[x][key]]
                for val in a_val:
                    new_dict[x][key][val] = dict_a[x][key][val]
                for val in b_val:
                    new_dict[x][key][val] = dict_b[x][key][val]
                for val in comb_val:
                    new_dict[x][key][val] = dict_a[x][key][val] + dict_b[x][key][val]
        elif x in dict_b:
            for key in dict_b[x]:
                new_dict[x][key] = dict_b[x][key]
        elif x in dict_a:
            for key in dict_a[x]:
                new_dict[x][key] = dict_a[x][key]
    return new_dict



class Tau2:
    verticies = {}
    counter = 0

    class E:
        def __init__(self, edge):
            self.alpha = edge[0]
            self.alpha_p = edge[1]
            edge[0].children.add(edge[1])

    class V:
        def __init__(self, node):
            if node not in Tau2.verticies:
                Tau2.verticies[node] = self
            else:
                original = Tau2.verticies[node].node
                if node.get_num() < 0:
                    if node.get_num() > original.get_num():
                        Tau2.verticies[node] = self
                else:
                    if node.get_num() < original.get_num():
                        Tau2.verticies[node] = self
            self.node = node
            self._num = Tau2.counter
            self.children = set()
            self.prob = {}
            Tau2.counter += 1
            self.expectations = Expectations()

        def __eq__(self, other):
            return hash(self) == hash(other)

        def __hash__(self):
            return self._num

    def __init__(self, graph, goal_set={}, verbose=False):
        self.graph = graph
        self.starting_state = graph.starting_state
        self.starting_vertex = None
        self.back_edges = {}
        self.terminal = set()
        self.verbose = verbose
        self.vs = []
        self.edges = {}
        self.goals = goal_set
        self.gen_self()
        print('be', len(self.back_edges))
        print('vs', len(self.vs))
        print('es', len(self.edges))
        print('max', len(self.edges) * 2)
        self.gen_regressed_expectations()
        print('reg')
        self.gen_immediate()
        print('imm')
        self.gen_informed()
        print('inf')
        self.gen_goldilocks()
        print('gold')
        self.set_expectation()

    def set_expectation(self):
        for key in self.verticies:
            key.expectations = Expectations()
            key.expectations.regression = self.verticies[key].expectations.regression
            key.expectations.informed = self.verticies[key].expectations.informed
            key.expectations.immediate = self.verticies[key].expectations.immediate
            key.expectations.goldilocks = self.verticies[key].expectations.goldilocks
            if self.verbose:
                print(key.get_num())
                print(key.expectations)

    def gen_immediate(self):
        queue = Queue()
        forward_only = [(edge.alpha, edge.alpha_p) for edge in self.edges.values() if edge not in self.back_edges]
        queue.put((self.starting_vertex, self.starting_vertex))
        action_type = Action()
        while not queue.empty():
            vertex, parent = queue.get()
            if type(vertex.node) == type(action_type):  # action, take from parent
                vertex.expectations.immediate = copy.deepcopy(parent.expectations.immediate)
            elif vertex == self.starting_vertex:  # starting state, no prev effects
                child = [x for x in self.graph.edges[vertex.node]][0]
                vertex.expectations.immediate = child.preconditions
            elif vertex in self.terminal:
                vertex.expectations.immediate = parent.node.effects[vertex.node]
            else:  # state != s0
                child = [x for x in self.graph.edges[vertex.node]][0]
                a = child.preconditions
                b = parent.node.effects[vertex.node]
                snd = lambda s: o_plus(a=a, b=b)
                nnd = lambda s: o_plus(a=a, s=s.node, b=b)
                cnd = lambda s: o_plus(a=a, s=s.node, t_p=s.node.t['t'], b=b)
                vertex.expectations.immediate = case(vertex.node, b, snd, nnd, cnd)(vertex)
            children = [x for (y, x) in forward_only if y == vertex]
            for child in children:
                queue.put((child, vertex))

    def gen_informed(self):
        forward_only = [(edge.alpha, edge.alpha_p) for edge in self.edges.values() if edge not in self.back_edges]
        queue = Queue()
        queue.put((self.starting_vertex, self.starting_vertex))
        action_type = Action()
        while not queue.empty():
            vertex, parent = queue.get()
            parent_expectations = parent.expectations.informed
            if type(vertex.node) == type(action_type):  # vertex=an Action
                vertex.expectations.informed = copy.deepcopy(parent_expectations)
                pass  # don't change parent_expectations, pass on to grandchildren of preceding state
            elif vertex == self.starting_vertex:
                pass  # starting state, null informed
            elif vertex:  # vertex != s_0 and is a state
                a = copy.deepcopy(parent_expectations)
                b = parent.node.effects[vertex.node]
                snd = lambda s: o_plus(a=a, b=b)
                nnd = lambda s: o_plus(a=a, s=s.node, b=b)
                cnd = lambda s: o_plus(a=a, s=s.node, t_p=s.node.t['t'], b=b)
                vertex.expectations.informed = case(vertex.node, b, snd, nnd, cnd)(vertex)
                pass
            children = [x for (y, x) in forward_only if y == vertex]
            for child in children:
                queue.put((child, vertex))

    def gen_regressed_expectations(self, goldilocks=False):
        exp_type = "regression"
        if goldilocks:
            exp_type = "goldilocks"
        q = Queue()
        count = 0
        finished = {}
        handled = set()
        prep = True
        for vertex in self.terminal:
            finished[vertex] = set()
            exp = copy.deepcopy(self.goals)
            if vertex.node.is_valid() and goldilocks:
                for d in vertex.expectations.informed:
                    exp[d] = {}
                    for key in vertex.expectations.informed[d]:
                        exp[d][key] = {vertex.expectations.informed[d][key]: 1}
            elif not vertex.node.is_valid():
                exp = {None: {None: {None: 1}}}
            setattr(vertex.expectations, exp_type, exp)
            x = [(edge.alpha, vertex) for edge in self.edges.values() if edge.alpha_p == vertex]
            for edge in x:
                if edge[0] not in finished:
                    finished[edge[0]] = set()
                finished[edge[0]].add(edge[1])
                q.put(edge)
        for i in range(2):
            while not q.empty():
                count += 1
                alpha, alpha_p = q.get()
                if isinstance(alpha.node, type(self.starting_state)):  # alpha is a state, and state exp = action exp
                    setattr(alpha.expectations, exp_type, getattr(alpha_p.expectations, exp_type))
                    x = [edge for edge in self.edges.values() if edge.alpha_p == alpha]
                    if not prep:
                        x = [edge for edge in x if edge not in self.back_edges]
                    for edge in x:
                        edge = (edge.alpha, edge.alpha_p)
                        if edge[0] not in finished:
                            finished[edge[0]] = set()
                        finished[edge[0]].add(edge[1])
                        handled.add(edge)
                        q.put(edge)
                else:
                    if self.edges[(alpha, alpha_p)] in self.back_edges and prep:
                        g_s = (self.back_edges[self.edges[(alpha, alpha_p)]])
                        x = [edge.alpha for edge in self.back_edges if edge.alpha_p == alpha_p]
                        y = getattr(alpha_p.expectations, exp_type)
                        for node in x:
                            y = o_minus(y, node.node.g_preconditions)
                        z = o_divide(y, (1 - g_s))
                        a = o_minus(y, z)
                        setattr(alpha_p.expectations, exp_type, o_times(a, z))
                    x = [edge for edge in self.back_edges if edge.alpha == alpha]
                    for edge in x:
                        finished[edge.alpha].add(edge.alpha_p)
                        pass
                    if len(finished[alpha]) == len(alpha.children):
                        setattr(alpha.expectations, exp_type, {})
                        for child in alpha.children:
                            x = o_minus(a=getattr(child.expectations, exp_type), b=alpha.node.effects[alpha_p.node])
                            y = o_minus(a=x, b=alpha.node.g_preconditions)
                            z = o_divide(y, 1 / alpha.node.eff_prob[child.node])
                            setattr(alpha.expectations, exp_type, o_times(getattr(alpha.expectations, exp_type), z))
                        child = list(alpha.children)[0]
                        child_exp = getattr(child.expectations, exp_type)
                        snd = o_times(alpha.node.g_preconditions, getattr(alpha.expectations, exp_type))
                        nnd = o_minus(a=child_exp, p=alpha.node.g_preconditions, b=alpha.node.effects[child.node])
                        cnd = o_minus(a=child_exp, p=alpha.node.g_preconditions, t_p=alpha.node.t['t'], b=alpha.node.effects[child.node])
                        setattr(alpha.expectations, exp_type, case(child.node, alpha.node.effects[child.node], snd, nnd, cnd))
                        x = [edge for edge in self.edges.values() if edge.alpha_p == alpha]
                        # print([(v.alpha.node.get_num(), v.alpha_p.node.get_num()) for v in x])
                        if not prep:
                            x = [edge for edge in x if edge not in self.back_edges]
                        x = [(edge.alpha, edge.alpha_p) for edge in x if (edge.alpha, edge.alpha_p) not in handled]
                        for edge in x:
                            if edge[0] not in finished:
                                finished[edge[0]] = set()
                            finished[edge[0]].add(edge[1])
                            handled.add(edge)
                            q.put(edge)
            prep = False
            finished = {}
            handled = set()
            for vertex in self.terminal:
                finished[vertex] = set()
                x = [(edge.alpha, vertex) for edge in self.edges.values() if edge.alpha_p == vertex]
                for edge in x:
                    if edge[0] not in finished:
                        finished[edge[0]] = set()
                    finished[edge[0]].add(edge[1])
                    q.put(edge)
        print("count:", count)

    def gen_goldilocks(self):
        self.gen_regressed_expectations(goldilocks=True)

    def gen_self(self, alpha=None, edges={}, route=[]):
        if not alpha:
            alpha = self.V(self.starting_state)
            self.starting_vertex = alpha
            self.vs.append(alpha)
        if alpha.node not in self.graph.edges:
            self.terminal.add(alpha)
            return
        route.append(alpha)
        alpha_edges = [(alpha.node, alpha_p) for alpha_p in self.graph.edges[alpha.node] if alpha.node.get_num() not in
                       edges or alpha_p.get_num() not in edges[alpha.node.get_num()]]
        r_list = []
        for (a, a_p) in alpha_edges:
            if a_p in self.graph.edges and len([z for z in self.graph.edges[a_p] if
                                                a_p.get_num() in edges and z.get_num() in edges[a_p.get_num()]]) > 0:
                prob = 1
                last = None
                end_prob = None
                for node in [node.node for node in route] + [a_p]:
                    if not end_prob and node.get_num() == a_p.get_num():
                        end_prob = prob
                    if last and node.get_num() >= 0:
                        prob *= last.eff_prob[node]
                    last = node
                # r_list.append(alpha.node.eff_prob[a_p]*prob/end_prob)
                r_list.append(prob / end_prob)
                # self.back_edges[edges[a.get_num()][a_p.get_num()]] = prob  # TODO find prob of returning to node after backedge. Use for r in geometric series calc for expectation probability
            alpha_p = None
            for v in self.vs:
                if v.node.get_num() == a_p.get_num():
                    alpha_p = v
            if not alpha_p:
                alpha_p = self.V(a_p)
                self.vs.append(alpha_p)
            if (alpha, alpha_p) not in self.edges:
                edge = self.E((alpha, alpha_p))
                self.edges[(alpha, alpha_p)] = edge
            else:
                edge = self.edges[(alpha, alpha_p)]
            if a.get_num() not in edges:
                edges[a.get_num()] = {}
            if a_p.get_num() not in edges[a.get_num()]:
                edges[a.get_num()][a_p.get_num()] = edge
            # HERE
            prob = 1
            last = None
            for node in route:
                if last and node.node.get_num() >= 0:
                    prob *= last.prob[node]
                    pass
                last = node
            g_s = 0
            for r in r_list:
                g_s += r / (1 - r) * alpha.node.eff_prob[alpha_p.node]
            if alpha.node.get_num() < 0:
                alpha.prob[alpha_p] = g_s + alpha.node.eff_prob[alpha_p.node]
            else:
                alpha.prob[alpha_p] = 1
                # HERE
            if a_p in self.graph.edges and len([z for z in self.graph.edges[a_p] if
                                                a_p.get_num() in edges and z.get_num() in edges[a_p.get_num()]]) > 0:
                self.back_edges[edges[a.get_num()][a_p.get_num()]] = prob * alpha.node.eff_prob[alpha_p.node]
            self.gen_self(alpha_p, copy.copy(edges), copy.copy(route))
        return


    def extra(self, alpha, a, a_p, alpha_p, edges, route):
        if a_p in self.graph.edges and len([z for z in self.graph.edges[a_p] if
                                            a_p.get_num() in edges and z.get_num() in edges[a_p.get_num()]]) > 0:
            prob = 1
            last = None
            end_prob = None
            for node in route:
                if not end_prob and node.node.get_num() == alpha_p.node.get_num():
                    print('here')
                    end_prob = prob
                print(node.node.get_num())
                if last and node.node.get_num() >= 0:
                    prob *= last.node.eff_prob[node.node]
                    pass
                last = node
            print('here', prob, end_prob)
            self.back_edges[edges[a.get_num()][a_p.get_num()]] = alpha.node.eff_prob[
                                                                     alpha_p.node] * prob / end_prob  # TODO find prob of returning to node after backedge. Use for r in geometric series calc for expectation probability



class Vertex:
    def __init__(self, node, num):
        self.node = node
        self.num = num
        self.children = 0
        self.added = 0
        self.type = type(node)
        self.set = False
        self.expectations = Expectations()

    def __str__(self):
        return str(self.node) + "," + str(self.num)

    def finished(self):
        if self.children == self.added:
            return True
        else:
            return False


def print_exp(policy):
    for state in policy:
        state.expectations.print()
        print()


def gen_expectations(policy, goal_set={}, verbose=False):
    # graph = Graph(starting_state, policy)
    # graph.initialize_expectations()
    # graph.gen_immediate()
    # graph.gen_informed()
    tau = Tau2(policy, goal_set={}, verbose=verbose)
    # tau.gen_regressed_expectations('regression')
    # tau.gen_regressed_expectations('goldilocks')
    return
