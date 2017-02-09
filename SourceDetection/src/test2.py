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
a = nx.adjacency_matrix(d.graph)  # adjacent matrix
aa = nx.adjacency_matrix(d.graph, weight=None)  # adjacent matrix

weights = nx.get_edge_attributes(d.graph, 'weight')

c = np.ones([5,5])
print a.todense(out=c)
c = np.ones([5,5])
print c
print np.multiply(a.todense(),c)
print d.graph.nodes()
print d.node2index
print weights
print aa.todense()

ps0 = np.random.rand(5)
print ps0
print np.tile(ps0, 5).reshape(5,5).T
print nx.diameter(d.graph)
x =  np.tile(ps0, 5).reshape(5,5).T
x[1] = 0
print x
print np.arange(1,10)
a = {}
a[1] = np.asarray([1,2,3])
a[2] = np.ones(3)
a[3] = np.zeros(3)
print sum(np.asarray(a.values())[:,2])