# coding=utf-8
"""
A part of Source Detection.
Author: Biao Chang, changb110@gmail.com, from University of Science and Technology of China
created at 2017/1/9.
"""

import logging
import pickle
import random
from time import clock

import networkx as nx
import numpy as np

import data as mydata


class Experiment:
    """Conduct experiments with simulations about information propagation under two test_category categories:
    Full test_category: each node is selected to be the source.
    Random test_category: randomly select a node as the infection source.
    """
    precision = {}  # Detection Rate
    error = {}  # Detection Error
    topological_error = {}  # Detection topological Error
    ranking = {}  # Normalized Ranking
    methods = []
    running_time = {}
    propagation_model = 'IC'
    logger = logging.getLogger()
    RANDOM_TEST = 'random test'
    FULL_TEST = 'full test'

    def __init__(self, methods, logger):
        self.methods = methods
        self.logger = logger

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
            self.running_time[test_category][m.method_name] = list()


    def start(self, d, test_category, test_num, start,end,step):
        """
        start the experiment
        Args:
            d: mydata.Graph
            test_category: {'full test', 'random test'}
            test_num: the number of random test times
            start: the minimal number of infected nodes
            end: the maximal number of infected nodes
            step: the increasing step
        """
        self.logger.info(test_category)
        for infected_size in np.arange(start, end, step):
            self.initialize_evaluation_measures(test_category)
            s_time = clock()
            self.detect_generated(d, test_category, test_num, infected_size)
            e_time = clock()
            print "Running time:", e_time - s_time
            # self.logger.info(("Running time:", e_time - s_time))
            self.print_result(test_category)
            print '\n'
            self.logger.info('\n')

    def detect_generated(self, data, test_category, test_num=1, infected_size=None):
        """
        do random (or full) test with real-time generated simulations about information propagation.
        Args:
            data: mydata.Graph
            test_category: {'full_test', 'random_test'}
            test_num:   int
            infected_size: int
        """
        nodes = data.graph.nodes()
        n = len(nodes)
        sources = list()  # source nodes' index
        if test_category is self.RANDOM_TEST:
            """randomly select the sources"""
            v = 0
            while v < test_num:
                sources.append(nodes[random.randint(0, n - 1)])
                v += 1
        else:
            sources = nodes
        n_i = len(sources)
        print test_category, len(sources), infected_size
        self.logger.info((test_category, len(sources), infected_size))
        i = 0
        p = 0.1
        for s in sources:
            i += 1
            if abs(i - n_i * p) < 1:
                print '\t percentage: ', p
                p += 0.1
            if self.propagation_model is 'IC':
                infected = data.infect_from_source_IC(s, infected_size=infected_size)
            elif self.propagation_model is 'SI':
                infected = data.infect_from_source_SI(s, infected_size=infected_size)
            if infected_size is not None and len(infected)<infected_size-1:
                continue
            for m in self.methods:
                m.set_data(data)
                start_time = clock()
                result = m.detect()
                end_time = clock()
                self.running_time[test_category][m.method_name].append(end_time - start_time)
                """evaluate the result"""
                if len(result) > 0:
                    if result[0][0] == s:
                        self.precision[test_category][m.method_name].append(1)
                    else:
                        self.precision[test_category][m.method_name].append(0)
                    self.error[test_category][m.method_name].append(
                        nx.dijkstra_path_length(data.subgraph, result[0][0], s, weight='weight'))
                    self.topological_error[test_category][m.method_name].append(
                        nx.dijkstra_path_length(data.subgraph, result[0][0], s, weight=None))
                    r = 0
                    for u in result:
                        r += 1
                        if u[0] == s:
                            self.ranking[test_category][m.method_name].append(r * 1.0 / len(result))
                            break

    def detect_loaded(self, network, test_category, infected_size, test_num=1):
        """
        do random (or full) test with loaded simulations about information propagation.
        Args:
            data: mydata.Graph
            test_category: {'full_test', 'random_test'}
            test_num:   int
            infected_size: int
        """
        """Read the network and generate source nodes according to the test_category category"""
        d = mydata.Graph("../data/%s" % network, weighted=1)
        nodes = d.graph.nodes()
        n = d.graph.number_of_nodes()
        sources = list()  # source nodes' index
        self.initialize_evaluation_measures(test_category)
        if test_category is self.RANDOM_TEST:
            v = 0
            while v < test_num:
                sources.append(random.randint(0, n - 1))
                v += 1
        else:
            sources = np.arange(0, n)
        n = len(sources)

        """run the test_category"""
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
                            self.ranking[test_category][m.method_name].append(r * 1.0 / len(result))
                            break
            end_time = clock()
            self.running_time[test_category][m.method_name] = end_time - start_time

    def print_result(self, test):
        self.logger.info(self.precision)
        self.logger.info(self.error)
        self.logger.info(self.topological_error)
        self.logger.info(self.ranking)
        self.logger.info(self.running_time)
        for m in self.methods:
            l = len(self.precision[test][m.method_name]) * 1.0
            if l == 0: continue
            r = sum(self.precision[test][m.method_name]) / l, sum(self.error[test][m.method_name]) / l, sum(
                self.topological_error[test][m.method_name]) / l, sum(
                self.ranking[test][m.method_name]) / l,sum(self.running_time[test][m.method_name])/l, m.method_name, l
            print "%.4f\t%.4f\t%.4f\t%.4f\t%.5f\t%s\t%d"%r
            self.logger.info(r)
