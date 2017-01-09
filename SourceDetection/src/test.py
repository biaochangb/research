import networkx as nx
import matplotlib.pyplot as plt
from networkx.drawing.nx_pydot import write_dot
import data
import random
from decimal import *
import math
import rumor_centrality

Decimal('0.142857')
d = data.Graph("../data/test.txt")
# nx.draw(d.graph)
# plt.show()
a = {e:random.random() for e in d.graph.edges_iter()}
nx.set_edge_attributes(d.graph, 'weight', a)
print d.graph.edges(), d.graph.nodes()[0], d.graph.nodes()
print nx.edge_betweenness_centrality(d.graph)
print a
weight = nx.get_edge_attributes(d.graph, 'weight')
print weight
print d.graph.nodes(), d.graph['1']['2']['weight']

print nx.bfs_tree(d.graph, '1').edges()
children =  nx.all_neighbors(nx.bfs_tree(d.graph, '1'), '2')
for c in children:
    if c not in ('1'):
        print c
nx.set_node_attributes(d.graph, 'number', {'2':Decimal(1)})
print nx.get_node_attributes(d.graph, 'number')
print weight
print sorted(weight, key=weight.get, reverse=True)
rc =  rumor_centrality.RumorCentrality()
print rc.detect(d.graph)
# nx.draw(nx.bfs_tree(d.graph, '1'))
# plt.show()