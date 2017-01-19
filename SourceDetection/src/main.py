"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/9.
"""

# coding=utf-8

import networkx as nx

import data
import distance_center as dc
import dynamic_importance as di
import dynamic_message_passing as dmp
import jordan_center as jc
import reverse_infection as ri
import rumor_center as rc
import map_gsba as gsba

d = data.Graph("../data/test.txt")
weight = nx.get_edge_attributes(d.graph, 'weight')
print weight
methods = [rc.RumorCenter(d.graph), di.DynamicImportance(d.graph), dc.DistanceCenter(d.graph),
           jc.JordanCenter(d.graph), ri.ReverseInfection(d.graph), dmp.DynamicMessagePassing(d.graph), gsba.GSBA(d.graph)]
for m in methods:
    result = m.detect()
    print result, m.method_name
    if len(result)>0:
        print result[0][0], result[0][1]
