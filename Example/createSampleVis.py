from igraph import *
import random

ROLE_PROB = .8
CONVERT_PROB = .4
GRAPH_SIZE = 30
CONNECTION_PROB = .3
color_dict = {1: 'red', 0: 'blue'}

g = Graph.GRG(GRAPH_SIZE, CONNECTION_PROB)
g.vs['role'] = [0] * GRAPH_SIZE

degreeCent = g.degree()
maxDegree = degreeCent.index(max(degreeCent))

curr = maxDegree
g.vs[curr]['role'] = 1
visited = [curr]
toVisit = g.neighbors(g.vs[curr])
while len(toVisit) > 0:
    curr = toVisit.pop()
    visited.append(curr)
    r = random.random()
    print r
    if r < ROLE_PROB:
        # If this is of the role type 1, then also look at the neighbors of this person
        g.vs[curr]['role'] = 1
        toVisit += [x for x in g.neighbors(g.vs[curr]) if x not in visited and x not in toVisit]
        print visited
        print toVisit

print(summary(g))
layout1 = g.layout('fr')
g.vs['color'] = [color_dict[x] for x in g.vs['role']]
plot(g, layout = layout1)

