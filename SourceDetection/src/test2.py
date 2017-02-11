"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/2/9.
"""

# coding=utf-8

import numpy as np
import networkx as nx
import scipy as sp

import data


a = np.random.rand(2,2)
b = np.random.rand(2,2)
print a*b, a[0,0], np.ones([5,5])
a = np.mat(a)
b = np.mat(b)
print a, b
print a*b
print a[0,0]*b[0,0]+a[0,1]*b[1,0]
print np.log(a).diagonal()

d = data.Graph("../data/test.txt", weighted=1)
a = nx.adjacency_matrix(d.graph).todense()  # adjacent matrix
aa = nx.adjacency_matrix(d.graph, weight=None).todense()  # adjacent matrix

mu = np.zeros(d.graph.number_of_nodes())  # recover probability
d = np.ones([5,5])
print a
print aa
print np.dot(a,aa)
print d[0], a.diagonal()

print np.tile(1,5)

x = np.asarray([[1,2],[3,4]])
y = np.asarray([[2.0,2.0],[2.0,2.0]])
print x[0][0], x[0,1]