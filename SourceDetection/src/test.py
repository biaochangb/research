import random
from decimal import *

import networkx as nx
import numpy as np
import numpy.linalg
import scipy.sparse.linalg
import scipy.sparse.linalg.eigen

import data
import rumor_center

Decimal('0.142857')
d = data.Graph("../data/test.txt")
# nx.draw(d.subgraph)
# plt.show()
a = {e: random.random() for e in d.graph.edges_iter()}
nx.set_edge_attributes(d.graph, 'weight', a)
print d.graph.edges(), d.graph.nodes()[0], d.graph.nodes()
print nx.edge_betweenness_centrality(d.graph)
print a
weight = nx.get_edge_attributes(d.graph, 'weight')
print weight
print d.graph.nodes(), d.graph['1']['2']['weight']

print nx.bfs_tree(d.graph, '1').edges()
children = nx.all_neighbors(nx.bfs_tree(d.graph, '1'), '2')
for c in children:
    if c not in ('1'):
        print c
nx.set_node_attributes(d.graph, 'number', {'2': Decimal(1)})
print nx.get_node_attributes(d.graph, 'number')
print weight
print sorted(weight, key=weight.get, reverse=True)
rc = rumor_center.RumorCenter(d.graph)
print rc.detect()

eigenvalues = nx.adjacency_spectrum(d.graph, weight='weight')
eigenvalues_new = scipy.sparse.linalg.eigs(nx.adjacency_matrix(d.graph, weight='weight'), k=3)
print eigenvalues
print eigenvalues_new

eigenvalues = numpy.linalg.eigvals(nx.adjacency_matrix(d.graph, weight='weight').toarray())
print eigenvalues, max(eigenvalues)

arr = np.array([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])
print np.delete(arr, 0, 0)
print np.delete(arr, 0, 1)
weight = nx.get_edge_attributes(d.graph, 'weight')
print weight
nx.set_edge_attributes(d.graph, 'weight', {})
weight = nx.get_edge_attributes(d.graph, 'weight')
print weight


print len(nx.nodes(d.graph))
