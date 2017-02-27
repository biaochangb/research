"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/9.
"""

# coding=utf-8

import pickle
import random
from time import clock

import networkx as nx
import numpy as np

import data as mydata
import distance_center as dc
import dmp2
import dynamic_importance as di
import dynamic_message_passing as dmp
import jordan_center as jc
import map_gsba as gsba
import reverse_infection as ri
import rumor_center as rc


class Experiment:
    precision = {}  # Detection Rate
    error = {}  # Detection Error
    topological_error = {}  # Detection topological Error
    ranking = {}  # Normalized Ranking
    running_time = {}
    methods = []

    def initialize_evaluation_measures(self, test_category):
        self.precision[test_category] = {}
        self.error[test_category] = {}
        self.topological_error[test_category] = {}
        self.ranking[test_category] = {}
        self.running_time[test_category] = {}
        for m in self.methods:
            self.precision[test_category][m.method_name] = list()
            self.error[test_category][m.method_name] = list()
            self.topological_error[test_category][m.method_name] = list()
            self.ranking[test_category][m.method_name] = list()

    def detection_test(self, network, test_category, infected_size, test_num=1):
        """Full test: each node is selected to be the source
            Random test: randomly select a node as the infection source
        """
        """Read the network and generate source nodes according to the test category"""
        d = mydata.Graph("../data/%s" % network, weighted=1)
        nodes = d.graph.nodes()
        n = d.graph.number_of_nodes()
        sources = list()  # source nodes' index
        self.initialize_evaluation_measures(test_category)
        if test_category == 'random_test':
            v = 0
            while v < test_num:
                sources.append(random.randint(0, n - 1))
                v += 1
        else:
            sources = np.arange(0, n)
        n = len(sources)

        """run the test"""
        print test_category, len(nodes), d.graph.number_of_edges(), infected_size, test_num
        for m in self.methods:
            print '\t', m.method_name
            start_time = clock()
            percentage = 0.2
            i = 0
            for s in sources:
                i += 1
                if abs(i - n * percentage) < 1:
                    print '\t\t percentage: ', percentage
                    percentage += 0.2
                file = "../data/simulation/%s.i%s.s%s.subgraph" % (network, infected_size, s)
                reader = open(file, "r")
                data = pickle.load(reader)
                """@type data: mydata.Graph"""
                reader.close()
                data.weights = d.weights
                m.set_data(data)
                result = m.detect()
                """evaluate the result"""
                if len(result) > 0:
                    if result[0][0] == nodes[s]:
                        self.precision[test_category][m.method_name].append(1)
                    else:
                        self.precision[test_category][m.method_name].append(0)
                    self.error[test_category][m.method_name].append(
                        nx.dijkstra_path_length(d.subgraph, result[0][0], nodes[s], weight='weight'))
                    self.topological_error[test_category][m.method_name].append(
                        nx.dijkstra_path_length(d.subgraph, result[0][0], nodes[s], weight=None))
                    r = 0
                    for u in result:
                        r += 1
                        if u[0] == nodes[s]:
                            self.ranking[test_category][m.method_name].append(r)
                            break
            end_time = clock()
            self.running_time[test_category][m.method_name] = end_time - start_time

    def print_result(self, test_category):
        for m in self.methods:
            l = len(self.precision[test_category][m.method_name]) + 1.0
            print sum(self.precision[test_category][m.method_name]) / l, sum(
                self.error[test_category][m.method_name]) / l, sum(
                self.topological_error[test_category][m.method_name]) / l, sum(
                self.ranking[test_category][m.method_name]) / l, self.running_time[test_category][
                m.method_name], m.method_name


if __name__ == '__main__':
    experiment = Experiment()
    print "Starting..."

    prior_detector1 = rc.RumorCenter()
    prior_detector2 = dmp2.DynamicMessagePassing()
    prior_detector3 = dc.DistanceCenter()
    prior_detector4 = jc.JordanCenter()
    prior_detector5 = ri.ReverseInfection()
    methods = [rc.RumorCenter(), di.DynamicImportance(), dc.DistanceCenter(),
               jc.JordanCenter(), ri.ReverseInfection(), dmp.DynamicMessagePassing(), gsba.GSBA(prior_detector1)]
    methods = [rc.RumorCenter(), di.DynamicImportance(), dc.DistanceCenter(),
               jc.JordanCenter(), ri.ReverseInfection(), dmp2.DynamicMessagePassing(), gsba.GSBA(prior_detector1)]
    methods = [rc.RumorCenter(), dc.DistanceCenter(), jc.JordanCenter(), ri.ReverseInfection(),
               gsba.GSBA(prior_detector1),gsba.GSBA(prior_detector2), gsba.GSBA(prior_detector3),
               gsba.GSBA(prior_detector4), gsba.GSBA(prior_detector5),dmp2.DynamicMessagePassing()]
    #methods = [ gsba.GSBA(prior_detector3)]
    experiment.methods = methods

    random_num = 10
    infected_size = 30
    networks = {'sw.v100e500': 'small-world.ws.v100.e500.gml', 'power-grid':'power-grid.gml'}
    net = 'sw.v100e500'
    test_category = 'random_test'
    initialize_time = clock()
    experiment.detection_test(networks[net], test_category, infected_size, test_num=random_num)
    test_time = clock()
    experiment.print_result(test_category)
    print "Runing time:", (test_time - initialize_time)

    # test_category = 'full_test'
    # initialize_time = clock()
    # experiment.detection_test(networks[net], test_category, infected_size, test_num=random_num)
    # test_time = clock()
    # experiment.print_result(test_category)
    # print "Runing time:", (test_time - initialize_time)
